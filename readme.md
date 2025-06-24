# Project Overview

This project provides an example intelligent agent built on the MCP (Model Collaboration Platform) framework. Use `mcp_agent_success.py` to start the service and manage MCP tools via `config.json`.

## Prerequisites

- Python 3.10 or above
- A virtual environment is recommended

## Install Dependencies

```bash
# Navigate to the project root
cd /path/to/your/project

# (Optional) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Use `config.json` to manage the list of MCP tools and related parameters. Example:

```json
{
  "mcps": [
    {
      "name": "mcp_browser",
      "module": "mcp.browser",
      "endpoint": "http://localhost:8000/browser"
    },
    {
      "name": "mcp_file",
      "module": "mcp.file",
      "endpoint": "http://localhost:8000/file"
    }
  ],
  "default_timeout": 30
}
```

### Adding a New MCP

1. Open `config.json`.
2. Add a new entry to the `mcps` array with the following fields:
   - `name`: Unique identifier for the MCP.
   - `module`: Python module path for loading the MCP tool.
   - `endpoint`: Service endpoint URL for the MCP.

Example:

```json
{
  "name": "mcp_newtool",
  "module": "mcp.newtool",
  "endpoint": "http://localhost:8000/newtool"
}
```

## Usage

Run the agent script from the project root:

```bash
python ./mcp_agent_success.py
```

The script will load `config.json`, register all MCP tools, and start the service.

## Troubleshooting

- **How to debug a newly added MCP?**
  - Verify the module path is correct.
  - Ensure the endpoint is reachable.
  - Check the logs for loading or invocation errors.

## Contact

For questions or suggestions, please contact the project maintainer.

