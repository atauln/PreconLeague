from fastapi import APIRouter, HTTPException
from db import get_deck_by_id, get_all_decks, create_deck, get_user_decks, get_user_by_id, create_user
from db import find_deck_by_moxfield_url, find_deck_by_archidekt_url
from funcs.moxfield import fetch_moxfield_deck
from funcs.archidekt import fetch_archidekt_deck

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
async def register_deck(data: Dict[str, Any]):
    if data.get("source") not in ["moxfield", "archidekt"]:
        raise HTTPException(status_code=400, detail="Invalid source. Must be 'moxfield' or 'archidekt'")
    if data.get("source") == "moxfield" and not data.get("moxfield_deck_url"):
        raise HTTPException(status_code=400, detail="Missing moxfield_deck_url for Moxfield source")
    if data.get("source") == "archidekt" and not data.get("archidekt_deck_url"):
        raise HTTPException(status_code=400, detail="Missing archidekt_deck_url for Archidekt source")

    # get deck data
    if data.get("source") == "moxfield":
        if await find_deck_by_moxfield_url(data.get("moxfield_deck_url")) is not None:
            raise HTTPException(status_code=400, detail="Deck with this Moxfield URL already exists")
        deck_data = fetch_moxfield_deck(data.get("moxfield_deck_url"))
    else:  # archidekt
        if await find_deck_by_archidekt_url(data.get("archidekt_deck_url")) is not None:
            raise HTTPException(status_code=400, detail="Deck with this Archidekt URL already exists")
        deck_data = fetch_archidekt_deck(data.get("archidekt_deck_url"))
    
    # ensure user exists
    if await get_user_by_id(data.get("user_id")) is None:
        await create_user(user_name=deck_data.owner_name)
    deck_id = await create_deck(
        moxfield_deck_url=data.get("moxfield_deck_url"),
        archidekt_deck_url=data.get("archidekt_deck_url"),
        user_id=data.get("user_id"),
        deck_name=data.get("deck_name"),
        source=data.get("source")
    )
    if deck_id:
        return {"deck_id": deck_id}
    raise HTTPException(status_code=500, detail="Failed to create deck")
