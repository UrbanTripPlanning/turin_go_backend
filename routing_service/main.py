import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from routing_service.job.base import register_jobs
from fastapi import FastAPI
from routing_service.routers import route

app = FastAPI(title="routing service")
scheduler = BackgroundScheduler()
# register
app.include_router(route.router, prefix="/route", tags=["Route"])


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_running_loop()
    register_jobs(scheduler, loop)
    scheduler.start()
