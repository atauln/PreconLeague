from dataclasses import dataclass

@dataclass
class Decklist:
    commander: str
    cards: list[str]