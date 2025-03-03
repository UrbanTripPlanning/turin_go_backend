from fastapi.responses import JSONResponse


def response(data, code=200, message="success"):
    result = {
        "code": code,
        "message": message,
        "data": data
    }
    return JSONResponse(content=result)
