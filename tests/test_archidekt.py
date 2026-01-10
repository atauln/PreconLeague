"""Unit tests for api/funcs/archidekt.py"""
import pytest
import sys
import os

# Add the api directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

# Import the module to access functions
import funcs.archidekt as archidekt_module


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
