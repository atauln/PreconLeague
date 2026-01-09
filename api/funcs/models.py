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
        total_quantity = sum(card.quantity for card in self.library)
        commander_quantity = sum(card.quantity for card in self.commanders)
        total_quantity += commander_quantity
        return total_quantity
    
    def __repr__(self):
        return (f"ProcDeck(id={self.id}, name='{self.name}', owner_id={self.owner_id}, "
                f"owner_name='{self.owner_name}', library_size={self.library_size()}, "
                f"commanders={self.commanders}, source='{self.source}')")
