from fastapi import APIRouter, HTTPException
from db import get_deck_by_id, get_all_decks, create_deck, get_user_decks
from typing import Any, Dict

router = APIRouter(
    prefix="/decks",
    tags=["decks"],
)

@router.get("/{deck_id}")
async def read_deck(deck_id: int):
    deck = await get_deck_by_id(deck_id)
    if deck:
        return deck
    raise HTTPException(status_code=404, detail="Deck not found")

@router.get("/")
async def read_all_decks():
    decks = await get_all_decks()
    if decks:
        return decks
    raise HTTPException(status_code=404, detail="No decks found")

@router.get("/user/{user_id}")
async def read_user_decks(user_id: int):
    decks = await get_user_decks(user_id)
    if decks:
        return decks
    raise HTTPException(status_code=404, detail="No decks found for this user")

@router.post("/")
async def create_new_deck(deck: Dict[str, Any]):
    deck_name = deck.get("deck_name")
    user_id = deck.get("user_id")
    if not deck_name or not user_id:
        raise HTTPException(status_code=400, detail="deck_name and user_id are required")
    deck_id = await create_deck(user_id, deck_name)
    if deck_id:
        return {"deck_id": deck_id, "deck_name": deck_name, "user_id": user_id}
    raise HTTPException(status_code=500, detail="Failed to create deck")
