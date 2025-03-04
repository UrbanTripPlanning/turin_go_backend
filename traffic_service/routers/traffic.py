from fastapi import APIRouter


router = APIRouter()


@router.get("/info")
async def info():
    # TODO: traffic graph logic
    return {}
