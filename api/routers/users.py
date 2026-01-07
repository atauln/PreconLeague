
from typing import Any, Dict
from fastapi import APIRouter
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
    return {"error": "User not found"}

@router.get("/")
async def read_all_users():
    users = await get_all_users()
    if users:
        return users
    return {"error": "No users found"}

@router.post("/")
async def register_user(user: Dict[str, Any]):
    user_name = user.get("user_name")
    print(user_name)
    if not user_name:
        return {"error": "user_name is required"}
    user_id = await create_user(user_name)
    if user_id:
        return {"user_id": user_id, "user_name": user_name}
    return {"error": "Failed to create user"}
