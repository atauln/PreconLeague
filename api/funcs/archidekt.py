from urllib.parse import urlparse

from pyrchidekt.api import getDeckById
from pyrchidekt.deck import Deck as pDeck
from .models import Deck, Card

# Categories to ignore when processing the deck
BLACKLISTED_CATEGORIES = [
    "maybeboard",
    "sideboard",
]


def __extract_deck_id(deck_url: str) -> int:
    """
    Extract the deck id from an Archidekt deck URL.
    Example: https://archidekt.com/decks/18053512/anikthea_precon_league -> 18053512
    """
    path_parts = urlparse(deck_url).path.strip("/").split("/")
    if not path_parts or not path_parts[1].isdigit():
        raise ValueError(f"Could not extract deck id from URL: {deck_url}")
    return int(path_parts[1])


# Internal function to fetch the deck without processing
def __fetch_archidekt_deck_unprocessed(deck_url: str) -> pDeck:
    deck_id = __extract_deck_id(deck_url)
    return getDeckById(deck_id)


# Main function to fetch and process the deck
def fetch_archidekt_deck(deck_url: str) -> Deck:
    deck = __fetch_archidekt_deck_unprocessed(deck_url)
    proc_deck = Deck(deck.id, deck.name, deck.owner.id, deck.owner.username, source="Archidekt")

    card_dict = {}

    for category in deck.categories:
        if category.name.lower() == "commander":  # special handling for commanders
            proc_deck.commanders = [
                Card(card.card.uid, card.card.oracle_card.name, card.quantity) for card in category.cards
            ]
            continue
        if category.name.lower() in BLACKLISTED_CATEGORIES:  # skip anything but the mainboard
            continue
        for card in category.cards:
            if card.categories and any(cat.lower() in BLACKLISTED_CATEGORIES for cat in card.categories):
                continue  # double check, since some cards have multiple categories (including maybeboard/sideboard)
            card_dict[card.card.uid] = Card(card.card.uid, card.card.oracle_card.name, card.quantity)

    # convert the set to a list for better usability
    proc_deck.library = list(card_dict.values())

    return proc_deck


if __name__ == "__main__":
    archidekt_url = "https://archidekt.com/decks/18053512/anikthea_precon_league"
    deck = fetch_archidekt_deck(archidekt_url)
    print(deck)
