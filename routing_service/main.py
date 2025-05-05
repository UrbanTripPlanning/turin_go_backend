import uvicorn
from fastapi import FastAPI
from routing_service.routers import route
from routing_service.cache.traffic import load_traffic_data

app = FastAPI(title="routing service")
# register
app.include_router(route.router, prefix="/route", tags=["Route"])


@app.on_event("startup")
async def startup_event():
    # init
    await load_traffic_data()

# if __name__ == '__main__':
#     uvicorn.run(app, host="0.0.0.0", port=8003, reload=True)
