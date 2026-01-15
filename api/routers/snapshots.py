from fastapi import APIRouter, HTTPException
from db import get_snapshot_by_id, get_all_snapshots, create_snapshot, get_deck_snapshots, get_most_recent_snapshot_for_deck
from db import get_most_recent_snapshots_per_deck_all_weeks
from db import get_snapshot_with_library, get_deck_by_id, associate_card_with_snapshot
from db import get_card_by_id, create_card
from db import get_all_snapshots_for_week, update_snapshot_week
from db import get_cards_by_ids, create_cards_bulk, associate_cards_with_snapshot_bulk
from funcs.archidekt import fetch_archidekt_deck
from funcs.moxfield import fetch_moxfield_deck
from funcs.commandersalt import fetch_commandersalt_deck_data
from typing import Any, Dict
from funcs.models import SnapshotCreateRequest, SnapshotCreateResponse
from datetime import datetime

STARTING_DATE_FOR_LEAGUE = datetime(2026, 1, 12)  # Example starting date
CURRENT_WEEK_NUMBER = (datetime.now() - STARTING_DATE_FOR_LEAGUE).days // 7 + 1

router = APIRouter(
    prefix="/snapshots",
    tags=["snapshots"],
)

def __sort_snapshots_by_date(snapshots: list) -> list:
    # Some snapshots returned by tests or db mocks may not have `created_at` set.
    # Use empty-string fallback so keys are comparable (strings) and sorting won't
    # raise TypeError when values are None.
    return sorted(snapshots, key=lambda x: x.get("created_at") or "", reverse=True)

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
        return __sort_snapshots_by_date(snapshots)
    raise HTTPException(status_code=404, detail="No snapshots found")

@router.get("/deck/{deck_id}")
async def read_deck_snapshots(deck_id: int):
    snapshots = await get_deck_snapshots(deck_id)
    if snapshots:
        return __sort_snapshots_by_date(snapshots)
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
        week_of_league=CURRENT_WEEK_NUMBER
    )

    # Batch card handling: expand card IDs to repeat per-card quantities
    # so the DB will receive one row per copy.
    card_ids = []
    for card in proc_deck.library:
        cid = getattr(card, 'id', None)
        if cid is None:
            continue
        qty = getattr(card, 'quantity', None)
        qty = qty if isinstance(qty, int) and qty > 0 else 1
        for _ in range(qty):
            card_ids.append(cid)
    # Query existing cards in one go
    existing_cards = await get_cards_by_ids(card_ids)
    existing_ids = {c.get('oracle_card_id') for c in existing_cards}

    # Prepare list of missing cards (oracle_card_id, card_name)
    missing_cards = [ (card.id, card.name) for card in proc_deck.library if card.id not in existing_ids ]
    if missing_cards:
        await create_cards_bulk(missing_cards)

    # Associate all library cards with the snapshot in bulk (card_ids may contain duplicates)
    await associate_cards_with_snapshot_bulk(snapshot_id, card_ids)
    
    if snapshot_id:
        return {"snapshot_id": snapshot_id, "deck_id": deck_id}
    raise HTTPException(status_code=500, detail="Failed to create snapshot")

@router.get("/week/{week_of_league}")
async def read_snapshots_for_week(week_of_league: int):
    snapshots = await get_all_snapshots_for_week(week_of_league)
    if snapshots:
        return __sort_snapshots_by_date(snapshots)
    raise HTTPException(status_code=404, detail="No snapshots found for this week")

@router.get("/week/{week_of_league}/most_recent")
async def read_most_recent_snapshots_for_week(week_of_league: int):
    snapshots = []
    deck_ids = []
    snapshots_all = await get_all_snapshots_for_week(week_of_league)
    for snapshot in snapshots_all:
        deck_id = snapshot.get("deck_id")
        if deck_id not in deck_ids:
            deck_ids.append(deck_id)
    for deck_id in deck_ids:
        snapshot = await get_most_recent_snapshot_for_deck(deck_id, week_of_league)
        if snapshot:
            snapshots.append(snapshot)
    if snapshots:
        return __sort_snapshots_by_date(snapshots)
    raise HTTPException(status_code=404, detail="No snapshots found for this week")


