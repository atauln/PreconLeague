from fastapi import APIRouter, HTTPException
from db import get_snapshot_by_id, get_all_snapshots, create_snapshot, get_deck_snapshots
from db import get_snapshot_with_library
from typing import Any, Dict

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

@router.post("/")
async def create_new_snapshot(snapshot: Dict[str, Any]):
    deck_id = snapshot.get("deck_id")
    snapshot_name = snapshot.get("snapshot_name")
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
