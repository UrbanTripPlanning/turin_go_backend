import uvicorn
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from user_service.routers import common, map, route, place
from user_service.middleware import handle_wrapper_middleware


app = FastAPI(title="user service")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:28080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(handle_wrapper_middleware)
# register
app.include_router(route.router, prefix="/route", tags=["Route"])
app.include_router(common.router, prefix="", tags=["Common"])
app.include_router(map.router, prefix="/map", tags=["Map"])
app.include_router(place.router, prefix="/place", tags=["Place"])


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
