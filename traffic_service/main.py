import uvicorn
from fastapi import FastAPI
from traffic_service.routers import traffic


app = FastAPI(title="traffic service")
# register
app.include_router(traffic.router, prefix="/traffic", tags=["Traffic"])


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)