@router.get("/most_recent/per_deck")
async def read_most_recent_snapshots_per_deck_all_weeks():
    """Return the most recent snapshot per deck per week (only snapshots with week_of_league set).

    This endpoint is intended for bulk consumption by analytics pages so the
    frontend can fetch aggregated "All Decks" metrics in a single request.
    """
    snapshots = await get_most_recent_snapshots_per_deck_all_weeks()
    if snapshots:
        return __sort_snapshots_by_date(snapshots)
    raise HTTPException(status_code=404, detail="No snapshots found")

#update week of snapshot for manual corrections
@router.put("/{snapshot_id}/week/{new_week_of_league}")
async def upd_snapshot_week(snapshot_id: int, new_week_of_league: int):
    success = await update_snapshot_week(snapshot_id, new_week_of_league)
    if success:
        return {"message": "Snapshot week updated successfully"}
    raise HTTPException(status_code=500, detail="Failed to update snapshot week")

@router.get("/{snapshot_id}/changes/{old_snapshot_id}")
async def read_snapshot_changes(snapshot_id: int, old_snapshot_id: int):
    new_snapshot = await get_snapshot_with_library(snapshot_id)
    old_snapshot = await get_snapshot_with_library(old_snapshot_id)

    if not new_snapshot or not old_snapshot:
        raise HTTPException(status_code=404, detail="One or both snapshots not found")
    if new_snapshot.get("deck_id") != old_snapshot.get("deck_id"):
        raise HTTPException(status_code=400, detail="Snapshots do not belong to the same deck")
    # Build counts for each card_id in both snapshots. Some entries may
    # include an explicit `quantity` field; others may appear multiple
    # times (one entry per copy). Support both patterns.
    def _counts_from_library(lib_cards: list) -> tuple:
        """Return (counts, meta) where:
        - counts maps a canonical key (prefer card_name when available, otherwise oracle id)
          to total quantity (number of rows / summed quantity).
        - meta maps the same canonical key to a dict with keys `card_id` (example
          oracle_card_id) and `card_name` (if available).
        """
        counts = {}
        meta = {}
        for c in lib_cards or []:
            # support a few possible id keys coming from different codepaths
            card_id = c.get('card_id') or c.get('oracle_card_id') or c.get('id')
            card_name = c.get('card_name') or c.get('card_name') or c.get('name')
            if card_id is None and not card_name:
                continue

            # canonical key: prefer name when present so variants map together
            key = card_name if card_name else card_id

            # quantity: older rows may have explicit `quantity`, but most rows are
            # one per copy (repeated rows). Support both patterns.
            qty = c.get('quantity') if isinstance(c.get('quantity'), int) else 1

            counts[key] = counts.get(key, 0) + (qty or 0)
            # store an example oracle id and name for this key (if not already set)
            if key not in meta:
                meta[key] = {'card_id': card_id, 'card_name': card_name}

        return counts, meta

    new_counts, new_meta = _counts_from_library(new_snapshot.get('library_cards', []))
    old_counts, old_meta = _counts_from_library(old_snapshot.get('library_cards', []))

    if not new_counts and not old_counts:
        raise HTTPException(status_code=404, detail="No cards found in either snapshot")

    added_cards = []
    removed_cards = []

    all_keys = set(new_counts.keys()) | set(old_counts.keys())
    for key in all_keys:
        n_qty = new_counts.get(key, 0)
        o_qty = old_counts.get(key, 0)
        qty_diff = abs(n_qty - o_qty)
        if qty_diff == 0:
            continue

        # Prefer metadata from the 'new' snapshot if available, otherwise fall back
        meta = new_meta.get(key) or old_meta.get(key) or {'card_id': None, 'card_name': None}
        entry = {
            'card_id': meta.get('card_id'),
            'card_name': meta.get('card_name'),
            'quantity': qty_diff,
        }

        if n_qty > o_qty:
            added_cards.append(entry)
        else:
            removed_cards.append(entry)

    return {
        "added_cards": added_cards,
        "removed_cards": removed_cards
    }
