from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
async def login():
    return {"token": "fake-jwt-token"}
