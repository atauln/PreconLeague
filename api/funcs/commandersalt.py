import requests
from .models import CommanderSaltData

BASE_URL = "https://api.commandersalt.com/decks"

def __fetch_commandersalt_deck_data(deck_url: str) -> dict:
    """Return data for a deck from commandersalt given its URL."""
    url = f"{BASE_URL}?url={deck_url}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": "https://www.commandersalt.com/",
        "Origin": "https://www.commandersalt.com",
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_commandersalt_deck_data(deck_url: str) -> dict:
    """Public function to fetch deck data from Commandersalt."""
    data = __fetch_commandersalt_deck_data(deck_url)
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
    return CommanderSaltData(**proc_data)

if __name__ == "__main__":
    # Example usage
    deck_url = "https://archidekt.com/decks/18053512/anikthea_precon_league"
    deck_data = fetch_commandersalt_deck_data(deck_url)
    print(deck_data)
