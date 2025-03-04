from fastapi import Request
from fastapi.responses import JSONResponse


async def handle_wrapper_middleware(request: Request, call_next):
    # TODO: handle request

    try:
        response = await call_next(request)
        # TODO: handle response
        return response
    except Exception as e:
        return JSONResponse(
            content={"code": -1, "message": str(e), "data": None},
            status_code=500
        )
