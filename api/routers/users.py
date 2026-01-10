from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from db import get_user_by_id, get_all_users, create_user

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

@router.post("/")
async def register_user(user: Dict[str, Any]):
    user_name = user.get("user_name")
    if not user_name:
        raise HTTPException(status_code=400, detail="user_name is required")
    user_id = await create_user(user_name)
    if user_id:
        return {"user_id": user_id, "user_name": user_name}
    raise HTTPException(status_code=500, detail="Failed to create user")
