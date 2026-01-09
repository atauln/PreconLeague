from pyrchidekt.api import getDeckById
from pyrchidekt.deck import Deck
from pprint import pprint

# Categories to ignore when processing the deck
BLACKLISTED_CATEGORIES = [
    "maybeboard",
    "sideboard"
]

# Data classes for processed deck and cards
class ProcCard:
    def __init__(self, card_id: int, card_name: str, quantity: int):
        self.card_id = card_id
        self.card_name = card_name
        self.quantity = quantity
    
    def __repr__(self):
        return f"ProcCard(card_id={self.card_id}, card_name='{self.card_name}', quantity={self.quantity})"

class ProcDeck:
    def __init__(self, deck: Deck):
        self.id = deck.id
        self.name = deck.name
        self.owner_id = deck.owner.id
        self.owner_name = deck.owner.username
        self.library: list[ProcCard] = []
        self.commanders: list[ProcCard] = []
    
    def library_size(self) -> int:
        total_quantity = sum(card.quantity for card in self.library)
        commander_quantity = sum(card.quantity for card in self.commanders)
        total_quantity += commander_quantity
        return total_quantity
    
    def __repr__(self):
        return (f"ProcDeck(id={self.id}, name='{self.name}', owner_id={self.owner_id}, "
                f"owner_name='{self.owner_name}', library_size={self.library_size()}, "
                f"commanders={self.commanders})")


# Internal function to fetch the deck without processing
def __fetch_deck_unprocessed(deck_id: int) -> Deck:
    return getDeckById(deck_id)

# Main function to fetch and process the deck
def fetch_deck(deck_id: int) -> ProcDeck:
    deck = __fetch_deck_unprocessed(deck_id)
    proc_deck = ProcDeck(deck)

    card_dict = {}

    for category in deck.categories:
        if category.name.lower() == "commander": # special handling for commanders
            proc_deck.commanders = [
                ProcCard(card.id, card.card.oracle_card.name, card.quantity)
                for card in category.cards]
            continue
        if category.name.lower() in BLACKLISTED_CATEGORIES: # skip anything but the mainboard
            continue
        for card in category.cards:
            if card.categories and any(cat.lower() in BLACKLISTED_CATEGORIES for cat in card.categories):
                continue # double check, since some cards have multiple categories (including maybeboard/sideboard)
            card_dict[card.id] = ProcCard(card.id, card.card.oracle_card.name, card.quantity)
    
    # convert the set to a list for better usability
    proc_deck.library = list(card_dict.values())

    return proc_deck

if __name__ == "__main__":
    deck = fetch_deck(18053512)
    pprint(sorted(deck.library, key=lambda card: card.card_name), indent=2)
    print(f"Library size: {deck.library_size()}")
