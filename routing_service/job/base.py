import asyncio
from datetime import datetime, timedelta
from routing_service.job import traffic
from apscheduler.schedulers.background import BackgroundScheduler


def register_jobs(scheduler: BackgroundScheduler, loop):
    def async_wrapper(job):
        def run():
            if loop and loop.is_running():
                loop.call_soon_threadsafe(asyncio.create_task, job())
        return run

    scheduler.add_job(
        async_wrapper(traffic.load_current_traffic),
        'interval',
        seconds=5 * 60,
        next_run_time=datetime.now() + timedelta(minutes=2)
    )
    scheduler.add_job(
        async_wrapper(traffic.load_future_traffic),
        'interval',
        seconds=60 * 60,
        next_run_time=datetime.now() + timedelta(minutes=3)
    )
