class Card:
    def __init__(self, card_id: str, name: str, quantity: int):
        self.id = card_id
        self.name = name
        self.quantity = quantity

    def __repr__(self):
        return f"Card(id='{self.id}', name='{self.name}', quantity={self.quantity})"

class Deck:
    def __init__(self, deck_id: str, name: str, owner_id: str, owner_name: str, source: str = "Unknown"):
        self.id = deck_id
        self.name = name
        self.owner_id = owner_id
        self.owner_name = owner_name
        self.source = source
        self.library: list[Card] = []
        self.commanders: list[Card] = []
    
    def library_size(self) -> int:
        return sum(card.quantity for card in self.library) + sum(card.quantity for card in self.commanders)
    
    def __repr__(self):
        return (f"ProcDeck(id={self.id}, name='{self.name}', owner_id={self.owner_id}, "
                f"owner_name='{self.owner_name}', library_size={self.library_size()}, "
                f"commanders={self.commanders}, source='{self.source}')")

class CommanderSaltData:
    """
    based on this:
    proc_data = {
        'salt_rating': float(data.get('saltRating')),
        'synergy_rating': float(data.get('synergyRating')),
        'power_level_rating': float(data.get('powerLevelRating')),
        'threat_rating': float(data.get('threatRating')),
        'bracket_rating': float(data.get('bracketRating')),
        'overall_rating': float(data.get('overallRating')),
        'manabase_score': float(data.get('details').get('manabase').get('score')),
        'power_level_display_value': int(data.get('powerLevelDisplayValue')),
        'combo_rating': float(data.get('comboRating')),
        'archetype_minor': data.get('archetypeMinor'),
        'archetype_major': data.get('archetypeMajor'),
        'price_usd': float(data.get('price').get('usd')),
    }
    """

    def __init__(self, salt_rating: float, synergy_rating: float, power_level_rating: float,
                 threat_rating: float, bracket_rating: float, overall_rating: float,
                    manabase_score: float, power_level_display_value: int,
                    combo_rating: float, archetype_minor: str, archetype_major: str,
                    price_usd: float):
        self.salt_rating = salt_rating
        self.synergy_rating = synergy_rating
        self.power_level_rating = power_level_rating
        self.threat_rating = threat_rating
        self.bracket_rating = bracket_rating
        self.overall_rating = overall_rating
        self.manabase_score = manabase_score
        self.power_level_display_value = power_level_display_value
        self.combo_rating = combo_rating
        self.archetype_minor = archetype_minor
        self.archetype_major = archetype_major
        self.price_usd = price_usd
    
    def __repr__(self):
        return (f"CommanderSaltData(salt_rating={self.salt_rating}, synergy_rating={self.synergy_rating}, "
                f"power_level_rating={self.power_level_rating}, threat_rating={self.threat_rating}, "
                f"bracket_rating={self.bracket_rating}, overall_rating={self.overall_rating}, "
                f"manabase_score={self.manabase_score}, power_level_display_value={self.power_level_display_value}, "
                f"combo_rating={self.combo_rating}, archetype_minor='{self.archetype_minor}', "
                f"archetype_major='{self.archetype_major}', price_usd={self.price_usd})")



# Pydantic models for request/response schemas (used by FastAPI for validation + Swagger)
from pydantic import BaseModel, HttpUrl
from typing import Literal


class DeckRegisterRequest(BaseModel):
    source: Literal["moxfield", "archidekt"]
    deck_url: HttpUrl


class DeckRegisterResponse(BaseModel):
    deck_id: int


# Other request models used by routers for Swagger documentation
class CreateCardRequest(BaseModel):
    card_id: str
    card_name: str


class AssociateCardRequest(BaseModel):
    snapshot_id: int
    card_id: str


class SnapshotCreateRequest(BaseModel):
    deck_id: int
    snapshot_name: str


class UserCreateRequest(BaseModel):
    user_name: str


class UserCreateResponse(BaseModel):
    user_id: int
    user_name: str


class CreateCardResponse(BaseModel):
    card_id: str
    card_name: str


class AssociateCardResponse(BaseModel):
    message: str


class SnapshotCreateResponse(BaseModel):
    snapshot_id: int
    deck_id: int
    snapshot_name: str | None = None

