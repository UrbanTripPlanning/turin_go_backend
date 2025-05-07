import asyncio
from data_service.job import weather
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler


def register_jobs(scheduler: BackgroundScheduler, loop):
    def async_wrapper(job):
        def run():
            if loop and loop.is_running():
                loop.call_soon_threadsafe(asyncio.create_task, job())
        return run

    scheduler.add_job(
        async_wrapper(weather.fetch_weather),
        'interval',
        seconds=30 * 60,
        next_run_time=datetime.now() + timedelta(minutes=2)
    )
