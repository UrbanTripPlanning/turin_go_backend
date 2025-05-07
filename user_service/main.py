import asyncio
from fastapi import FastAPI
from user_service.job.base import register_jobs
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from user_service.routers import common, map, route, place
from user_service.middleware import handle_wrapper_middleware
from apscheduler.schedulers.background import BackgroundScheduler


app = FastAPI(title="user service")
scheduler = BackgroundScheduler()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(handle_wrapper_middleware)
# register
app.include_router(route.router, prefix="/route", tags=["Route"])
app.include_router(common.router, prefix="/common", tags=["Common"])
app.include_router(map.router, prefix="/map", tags=["Map"])
app.include_router(place.router, prefix="/place", tags=["Place"])


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_running_loop()
    register_jobs(scheduler, loop)
    scheduler.start()


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
