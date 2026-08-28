"""Unit tests for the Lab 04 MCP weather tools."""

import asyncio
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

SERVER_FILE = Path(__file__).parent / "mcp-server" / "weather.py"
SPEC = importlib.util.spec_from_file_location("lab_weather", SERVER_FILE)
weather = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(weather)


class WeatherToolTests(unittest.TestCase):
    def test_health_check(self):
        result = asyncio.run(weather.health_check())
        self.assertIn("running", result)

    def test_current_weather_formats_api_response(self):
        payload = {
            "location": {"name": "Hanoi", "region": "", "country": "Vietnam"},
            "current": {
                "temp_c": 30,
                "temp_f": 86,
                "feelslike_c": 35,
                "feelslike_f": 95,
                "condition": {"text": "Sunny"},
                "humidity": 70,
                "wind_kph": 10,
                "wind_mph": 6.2,
                "wind_dir": "S",
                "pressure_mb": 1000,
                "uv": 5,
                "vis_km": 10,
                "last_updated": "2026-08-28 12:00",
            },
        }
        with patch.object(weather, "make_weather_request", AsyncMock(return_value=payload)):
            result = asyncio.run(weather.get_current_weather("Hanoi"))
        self.assertIn("Current Weather for Hanoi, Vietnam", result)
        self.assertNotIn("Hanoi, , Vietnam", result)
        self.assertIn("Temperature: 30°C", result)

    def test_forecast_clamps_days_to_free_tier_range(self):
        payload = {
            "location": {"name": "Hanoi", "region": "", "country": "Vietnam"},
            "forecast": {"forecastday": []},
        }
        request = AsyncMock(return_value=payload)
        with patch.object(weather, "make_weather_request", request):
            asyncio.run(weather.get_forecast("Hanoi", 0))
            self.assertEqual(request.await_args.args[1]["days"], "1")
            asyncio.run(weather.get_forecast("Hanoi", 10))
            self.assertEqual(request.await_args.args[1]["days"], "3")


if __name__ == "__main__":
    unittest.main()
