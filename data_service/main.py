import uvicorn
from fastapi import FastAPI
from data_service.routers import weather, traffic, position, road, place

app = FastAPI(title="data service")
# register
app.include_router(weather.router, prefix="/weather", tags=["Weather"])
app.include_router(traffic.router, prefix="/traffic", tags=["Traffic"])
app.include_router(position.router, prefix="/position", tags=["Position"])
app.include_router(road.router, prefix="/road", tags=["Road"])
app.include_router(place.router, prefix="/place", tags=["Place"])


# if __name__ == '__main__':
#     uvicorn.run(app, host="0.0.0.0", port=8004, reload=True)
