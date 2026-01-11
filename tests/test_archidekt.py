"""Unit tests for api/funcs/archidekt.py"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the api directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

# Import the module to access functions
import funcs.archidekt as archidekt_module
from funcs.archidekt import fetch_archidekt_deck


class TestArchidektExtractDeckId:
    """Tests for extracting deck ID from URLs"""
    
    def test_extract_deck_id_valid_url(self):
        """Test extracting deck ID from a valid Archidekt URL"""
        # Access the private function directly from module dict
        extract_func = archidekt_module.__dict__['__extract_deck_id']
        url = "https://archidekt.com/decks/18053512/anikthea_precon_league"
        deck_id = extract_func(url)
        assert deck_id == 18053512
    
    def test_extract_deck_id_simple_url(self):
        """Test extracting deck ID from a simple URL format"""
        extract_func = archidekt_module.__dict__['__extract_deck_id']
        url = "https://archidekt.com/decks/12345/my-deck"
        deck_id = extract_func(url)
        assert deck_id == 12345
    
    def test_extract_deck_id_no_trailing_slash(self):
        """Test extracting deck ID from URL without trailing slash"""
        extract_func = archidekt_module.__dict__['__extract_deck_id']
        url = "https://archidekt.com/decks/99999/test-deck"
        deck_id = extract_func(url)
        assert deck_id == 99999
    
    def test_extract_deck_id_with_trailing_slash(self):
        """Test extracting deck ID from URL with trailing slash"""
        extract_func = archidekt_module.__dict__['__extract_deck_id']
        url = "https://archidekt.com/decks/54321/another-deck/"
        deck_id = extract_func(url)
        assert deck_id == 54321
    
    def test_extract_deck_id_invalid_url_raises_error(self):
        """Test that invalid URL raises ValueError"""
        extract_func = archidekt_module.__dict__['__extract_deck_id']
        invalid_url = "https://archidekt.com/invalid/path"
        with pytest.raises(ValueError, match="Could not extract deck id from URL"):
            extract_func(invalid_url)
    
    def test_extract_deck_id_non_numeric_raises_error(self):
        """Test that non-numeric deck ID raises ValueError"""
        extract_func = archidekt_module.__dict__['__extract_deck_id']
        invalid_url = "https://archidekt.com/decks/notanumber/deck-name"
        with pytest.raises(ValueError, match="Could not extract deck id from URL"):
            extract_func(invalid_url)


class TestArchidektFetchDeck:
    """Tests for fetching Archidekt decks"""
    
    def test_fetch_archidekt_deck_success(self):
        """Test successful fetch from Archidekt"""
        # Create mock deck data
        mock_commander_card = MagicMock()
        mock_commander_card.card.uid = 'commander123'
        mock_commander_card.card.oracle_card.name = 'Test Commander'
        mock_commander_card.quantity = 1
        mock_commander_card.categories = None
        
        mock_library_card = MagicMock()
        mock_library_card.card.uid = 'card456'
        mock_library_card.card.oracle_card.name = 'Test Card'
        mock_library_card.quantity = 2
        mock_library_card.categories = None
        
        mock_commander_category = MagicMock()
        mock_commander_category.name = 'Commander'
        mock_commander_category.cards = [mock_commander_card]
        
        mock_mainboard_category = MagicMock()
        mock_mainboard_category.name = 'Mainboard'
        mock_mainboard_category.cards = [mock_library_card]
        
        mock_deck = MagicMock()
        mock_deck.id = 123456
        mock_deck.name = 'Test Deck'
        mock_deck.owner.id = 'owner123'
        mock_deck.owner.username = 'testuser'
        mock_deck.categories = [mock_commander_category, mock_mainboard_category]
        
        with patch('funcs.archidekt.getDeckById', return_value=mock_deck):
            deck = fetch_archidekt_deck('https://archidekt.com/decks/123456/test-deck')
            
            assert deck.id == 123456
            assert deck.name == 'Test Deck'
            assert deck.owner_id == 'owner123'
            assert deck.owner_name == 'testuser'
            assert deck.source == 'Archidekt'
            assert len(deck.commanders) == 1
            assert len(deck.library) == 1
    
    def test_fetch_archidekt_deck_filters_maybeboard(self):
        """Test that maybeboard cards are filtered out"""
        mock_card = MagicMock()
        mock_card.card.uid = 'card789'
        mock_card.card.oracle_card.name = 'Maybe Card'
        mock_card.quantity = 1
        mock_card.categories = None
        
        mock_commander_card = MagicMock()
        mock_commander_card.card.uid = 'commander123'
        mock_commander_card.card.oracle_card.name = 'Test Commander'
        mock_commander_card.quantity = 1
        mock_commander_card.categories = None
        
        mock_commander_category = MagicMock()
        mock_commander_category.name = 'Commander'
        mock_commander_category.cards = [mock_commander_card]
        
        mock_maybeboard_category = MagicMock()
        mock_maybeboard_category.name = 'Maybeboard'
        mock_maybeboard_category.cards = [mock_card]
        
        mock_deck = MagicMock()
        mock_deck.id = 123
        mock_deck.name = 'Filtered Deck'
        mock_deck.owner.id = 'owner'
        mock_deck.owner.username = 'user'
        mock_deck.categories = [mock_commander_category, mock_maybeboard_category]
        
        with patch('funcs.archidekt.getDeckById', return_value=mock_deck):
            deck = fetch_archidekt_deck('https://archidekt.com/decks/123/filtered')
            
            # Library should be empty (maybeboard filtered out)
            assert len(deck.library) == 0
    
    def test_fetch_archidekt_deck_filters_sideboard(self):
        """Test that sideboard cards are filtered out"""
        mock_card = MagicMock()
        mock_card.card.uid = 'card999'
        mock_card.card.oracle_card.name = 'Sideboard Card'
        mock_card.quantity = 1
        mock_card.categories = None
        
        mock_commander_card = MagicMock()
        mock_commander_card.card.uid = 'commander123'
        mock_commander_card.card.oracle_card.name = 'Test Commander'
        mock_commander_card.quantity = 1
        mock_commander_card.categories = None
        
        mock_commander_category = MagicMock()
        mock_commander_category.name = 'Commander'
        mock_commander_category.cards = [mock_commander_card]
        
        mock_sideboard_category = MagicMock()
        mock_sideboard_category.name = 'Sideboard'
        mock_sideboard_category.cards = [mock_card]
        
        mock_deck = MagicMock()
        mock_deck.id = 456
        mock_deck.name = 'Sideboard Deck'
        mock_deck.owner.id = 'owner'
        mock_deck.owner.username = 'user'
        mock_deck.categories = [mock_commander_category, mock_sideboard_category]
        
        with patch('funcs.archidekt.getDeckById', return_value=mock_deck):
            deck = fetch_archidekt_deck('https://archidekt.com/decks/456/sideboard')
            
            # Library should be empty (sideboard filtered out)
            assert len(deck.library) == 0
    
    def test_fetch_archidekt_deck_filters_cards_with_blacklisted_categories(self):
        """Test that cards with blacklisted categories are filtered"""
        mock_card_with_category = MagicMock()
        mock_card_with_category.card.uid = 'card111'
        mock_card_with_category.card.oracle_card.name = 'Double Category Card'
        mock_card_with_category.quantity = 1
        mock_card_with_category.categories = ['Mainboard', 'Maybeboard']
        
        mock_commander_card = MagicMock()
        mock_commander_card.card.uid = 'commander123'
        mock_commander_card.card.oracle_card.name = 'Test Commander'
        mock_commander_card.quantity = 1
        mock_commander_card.categories = None
        
        mock_commander_category = MagicMock()
        mock_commander_category.name = 'Commander'
        mock_commander_category.cards = [mock_commander_card]
        
        mock_mainboard_category = MagicMock()
        mock_mainboard_category.name = 'Mainboard'
        mock_mainboard_category.cards = [mock_card_with_category]
        
        mock_deck = MagicMock()
        mock_deck.id = 789
        mock_deck.name = 'Multi-Cat Deck'
        mock_deck.owner.id = 'owner'
        mock_deck.owner.username = 'user'
        mock_deck.categories = [mock_commander_category, mock_mainboard_category]
        
        with patch('funcs.archidekt.getDeckById', return_value=mock_deck):
            deck = fetch_archidekt_deck('https://archidekt.com/decks/789/multi')
            
            # Library should be empty (card has maybeboard in categories)
            assert len(deck.library) == 0
