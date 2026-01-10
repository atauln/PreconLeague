from pyrchidekt.api import getDeckById

deck = getDeckById(18053512)
print([c.name for c in deck.categories])