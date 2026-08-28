"""Weather Agent that connects to an MCP server over Streamable HTTP."""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Dùng chung Gemini key trong .env ở thư mục gốc của repo.
repo_env = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(repo_env, override=True)
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    # ADK đọc GOOGLE_API_KEY; key trong repo phải ưu tiên hơn key cũ của máy.
    os.environ["GOOGLE_API_KEY"] = gemini_api_key

# Phải import ADK sau khi nạp key vì SDK khởi tạo cấu hình model lúc import.
from google.adk import Agent  # noqa: E402
from google.adk.tools.mcp_tool.mcp_toolset import (  # noqa: E402
    McpToolset,
    StreamableHTTPConnectionParams,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8085/mcp")

logger.info("Initializing weather agent with remote MCP server")
logger.info("MCP Server: %s", MCP_SERVER_URL)

# The connection is opened lazily when ADK first uses the toolset.
connection_params = StreamableHTTPConnectionParams(
    url=MCP_SERVER_URL,
    timeout=30.0,
)

logger.info("Configuring MCP toolset...")
weather_tools = McpToolset(connection_params=connection_params)

root_agent = Agent(
    name="weather_agent",
    model="gemini-2.5-flash",
    description="Answers weather questions using tools from the MCP weather server.",
    instruction=(
        "Use the MCP weather tools for weather, forecast, and server-health questions. "
        "Do not invent weather data when a tool reports an error."
    ),
    tools=[weather_tools],
)

logger.info("Weather agent initialized with MCP tools:")
logger.info("   - get_current_weather(city)")
logger.info("   - get_forecast(city, days)")
logger.info("   - health_check()")

