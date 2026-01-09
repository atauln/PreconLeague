from pyrchidekt.api import getDeckById
from pyrchidekt.deck import Deck as pDeck
from funcs.models import Deck, Card

# Categories to ignore when processing the deck
BLACKLISTED_CATEGORIES = [
    "maybeboard",
    "sideboard"
]

# Internal function to fetch the deck without processing
def __fetch_archidekt_deck_unprocessed(deck_id: int) -> pDeck:
    return getDeckById(deck_id)

# Main function to fetch and process the deck
def fetch_archidekt_deck(deck_id: int) -> Deck:
    deck = __fetch_archidekt_deck_unprocessed(deck_id)
    proc_deck = Deck(deck.id, deck.name, deck.owner.id, deck.owner.username, source="Archidekt")

    card_dict = {}

    for category in deck.categories:
        if category.name.lower() == "commander": # special handling for commanders
            proc_deck.commanders = [
                Card(card.card.uid, card.card.oracle_card.name, card.quantity)
                for card in category.cards]
            continue
        if category.name.lower() in BLACKLISTED_CATEGORIES: # skip anything but the mainboard
            continue
        for card in category.cards:
            if card.categories and any(cat.lower() in BLACKLISTED_CATEGORIES for cat in card.categories):
                continue # double check, since some cards have multiple categories (including maybeboard/sideboard)
            card_dict[card.card.uid] = Card(card.card.uid, card.card.oracle_card.name, card.quantity)
    
    # convert the set to a list for better usability
    proc_deck.library = list(card_dict.values())

    return proc_deck

if __name__ == "__main__":
    deck = fetch_archidekt_deck(18053512)
    print(deck)
