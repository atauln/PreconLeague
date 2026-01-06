from pyrchidekt.api import getDeckById
from pprint import pprint



deck = getDeckById(18053512)
pprint(vars(deck), indent=2, depth=3, sort_dicts=False)
# for category in deck.categories:
#     print(f"Category: {category.name}")
#     for card in category.cards:
#         print(f" - Card: {card.card.oracle_card.name} (ID: {card.id})")