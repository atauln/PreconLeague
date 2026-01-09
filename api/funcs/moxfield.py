import requests

from funcs.models import Deck, Card

MOXFIELD_BASE_EXPORT_URL = "https://api2.moxfield.com/v3/decks/all/"


def __fetch_moxfield_deck_unprocessed(deck_id: str) -> dict:
    """Fetch a deck from Moxfield by its deck ID."""
    url = f"{MOXFIELD_BASE_EXPORT_URL}{deck_id}"
    headers = {  # Moxfield API requires a User-Agent header
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()

def fetch_moxfield_deck(deck_id: str) -> Deck:
    deck = __fetch_moxfield_deck_unprocessed(deck_id)
    deck_obj = Deck(
        deck_id=deck.get("publicId"),
        name=deck.get("name"),
        owner_id=deck.get("createdByUser", {}).get("userName", "Unknown"),
        owner_name=deck.get("createdByUser", {}).get("displayName", "Unknown"),
        source="Moxfield",
    )

    for _, card_wrap in deck.get("boards").get("commanders").get("cards").items():
        card = card_wrap.get("card")
        card_obj = Card(
            card_id=card.get("scryfall_id"),
            name=card.get("name"),
            quantity=card_wrap.get("quantity", 0)
        )
        deck_obj.commanders.append(card_obj)

    for _, card_wrap in deck.get("boards").get("mainboard").get("cards").items():
        card = card_wrap.get("card")
        card_obj = Card(
            card_id=card.get("scryfall_id"),
            name=card.get("name"),
            quantity=card_wrap.get("quantity", 0)
        )
        deck_obj.library.append(card_obj)
    
    return deck_obj

if __name__ == "__main__":
    # Example usage
    deck_id = "IzO5BX0e5UOKO4shiChTXA"
    deck_data = fetch_moxfield_deck(deck_id)
    print(deck_data)