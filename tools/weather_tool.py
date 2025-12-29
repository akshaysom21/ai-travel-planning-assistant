from langchain.tools import tool
import requests
from datetime import datetime, timedelta
from utils.geo import CITY_COORDS

@tool
def get_weather(city: str, days: int = 7):
    """
    Get weather forecast for a city with day-wise breakdown.

    Args:
        city: City name
        days: Number of days to forecast (default: 7, max: 7)

    Returns:
        Detailed weather forecast with daily temperatures
    """
    try:
        city_lower = city.lower().strip()

        # Check if city coordinates are available
        if city_lower not in CITY_COORDS:
            return f"""
🌤️ Weather Information for {city.title()}

⚠️ Detailed weather data not available for {city}.

Expected Conditions (Seasonal Estimate):
  • Temperature: 18-25°C (Pleasant winter weather)
  • Conditions: Clear to partly cloudy
  • Best for: Sightseeing and outdoor activities

Note: For accurate forecasts, please check local weather services.
"""

        coords = CITY_COORDS[city_lower]

        # Call Open-Meteo API with proper parameters
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode",
            "timezone": "Asia/Kolkata",
            "forecast_days": min(days, 7)
        }

        # Make request with timeout
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Parse forecast data
        daily = data.get("daily", {})
        dates = daily.get("time", [])[:days]
        max_temps = daily.get("temperature_2m_max", [])[:days]
        min_temps = daily.get("temperature_2m_min", [])[:days]
        precipitation = daily.get("precipitation_probability_max", [])[:days]
        weather_codes = daily.get("weathercode", [])[:days]

        if not dates:
            raise ValueError("No forecast data returned")

        # Weather code to description mapping
        weather_descriptions = {
            0: "Clear sky ☀️", 1: "Mainly clear 🌤️", 2: "Partly cloudy ⛅", 3: "Overcast ☁️",
            45: "Foggy 🌫️", 48: "Foggy 🌫️",
            51: "Light drizzle 🌦️", 53: "Drizzle 🌦️", 55: "Heavy drizzle 🌧️",
            61: "Light rain 🌧️", 63: "Moderate rain 🌧️", 65: "Heavy rain ⛈️",
            71: "Light snow ❄️", 73: "Moderate snow 🌨️", 75: "Heavy snow ❄️",
            80: "Rain showers 🌦️", 81: "Rain showers 🌧️", 82: "Heavy showers ⛈️",
            95: "Thunderstorm ⛈️", 96: "Thunderstorm with hail ⛈️", 99: "Heavy thunderstorm ⛈️"
        }

        # Build day-wise forecast
        forecast_lines = []
        for i, date in enumerate(dates):
            date_obj = datetime.fromisoformat(date)
            day_name = date_obj.strftime("%A, %b %d")

            max_t = round(max_temps[i]) if i < len(max_temps) else "N/A"
            min_t = round(min_temps[i]) if i < len(min_temps) else "N/A"
            precip = round(precipitation[i]) if i < len(precipitation) else 0
            w_code = weather_codes[i] if i < len(weather_codes) else 0
            weather = weather_descriptions.get(w_code, "Clear ☀️")

            # Add rain warning if high precipitation
            rain_note = f" (Rain: {precip}%)" if precip > 30 else ""

            forecast_lines.append(
                f"  📅 Day {i+1} ({day_name}): {max_t}°C / {min_t}°C - {weather}{rain_note}"
            )

        # Build final output
        result = f"""
🌤️ Weather Forecast for {city.title()}

{chr(10).join(forecast_lines)}

📍 Source: Open-Meteo API (Live Data)
💡 Pack accordingly based on the forecast!
"""
        return result

    except requests.Timeout:
        return f"""
🌤️ Weather Information for {city.title()}

⚠️ Weather service temporarily unavailable (timeout).

Expected Conditions (December/Winter Season):
  • Temperature: 15-22°C (Cool and pleasant)
  • Conditions: Generally clear with cool mornings
  • What to pack: Light jacket for mornings, comfortable clothes for day

Recommendation: Check local weather closer to travel date.
"""

    except requests.RequestException as e:
        return f"""
🌤️ Weather Information for {city.title()}

⚠️ Unable to fetch live weather data.

Seasonal Conditions (December/Winter):
  • Expected Temperature: 15-25°C
  • Typical Conditions: Pleasant and mild
  • Best for: Sightseeing, outdoor activities

Note: Weather conditions in India during winter are generally favorable for travel.
"""

    except Exception as e:
        return f"""
🌤️ Weather Information for {city.title()}

⚠️ Weather service error: {str(e)}

General Forecast:
  • Temperature: Moderate (18-24°C expected)
  • Conditions: Pleasant for travel
  • Recommendation: Check local forecasts before departure

The trip can proceed as planned with normal precautions.
"""
