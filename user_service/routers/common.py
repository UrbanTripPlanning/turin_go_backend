import httpx
from fastapi import APIRouter
from utils.encrypt import md5_encrypt
from user_service.schemas import response
from utils.load import DATA_SERVICE_URL


router = APIRouter()


@router.get("/user")
async def user_info(user_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{DATA_SERVICE_URL}/user/{user_id}')
    return response(resp.json())


@router.get("/login")
async def login(username: str, password: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{DATA_SERVICE_URL}/user/get', params={'username': username})
    user = resp.json()
    if user is not None:
        if user['password'] != md5_encrypt(password):
            return response(None, message='password not match')
        return response({
            'user_id': user['user_id'],
            'username': user['username']
        })
    # else
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{DATA_SERVICE_URL}/user/insert', params={
            'username': username,
            'password': password
        })
    return response(resp.json())
