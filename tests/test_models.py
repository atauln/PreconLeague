"""Unit tests for the models in api/funcs/models.py"""
import pytest
import sys
import os

# Add the api directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from funcs.models import Card, Deck, CommanderSaltData


class TestCard:
    """Tests for the Card model"""
    
    def test_card_initialization(self):
        """Test Card object initialization"""
        card = Card("card123", "Lightning Bolt", 4)
        assert card.id == "card123"
        assert card.name == "Lightning Bolt"
        assert card.quantity == 4
    
    def test_card_repr(self):
        """Test Card string representation"""
        card = Card("card456", "Counterspell", 2)
        expected = "Card(id='card456', name='Counterspell', quantity=2)"
        assert repr(card) == expected


class TestDeck:
    """Tests for the Deck model"""
    
    def test_deck_initialization(self):
        """Test Deck object initialization"""
        deck = Deck("deck001", "My EDH Deck", "user123", "TestUser", "Moxfield")
        assert deck.id == "deck001"
        assert deck.name == "My EDH Deck"
        assert deck.owner_id == "user123"
        assert deck.owner_name == "TestUser"
        assert deck.source == "Moxfield"
        assert deck.library == []
        assert deck.commanders == []
    
    def test_deck_library_size_empty(self):
        """Test library size calculation with empty deck"""
        deck = Deck("deck002", "Empty Deck", "user456", "Player", "Archidekt")
        assert deck.library_size() == 0
    
    def test_deck_library_size_with_cards(self):
        """Test library size calculation with cards"""
        deck = Deck("deck003", "Full Deck", "user789", "Commander", "Moxfield")
        deck.commanders = [Card("cmd1", "Atraxa", 1)]
        deck.library = [
            Card("card1", "Sol Ring", 1),
            Card("card2", "Command Tower", 1),
            Card("card3", "Island", 10),
        ]
        assert deck.library_size() == 13  # 1 commander + 12 library cards
    
    def test_deck_library_size_multiple_commanders(self):
        """Test library size with multiple commanders (partner)"""
        deck = Deck("deck004", "Partner Deck", "user000", "PartnerPlayer", "Archidekt")
        deck.commanders = [
            Card("cmd1", "Thrasios", 1),
            Card("cmd2", "Tymna", 1)
        ]
        deck.library = [Card("card1", "Sol Ring", 1)]
        assert deck.library_size() == 3  # 2 commanders + 1 library card
    
    def test_deck_repr(self):
        """Test Deck string representation"""
        deck = Deck("deck005", "Test Deck", "user111", "TestOwner", "Moxfield")
        deck.commanders = [Card("cmd1", "Yuriko", 1)]
        deck.library = [Card("card1", "Island", 20)]
        repr_str = repr(deck)
        assert "deck005" in repr_str
        assert "Test Deck" in repr_str
        assert "user111" in repr_str
        assert "TestOwner" in repr_str
        assert "Moxfield" in repr_str


class TestCommanderSaltData:
    """Tests for the CommanderSaltData model"""
    
    def test_commandersalt_initialization(self):
        """Test CommanderSaltData initialization with all fields"""
        data = CommanderSaltData(
            salt_rating=2.5,
            synergy_rating=7.8,
            power_level_rating=6.5,
            threat_rating=5.5,
            bracket_rating=3.0,
            overall_rating=7.0,
            manabase_score=8.2,
            power_level_display_value=7,
            combo_rating=4.5,
            archetype_minor="Voltron",
            archetype_major="Aggro",
            price_usd=250.50
        )
        
        assert data.salt_rating == 2.5
        assert data.synergy_rating == 7.8
        assert data.power_level_rating == 6.5
        assert data.threat_rating == 5.5
        assert data.bracket_rating == 3.0
        assert data.overall_rating == 7.0
        assert data.manabase_score == 8.2
        assert data.power_level_display_value == 7
        assert data.combo_rating == 4.5
        assert data.archetype_minor == "Voltron"
        assert data.archetype_major == "Aggro"
        assert data.price_usd == 250.50
    
    def test_commandersalt_repr(self):
        """Test CommanderSaltData string representation"""
        data = CommanderSaltData(
            salt_rating=1.0,
            synergy_rating=2.0,
            power_level_rating=3.0,
            threat_rating=4.0,
            bracket_rating=5.0,
            overall_rating=6.0,
            manabase_score=7.0,
            power_level_display_value=8,
            combo_rating=9.0,
            archetype_minor="Combo",
            archetype_major="Control",
            price_usd=100.0
        )
        repr_str = repr(data)
        assert "salt_rating=1.0" in repr_str
        assert "archetype_minor='Combo'" in repr_str
        assert "price_usd=100.0" in repr_str
