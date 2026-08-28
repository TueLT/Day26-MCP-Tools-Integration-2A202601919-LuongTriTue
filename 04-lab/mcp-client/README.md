# Weather Agent - Google ADK with MCP Server

AI agent built with **Google Agent Development Kit (ADK)** that uses tools from a local **MCP server** via Streamable HTTP transport.

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────────┐
│   User Browser  │ ───> │  ADK Web UI      │ ───> │  Weather Agent      │
│   localhost:8000│      │  (Google ADK)    │      │  (Agent with MCP)   │
└─────────────────┘      └──────────────────┘      └─────────────────────┘
                                                             │
                                                             │ Streamable HTTP
                                                             ▼
                                                   ┌─────────────────────┐
                                                   │  MCP Server         │
                                                   │  localhost:8085/mcp │
                                                   │  FastMCP + Tools    │
                                                   └─────────────────────┘
                                                             │
                                                             ▼
                                                   ┌─────────────────────┐
                                                   │  WeatherAPI.com     │
                                                   └─────────────────────┘
```

## Features

- **Remote MCP Tools**: Connects to MCP server via Streamable HTTP
- **3 Weather Tools**:
  - `get_current_weather(city)` - Real-time weather conditions
  - `get_forecast(city, days)` - Weather forecast up to 3 days
  - `health_check()` - Server health verification
- **Web Interface**: UI via ADK web
- **Streaming Responses**: Real-time AI responses

## Quick Start

From the repository root on Windows PowerShell:

```powershell
# One-time setup
powershell -ExecutionPolicy Bypass -File .\setup.ps1 -IncludeLab

# Terminal 1 — MCP server
& .\04-lab\mcp-server\start_server.ps1

# Terminal 2 — ADK web UI
& .\04-lab\mcp-client\start_agent.ps1
```

Open http://localhost:8000 and select `weather_agent`.

The launchers read the root `.env`. `GEMINI_API_KEY` is required for the
agent. `WEATHERAPI_KEY` is required only for real weather/forecast calls;
`health_check` works without it.

For Bash/macOS, set `GOOGLE_API_KEY` and `WEATHERAPI_KEY`, then run the
server and `uv run adk web` from their respective directories.

## Project Structure

```
mcp-client/
├── weather_agent/
│   ├── agent.py           # Main agent with MCP connection
│   └── __init__.py
├── pyproject.toml
├── start_agent.ps1        # Windows launcher; loads root .env before ADK
└── README.md
```

## Configuration

### Agent Configuration

In `weather_agent/agent.py`:

```python
MCP_SERVER_URL = "http://127.0.0.1:8085/mcp"

connection_params = StreamableHTTPConnectionParams(
    url=MCP_SERVER_URL,
    timeout=30.0,
)

root_agent = Agent(
    name="weather_agent",
    model="gemini-2.5-flash",
    tools=[weather_tools],
)
```

## Troubleshooting

### Agent won't connect to MCP server

1. **404 errors**: MCP server is not running or wrong port
   - Ensure the MCP server is running on port 8085
   - Check `MCP_SERVER_URL` in `agent.py`

2. **405 errors**: Port conflict with another application
   - Windows: `netstat -ano | findstr :8085`
   - macOS/Linux: `lsof -i :8085`
   - Change port in both server and client if needed

3. **Timeout errors**: Server not started
   - Start the MCP server first, then the ADK client

## Environment Variables

Root `.env`:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
WEATHERAPI_KEY=your_weatherapi_key
```

## Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [WeatherAPI](https://www.weatherapi.com/)
