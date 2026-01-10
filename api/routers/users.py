from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from db import get_user_by_id, get_all_users, create_user
from funcs.models import UserCreateRequest, UserCreateResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/{user_id}")
async def read_user(user_id: int):
    user = await get_user_by_id(user_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@router.get("/")
async def read_all_users():
    users = await get_all_users()
    if users:
        return users
    raise HTTPException(status_code=404, detail="No users found")

@router.post("/", response_model=UserCreateResponse)
async def register_user(user: Any):
    # Accept either a dict (used by some unit tests) or a Pydantic model (from FastAPI request)
    if isinstance(user, dict):
        user_name = user.get("user_name")
    else:
        user_name = getattr(user, "user_name", None)

    if not user_name:
        raise HTTPException(status_code=400, detail="user_name is required")
    user_id = await create_user(user_name)
    if user_id:
        return {"user_id": user_id, "user_name": user_name}
    raise HTTPException(status_code=500, detail="Failed to create user")
