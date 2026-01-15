import requests

from .models import Deck, Card

MOXFIELD_BASE_EXPORT_URL = "https://api2.moxfield.com/v3/decks/all/"

def __fetch_moxfield_deck_unprocessed(deck_url: str) -> dict:
    """Fetch a deck from Moxfield by its deck ID."""
    deck_id = deck_url.split("/")[-1]
    deck_url = f"{MOXFIELD_BASE_EXPORT_URL}{deck_id}"
    headers = {  # Moxfield API requires a User-Agent header
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(deck_url, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()

def fetch_moxfield_deck(deck_url: str) -> Deck:
    deck = __fetch_moxfield_deck_unprocessed(deck_url)
    deck_obj = Deck(
        deck_id=deck.get("publicId"),
        name=deck.get("name"),
        owner_id=deck.get("createdByUser", {}).get("userName", "Unknown"),
        owner_name=deck.get("createdByUser", {}).get("displayName", "Unknown"),
        source="Moxfield",
    )

    deck_obj.commanders = [
        Card(
            card_id=card_wrap.get("card").get("scryfall_id"),
            name=card_wrap.get("card").get("name"),
            quantity=card_wrap.get("quantity", 0)
        )
        for _, card_wrap in deck.get("boards").get("commanders").get("cards").items()
    ]

    deck_obj.library = [
        Card(
            card_id=card_wrap.get("card").get("scryfall_id"),
            name=card_wrap.get("card").get("name"),
            quantity=card_wrap.get("quantity", 0)
        )
        for _, card_wrap in deck.get("boards").get("mainboard").get("cards").items()
    ]
    
    return deck_obj

if __name__ == "__main__":
    # Example usage
    deck_data = fetch_moxfield_deck("https://moxfield.com/decks/zhU0jK8bnkeSMMk3dj0N9g")
    print(deck_data)
    print(deck_data.library)