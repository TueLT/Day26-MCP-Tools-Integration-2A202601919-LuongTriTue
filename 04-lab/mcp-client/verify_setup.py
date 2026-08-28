#!/usr/bin/env python3
"""
Verification script for Weather Agent setup
Checks if all components are configured correctly
"""
import asyncio
import os
import sys
from pathlib import Path

CLIENT_DIR = Path(__file__).resolve().parent
ROOT_ENV = CLIENT_DIR.parents[1] / ".env"
EXPECTED_TOOLS = {"get_current_weather", "get_forecast", "health_check"}


def get_mcp_server_url() -> str:
    return os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8085/mcp")


def check_environment():
    """Check if .env file exists and is configured"""
    print("🔍 Checking environment configuration...")
    
    if not ROOT_ENV.exists():
        print(f"❌ .env file not found: {ROOT_ENV}")
        return False
    
    # Load the repository configuration without printing secret values.
    from dotenv import load_dotenv
    load_dotenv(ROOT_ENV, override=True)
    
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    weather_api_key = os.getenv("WEATHERAPI_KEY")
    if not api_key or api_key.startswith("your_"):
        print("❌ GEMINI_API_KEY/GOOGLE_API_KEY not configured in root .env")
        print("   Get key from: https://aistudio.google.com/apikey")
        return False
    if not weather_api_key or weather_api_key.startswith("your_"):
        print("❌ WEATHERAPI_KEY not configured in root .env")
        print("   Get key from: https://www.weatherapi.com/")
        return False

    print("✅ Gemini API key configured")
    print("✅ WeatherAPI key configured")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        ("google.adk", "Google ADK"),
        ("google.genai", "Google Gen AI SDK"),
        ("mcp", "MCP"),
        ("fastmcp", "FastMCP"),
        ("dotenv", "python-dotenv"),
        ("httpx", "httpx"),
    ]
    
    all_installed = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} not installed")
            all_installed = False
    
    if not all_installed:
        print("\n   Install with: uv sync")
        print("   Or: pip install google-adk google-genai mcp fastmcp python-dotenv httpx")
    
    return all_installed

def check_agent_structure():
    """Check if agent directory structure is correct"""
    print("\n🔍 Checking agent structure...")
    
    required_files = [
        "weather_agent/agent.py",
        "weather_agent/__init__.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = CLIENT_DIR / file_path
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} not found")
            all_exist = False
    
    return all_exist

def check_mcp_server():
    """Complete an MCP handshake, discover tools, and call live tools."""
    print("\n🔍 Checking MCP server and tool discovery...")
    server_url = get_mcp_server_url()

    try:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        async def test_connection():
            async with streamable_http_client(server_url) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    response = await session.list_tools()
                    tool_names = {tool.name for tool in response.tools}
                    missing = EXPECTED_TOOLS - tool_names
                    if missing:
                        raise RuntimeError(f"Missing MCP tools: {', '.join(sorted(missing))}")

                    health = await session.call_tool("health_check", {})
                    if health.isError or not health.content:
                        raise RuntimeError("health_check failed")

                    current = await session.call_tool(
                        "get_current_weather", {"city": "Hanoi"}
                    )
                    if current.isError or not current.content:
                        raise RuntimeError("get_current_weather failed")
                    weather_text = current.content[0].text
                    error_markers = ("not configured", "Unable to fetch")
                    if any(marker in weather_text for marker in error_markers):
                        raise RuntimeError(weather_text)

                    forecast = await session.call_tool(
                        "get_forecast", {"city": "Hanoi", "days": 1}
                    )
                    if forecast.isError or not forecast.content:
                        raise RuntimeError("get_forecast failed")
                    forecast_text = forecast.content[0].text
                    if any(marker in forecast_text for marker in error_markers):
                        raise RuntimeError(forecast_text)

        asyncio.run(test_connection())
        print(f"✅ MCP handshake succeeded at {server_url}")
        print(f"✅ Discovered tools: {', '.join(sorted(EXPECTED_TOOLS))}")
        print("✅ health_check succeeded")
        print("✅ get_current_weather reached WeatherAPI successfully")
        print("✅ get_forecast reached WeatherAPI successfully")
        return True
    except Exception as e:
        print(f"❌ MCP/WeatherAPI verification failed: {e}")
        return False

def check_agent_import():
    """Try to import the agent"""
    print("\n🔍 Checking agent import...")
    
    try:
        # Suppress warnings during import
        import warnings
        warnings.filterwarnings("ignore")
        
        from weather_agent import root_agent
        print(f"✅ Agent imported successfully: {root_agent.name}")
        print(f"   Model: {root_agent.model}")
        return True
    except Exception as e:
        print(f"❌ Failed to import agent: {e}")
        return False

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("Weather Agent Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        check_environment(),
        check_dependencies(),
        check_agent_structure(),
        check_mcp_server(),
        check_agent_import(),
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ All checks passed!")
        print("\n🚀 Ready to start!")
        print(r"   Run: .\start_agent.ps1")
        print("\n📍 Then open: http://localhost:8000")
        return 0
    else:
        print("❌ Some checks failed")
        print("\n⚠️  Fix the issues above and run this script again")
        return 1

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())

