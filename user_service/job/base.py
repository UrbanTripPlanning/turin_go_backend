import asyncio
from user_service.job import plan
from apscheduler.schedulers.background import BackgroundScheduler


def register_jobs(scheduler: BackgroundScheduler, loop):
    def async_wrapper(job):
        def run():
            if loop and loop.is_running():
                loop.call_soon_threadsafe(asyncio.create_task, job())
        return run

    scheduler.add_job(async_wrapper(plan.check_future_plans), 'interval', seconds=5 * 60)
