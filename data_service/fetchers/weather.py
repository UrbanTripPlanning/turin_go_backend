import asyncio
import os
import requests
from enums.weather import Weather
from dotenv import load_dotenv
from datetime import datetime, timedelta
from data_service.database import get_mongo_collection

load_dotenv()


class WeatherQuery:
    _current = {
        'url': os.getenv('CURRENT_URL'),
        'params': {
            "apiKey": os.getenv("API_KEY"),
            "format": "json",
            "stationId": "ITURIN3276",  # Torino center (Piazza Castello) station id
            "units": "m"
        }
    }
    _forecast = {
        'url': os.getenv('FORECAST_URL'),
        'params': {
            "apiKey": os.getenv("API_KEY"),
            "format": "json",
            "postalKey": "10121:IT",  # Hardcoded for Torino center (Piazza Castello)
            "units": "e",
            "language": "en-US"
        }
    }

    def __init__(self, api_type):
        self.api_type = api_type

    def fetch_data(self):
        if self.api_type == 'current':
            conf = self._current
        elif self.api_type == 'forecast':
            conf = self._forecast
        else:
            print(f"Invalid api type: {self.api_type}")
            return
        response = requests.get(conf['url'], params=conf['params'])
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching {self.api_type} data: {response.status_code} - {response.text}")
            return None


WeatherQuery.CURRENT = WeatherQuery(api_type='current')
WeatherQuery.FORECAST = WeatherQuery(api_type='forecast')


def get_current_condition():
    """
    Analyzes the current observation data to decide if it is raining.
    It uses metrics like accumulated precipitation, humidity, temperature–dew point closeness,
    and solar radiation to determine the condition.
    Returns a tuple: (rain_flag, condition) where condition is "rain" if raining, else "clear".
    """
    current_data = WeatherQuery.CURRENT.fetch_data()
    if not current_data:
        return 0, Weather.CLEAR
    try:
        observations = current_data.get("observations", [])
        if not observations:
            print("No current observations available.")
            return 0, Weather.CLEAR
        obs = observations[0]
        metric = obs.get("metric", {})
        precip_total = float(metric.get("precipTotal", 0))
        temp = float(metric.get("temp", 0))
        dewpt = float(metric.get("dewpt", 0))
        humidity = float(obs.get("humidity", 0))
        solar_rad = float(obs.get("solarRadiation", 0))

        if precip_total > 0.1 or (humidity >= 90 and abs(temp - dewpt) < 1 and solar_rad < 10):
            return 1, Weather.RAIN
        else:
            return 0, Weather.CLEAR
    except Exception as e:
        print(f"Error parsing current observation: {e}")
        return 0, Weather.CLEAR


def determine_condition(narrative: str, rain_flag: int):
    """
    Determines a generic weather condition ("rain", "cloud", or "clear") based on the forecast narrative.
    If rain_flag is 1, returns "rain". Otherwise, it looks for keywords in the narrative.
    """
    if rain_flag == 1:
        return Weather.CLEAR
    if narrative:
        narrative_lower = narrative.lower()
        if "rain" in narrative_lower:
            return Weather.RAIN
        elif "cloud" in narrative_lower:
            return Weather.CLOUDS
        elif "sun" in narrative_lower:
            return Weather.CLEAR
    return Weather.CLEAR


async def fetch_hourly_data(threshold: int = 50):
    """
    Creates a CSV file with columns: 'datetime', 'rain', and 'weather_condition'.
    For each hour (from 00:00 to 23:00) for each day in the forecast data,
    only rows from the current time onward are included.
      - For the current day, the current observation data is used.
      - For future days, "day" is defined as 07:00 <= hour < 19:00; otherwise, it's "night".
        The corresponding forecast index is:
          • 2 * day_offset for day,
          • 2 * day_offset + 1 for night.
    The datetime is formatted as '%Y-%m-%d %H:%M:%S'.
    """
    forecast_data = WeatherQuery.FORECAST.fetch_data()
    if not forecast_data:
        print("Forecast data is not available.")
        return

    rain_flag_curr, weather_type_curr = get_current_condition()

    valid_dates = forecast_data.get("validTimeLocal", [])
    daypart_info = forecast_data.get("daypart", [{}])[0]
    precip_list = daypart_info.get("precipChance", [])
    narrative_list = daypart_info.get("narrative", [])
    num_days = len(valid_dates)
    now = datetime.now()

    records = []
    for i in range(num_days):
        date_str = valid_dates[i][:10]
        day_date = datetime.strptime(date_str, "%Y-%m-%d")
        for hour in range(24):
            current_dt = day_date + timedelta(hours=hour)
            # For the current day, include hours starting from the current hour (include the current hour)
            if current_dt.date() == now.date() and current_dt.hour < now.hour:
                continue
            if i == 0:
                condition = weather_type_curr
            else:
                # Define "day" period as 07:00 to 19:00; otherwise "night"
                if 7 <= current_dt.hour < 19:
                    index = 2 * i
                else:
                    index = 2 * i + 1
                if index >= len(precip_list) or precip_list[index] is None:
                    condition = "clear"
                else:
                    precip = precip_list[index]
                    rain = 1 if precip >= threshold else 0
                    narrative = narrative_list[index] if index < len(narrative_list) and narrative_list[
                        index] else ""
                    condition = determine_condition(narrative, rain)
            records.append({
                'date': date_str,
                'hour': hour,
                'condition': condition.value,
                'desc': condition.name()
            })
    weather_collection = get_mongo_collection('weather_data')
    for record in records:
        _ = await weather_collection.update_one({"date": record["date"], "hour": record["hour"]},
                                                {"$set": record}, upsert=True)


def test():
    asyncio.run(fetch_hourly_data())
