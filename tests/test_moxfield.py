"""Unit tests for Moxfield integration"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the api directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from funcs.moxfield import fetch_moxfield_deck, MOXFIELD_BASE_EXPORT_URL


class TestMoxfieldFetchDeck:
    """Tests for Moxfield deck fetching"""
    
    def test_fetch_moxfield_deck_success(self):
        """Test successful fetch from Moxfield"""
        mock_response_data = {
            'publicId': 'test123',
            'name': 'Test Deck',
            'createdByUser': {
                'userName': 'testuser',
                'displayName': 'Test User'
            },
            'boards': {
                'commanders': {
                    'cards': {
                        'card1': {
                            'card': {
                                'scryfall_id': 'scryfall123',
                                'name': 'Test Commander'
                            },
                            'quantity': 1
                        }
                    }
                },
                'mainboard': {
                    'cards': {
                        'card2': {
                            'card': {
                                'scryfall_id': 'scryfall456',
                                'name': 'Test Card'
                            },
                            'quantity': 2
                        }
                    }
                }
            }
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        
        with patch('funcs.moxfield.requests.get', return_value=mock_response):
            deck = fetch_moxfield_deck('https://moxfield.com/decks/test123')
            
            assert deck.id == 'test123'
            assert deck.name == 'Test Deck'
            assert deck.owner_id == 'testuser'
            assert deck.owner_name == 'Test User'
            assert deck.source == 'Moxfield'
            assert len(deck.commanders) == 1
            assert len(deck.library) == 1
    
    def test_fetch_moxfield_deck_with_missing_user_data(self):
        """Test fetch when user data is missing"""
        mock_response_data = {
            'publicId': 'test456',
            'name': 'Deck No User',
            'boards': {
                'commanders': {
                    'cards': {}
                },
                'mainboard': {
                    'cards': {}
                }
            }
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        
        with patch('funcs.moxfield.requests.get', return_value=mock_response):
            deck = fetch_moxfield_deck('https://moxfield.com/decks/test456')
            
            assert deck.owner_id == 'Unknown'
            assert deck.owner_name == 'Unknown'
    
    def test_fetch_moxfield_deck_extracts_deck_id(self):
        """Test that deck ID is correctly extracted from URL"""
        mock_response_data = {
            'publicId': 'extractedId',
            'name': 'Extract Test',
            'createdByUser': {'userName': 'user', 'displayName': 'User'},
            'boards': {
                'commanders': {'cards': {}},
                'mainboard': {'cards': {}}
            }
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        
        with patch('funcs.moxfield.requests.get', return_value=mock_response) as mock_get:
            fetch_moxfield_deck('https://moxfield.com/decks/extractedId')
            
            # Verify the correct URL was called
            called_url = mock_get.call_args[0][0]
            assert 'extractedId' in called_url
            assert MOXFIELD_BASE_EXPORT_URL in called_url
    
    def test_fetch_moxfield_deck_http_error(self):
        """Test handling of HTTP errors"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        
        with patch('funcs.moxfield.requests.get', return_value=mock_response):
            with pytest.raises(Exception, match="HTTP Error"):
                fetch_moxfield_deck('https://moxfield.com/decks/error123')
    
    def test_fetch_moxfield_deck_user_agent_header(self):
        """Test that User-Agent header is included"""
        mock_response_data = {
            'publicId': 'ua_test',
            'name': 'UA Test',
            'createdByUser': {'userName': 'user', 'displayName': 'User'},
            'boards': {
                'commanders': {'cards': {}},
                'mainboard': {'cards': {}}
            }
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        
        with patch('funcs.moxfield.requests.get', return_value=mock_response) as mock_get:
            fetch_moxfield_deck('https://moxfield.com/decks/ua_test')
            
            # Verify User-Agent header was set
            call_headers = mock_get.call_args[1]['headers']
            assert 'User-Agent' in call_headers
