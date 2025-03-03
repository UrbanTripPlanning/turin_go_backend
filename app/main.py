import uvicorn
from fastapi import FastAPI
from app.routers import hello
from app.middleware import handle_wrapper_middleware


app = FastAPI(title="Turin Go")
app.middleware("http")(handle_wrapper_middleware)
# register
app.include_router(hello.router, prefix="/hello", tags=["Hello"])


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
