from fastapi import APIRouter
from db import get_card_by_id, get_all_cards, create_card, associate_card_with_snapshot
from typing import Any, Dict
from fastapi import HTTPException

router = APIRouter(
    prefix="/cards",
    tags=["cards"],
)

@router.get("/{card_id}")
async def read_card(card_id: int):
    card = await get_card_by_id(card_id)
    if card:
        return card
    raise HTTPException(status_code=404, detail="Card not found")

@router.get("/")
async def read_all_cards():
    cards = await get_all_cards()
    if cards:
        return cards
    raise HTTPException(status_code=404, detail="No cards found")

@router.post("/")
async def create_new_card(card: Dict[str, Any]):
    card_name = card.get("card_name")
    card_id = card.get("card_id")
    if not card_name or not card_id:
        raise HTTPException(status_code=400, detail="card_name and card_id are required")
    created_card_id = await create_card(card_id, card_name)
    if created_card_id:
        return {"card_id": created_card_id, "card_name": card_name}
    raise HTTPException(status_code=500, detail="Failed to create card")

@router.post("/associate")
async def associate_card(association: Dict[str, Any]):
    snapshot_id = association.get("snapshot_id")
    card_id = association.get("card_id")
    if not snapshot_id or not card_id:
        raise HTTPException(status_code=400, detail="snapshot_id and card_id are required")
    success = await associate_card_with_snapshot(snapshot_id, card_id)
    if success:
        return {"message": "Card associated with snapshot successfully"}
    raise HTTPException(status_code=500, detail="Failed to associate card with snapshot")
