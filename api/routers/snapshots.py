from fastapi import APIRouter, HTTPException
from db import get_snapshot_by_id, get_all_snapshots, create_snapshot, get_deck_snapshots
from db import get_snapshot_with_library, get_deck_by_id, associate_card_with_snapshot
from db import get_card_by_id, create_card, get_most_recent_snapshot_for_deck
from db import get_all_snapshots_for_week
from db import get_cards_by_ids, create_cards_bulk, associate_cards_with_snapshot_bulk
from funcs.archidekt import fetch_archidekt_deck
from funcs.moxfield import fetch_moxfield_deck
from funcs.commandersalt import fetch_commandersalt_deck_data
from typing import Any, Dict
from funcs.models import SnapshotCreateRequest, SnapshotCreateResponse

router = APIRouter(
    prefix="/snapshots",
    tags=["snapshots"],
)

@router.get("/{snapshot_id}")
async def read_snapshot(snapshot_id: int):
    snapshot = await get_snapshot_by_id(snapshot_id)
    if snapshot:
        return snapshot
    raise HTTPException(status_code=404, detail="Snapshot not found")

@router.get("/")
async def read_all_snapshots():
    snapshots = await get_all_snapshots()
    if snapshots:
        return snapshots
    raise HTTPException(status_code=404, detail="No snapshots found")

@router.get("/deck/{deck_id}")
async def read_deck_snapshots(deck_id: int):
    snapshots = await get_deck_snapshots(deck_id)
    if snapshots:
        return snapshots
    raise HTTPException(status_code=404, detail="No snapshots found for this deck")

@router.post("/", response_model=SnapshotCreateResponse)
async def create_new_snapshot(snapshot: Any):
    # Support both dict inputs (tests) and Pydantic models (FastAPI)
    if isinstance(snapshot, dict):
        deck_id = snapshot.get("deck_id")
        snapshot_name = snapshot.get("snapshot_name")
    else:
        deck_id = getattr(snapshot, "deck_id", None)
        snapshot_name = getattr(snapshot, "snapshot_name", None)

    if not deck_id or not snapshot_name:
        raise HTTPException(status_code=400, detail="deck_id and snapshot_name are required")
    snapshot_id = await create_snapshot(deck_id, snapshot_name)
    if snapshot_id:
        return {"snapshot_id": snapshot_id, "snapshot_name": snapshot_name, "deck_id": deck_id}
    raise HTTPException(status_code=500, detail="Failed to create snapshot")

@router.get("/with_library/{snapshot_id}")
async def read_snapshot_with_library(snapshot_id: int):
    snapshot = await get_snapshot_with_library(snapshot_id)
    if snapshot:
        return snapshot
    raise HTTPException(status_code=404, detail="Snapshot not found")

@router.post("/create_snapshot/{deck_id}")
async def trigger_create_snapshot(deck_id: int):
    deck = await get_deck_by_id(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    source = deck.get("source")
    source_deck_url = deck.get("moxfield_deck_url") if source == "moxfield" else deck.get("archidekt_deck_url")

    if source == "moxfield":
        proc_deck = fetch_moxfield_deck(source_deck_url)
    elif source == "archidekt":
        proc_deck = fetch_archidekt_deck(source_deck_url)
    else:
        raise HTTPException(status_code=400, detail="Invalid deck source")
    
    commandersalt_data = fetch_commandersalt_deck_data(source_deck_url)
    
    # For simplicity, let's assume the first commander is the main one
    if not proc_deck.commanders:
        raise HTTPException(status_code=400, detail="No commanders found in the deck")
    
    commander = proc_deck.commanders[0]

    # Ensure commander card exists in `cards` table because `snapshots.commander_id` is FK to cards(oracle_card_id)
    existing_commander = await get_card_by_id(commander.id)
    if not existing_commander:
        await create_card(commander.id, commander.name)
    
    week_of_league = 0
    most_recent_snapshot = await get_most_recent_snapshot_for_deck(deck_id)
    if most_recent_snapshot:
        week_of_league = most_recent_snapshot.get("week_of_league", -1) + 1

    snapshot_id = await create_snapshot(
        deck_id=deck_id,
        commander_id=commander.id,
        salt_rating=commandersalt_data.salt_rating,
        synergy_rating=commandersalt_data.synergy_rating,
        power_level_rating=commandersalt_data.power_level_rating,
        threat_rating=commandersalt_data.threat_rating,
        bracket_rating=commandersalt_data.bracket_rating,
        overall_rating=commandersalt_data.overall_rating,
        manabase_score=commandersalt_data.manabase_score,
        power_level_display_value=commandersalt_data.power_level_display_value,
        combo_rating=commandersalt_data.combo_rating,
        archetype_minor=commandersalt_data.archetype_minor,
        archetype_major=commandersalt_data.archetype_major,
        price_usd=commandersalt_data.price_usd,
        week_of_league=week_of_league
    )

    # Batch card handling: check which cards already exist, insert missing, then bulk-associate
    card_ids = [card.id for card in proc_deck.library]
    # Query existing cards in one go
    existing_cards = await get_cards_by_ids(card_ids)
    existing_ids = {c.get('oracle_card_id') for c in existing_cards}

    # Prepare list of missing cards (oracle_card_id, card_name)
    missing_cards = [ (card.id, card.name) for card in proc_deck.library if card.id not in existing_ids ]
    if missing_cards:
        await create_cards_bulk(missing_cards)

    # Associate all library cards with the snapshot in bulk
    await associate_cards_with_snapshot_bulk(snapshot_id, card_ids)
    
    if snapshot_id:
        return {"snapshot_id": snapshot_id, "deck_id": deck_id}
    raise HTTPException(status_code=500, detail="Failed to create snapshot")

@router.get("/week/{week_of_league}")
async def read_snapshots_for_week(week_of_league: int):
    snapshots = await get_all_snapshots_for_week(week_of_league)
    if snapshots:
        return snapshots
    raise HTTPException(status_code=404, detail="No snapshots found for this week")
