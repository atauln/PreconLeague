import requests
from mtg_parser import parse_deck

def get_moxfield_deck(deck_id: int) -> dict:
    """Fetch a deck from Moxfield by its ID and parse it into a structured format."""
    url = f"https://moxfield.com/decks/{deck_id}"
    return parse_deck(url, requests.Session())

if __name__ == "__main__":
    deck_id = "IzO5BX0e5UOKO4shiChTXA"  # Example Moxfield deck ID
    deck = get_moxfield_deck(deck_id)
    for card in deck:
        print(card)