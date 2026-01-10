from fastapi import APIRouter, HTTPException
from db import (
    get_deck_by_id,
    get_all_decks,
    create_deck,
    get_user_decks,
    get_user_by_id,
    get_user_by_name,
    create_user,
)
from db import find_deck_by_moxfield_url, find_deck_by_archidekt_url
from funcs.moxfield import fetch_moxfield_deck
from funcs.archidekt import fetch_archidekt_deck
from funcs.models import DeckRegisterRequest, DeckRegisterResponse

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

@router.post("/", response_model=DeckRegisterResponse)
async def register_deck(request: DeckRegisterRequest):
    # check if deck already exists
    if request.source == "moxfield":
        if await find_deck_by_moxfield_url(str(request.deck_url)) is not None:
            raise HTTPException(status_code=400, detail="Deck with this Moxfield URL already exists")
        deck_data = fetch_moxfield_deck(str(request.deck_url))
    else:  # archidekt
        if await find_deck_by_archidekt_url(str(request.deck_url)) is not None:
            raise HTTPException(status_code=400, detail="Deck with this Archidekt URL already exists")
        deck_data = fetch_archidekt_deck(str(request.deck_url))

    # ensure user exists (by name). If not, create user and use returned id.
    existing_user = await get_user_by_name(deck_data.owner_name)
    if existing_user:
        user_id = existing_user.get("user_id")
    else:
        user_id = await create_user(user_name=deck_data.owner_name)
    if not user_id:
        raise HTTPException(status_code=500, detail="Failed to determine or create user for deck owner")

    # create deck record
    if request.source == "moxfield":
        deck_id = await create_deck(
            user_id=user_id,
            deck_name=deck_data.name,
            source=request.source,
            moxfield_deck_url=str(request.deck_url),
        )
    else:
        deck_id = await create_deck(
            user_id=user_id,
            deck_name=deck_data.name,
            source=request.source,
            archidekt_deck_url=str(request.deck_url),
        )

    if deck_id:
        return DeckRegisterResponse(deck_id=deck_id)
    raise HTTPException(status_code=500, detail="Failed to create deck")
