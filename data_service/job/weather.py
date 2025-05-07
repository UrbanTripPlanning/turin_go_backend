from data_service.fetchers import weather


async def fetch_weather():
    await weather.fetch_hourly_data()
