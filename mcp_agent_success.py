import asyncio, json, os
from contextlib import AsyncExitStack
from fastmcp import Client
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def make_function_list(registry):
    return [
        {
            "name": full_name,
            "description": desc,
            "parameters": schema
        }
        for full_name, (_, _, schema, desc) in registry.items()
    ]

async def main():
    # ---- 1) 打开所有 MCP Client 的生命周期 ----
    async with AsyncExitStack() as stack:
        # 1a) 读配置文件
        with open("mcp_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

        # 1b) 针对每个 server 建 Client 并保持 online
        registry: dict[str, tuple[Client, str, dict, str]] = {}
        for srv_name, srv_cfg in config.items():
            client = Client({"mcpServers": {srv_name: srv_cfg}})
            await stack.enter_async_context(client)
            tools = await client.list_tools()
            for tool in tools:
                raw = tool.name
                full = f"{srv_name}_{raw}"
                registry[full] = (
                    client,
                    raw,
                    tool.inputSchema,
                    tool.description or ""
                )

        # 1c) 打印可用工具，确认没问题
        print("Agent 可用工具：")
        for name in sorted(registry):
            print("  -", name)

        # ---- 2) 在同一个 context 里启动对话 ----
        messages = []
        while True:
            user_msg = input("User> ")
            if user_msg.lower() in ("exit", "quit"):
                break

            messages.append({"role": "user", "content": user_msg})
            functions = make_function_list(registry)

            # 2a) LLM 决定要不要调用函数
            resp1 = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                functions=functions,
                function_call="auto"
            )
            msg = resp1.choices[0].message

            # 2b) 如果要调函数
            if msg.function_call:
                func_name = msg.function_call.name
                args = json.loads(msg.function_call.arguments)

                # 记入“调用”这一步
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": func_name,
                        "arguments": msg.function_call.arguments
                    }
                })

                client, raw_name, _, _ = registry[func_name]
                results = await client.call_tool(raw_name, args)
                output = json.dumps([r.text for r in results], ensure_ascii=False)

                # 记入“函数返回”
                messages.append({
                    "role": "function",
                    "name": func_name,
                    "content": output
                })
                # 2c) 再次让模型回答
                resp2 = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )
                reply = resp2.choices[0].message.content
                messages.append({"role": "assistant", "content": reply})
                print("Assistant>", reply)

            else:
                # 2d) 直接回答
                reply = msg.content
                messages.append({"role": "assistant", "content": reply})
                print("Assistant>", reply)

    # AsyncExitStack 出栈后，所有 Client 一次性 clean up

if __name__ == "__main__":
    asyncio.run(main())