import uvicorn
from fastapi import FastAPI
from routing_service.routers import route

app = FastAPI(title="routing service")
# register
app.include_router(route.router, prefix="/route", tags=["Route"])


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8003, reload=True)
