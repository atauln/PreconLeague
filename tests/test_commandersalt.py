"""Unit tests for CommanderSalt integration"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the api directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from funcs.commandersalt import fetch_commandersalt_deck_data, BASE_URL


class TestCommanderSaltFetchData:
    """Tests for CommanderSalt data fetching"""
    
    def test_fetch_commandersalt_deck_data_success(self):
        """Test successful fetch from CommanderSalt"""
        mock_response_data = {
            'saltRating': 2.5,
            'synergyRating': 7.8,
            'powerLevelRating': 6.5,
            'threatRating': 5.5,
            'bracketRating': 3.0,
            'overallRating': 7.0,
            'powerLevelDisplayValue': 7,
            'comboRating': 4.5,
            'archetypeMinor': 'Voltron',
            'archetypeMajor': 'Aggro',
            'details': {
                'manabase': {
                    'score': 8.2
                }
            },
            'price': {
                'usd': 250.50
            }
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        
        with patch('funcs.commandersalt.requests.post', return_value=mock_response):
            result = fetch_commandersalt_deck_data('https://archidekt.com/decks/123')
            
            assert result.salt_rating == 2.5
            assert result.synergy_rating == 7.8
            assert result.power_level_rating == 6.5
            assert result.threat_rating == 5.5
            assert result.bracket_rating == 3.0
            assert result.overall_rating == 7.0
            assert result.manabase_score == 8.2
            assert result.power_level_display_value == 7
            assert result.combo_rating == 4.5
            assert result.archetype_minor == 'Voltron'
            assert result.archetype_major == 'Aggro'
            assert result.price_usd == 250.50
    
    def test_fetch_commandersalt_deck_data_url_parameter(self):
        """Test that URL is correctly passed as parameter"""
        mock_response_data = {
            'saltRating': 1.0,
            'synergyRating': 1.0,
            'powerLevelRating': 1.0,
            'threatRating': 1.0,
            'bracketRating': 1.0,
            'overallRating': 1.0,
            'powerLevelDisplayValue': 1,
            'comboRating': 1.0,
            'archetypeMinor': 'Test',
            'archetypeMajor': 'Test',
            'details': {'manabase': {'score': 1.0}},
            'price': {'usd': 1.0}
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        
        test_url = 'https://moxfield.com/decks/test123'
        
        with patch('funcs.commandersalt.requests.post', return_value=mock_response) as mock_post:
            fetch_commandersalt_deck_data(test_url)
            
            # Verify the URL was called correctly
            called_url = mock_post.call_args[0][0]
            assert BASE_URL in called_url
            assert f'url={test_url}' in called_url
    
    def test_fetch_commandersalt_deck_data_headers(self):
        """Test that proper headers are included"""
        mock_response_data = {
            'saltRating': 1.0,
            'synergyRating': 1.0,
            'powerLevelRating': 1.0,
            'threatRating': 1.0,
            'bracketRating': 1.0,
            'overallRating': 1.0,
            'powerLevelDisplayValue': 1,
            'comboRating': 1.0,
            'archetypeMinor': 'Test',
            'archetypeMajor': 'Test',
            'details': {'manabase': {'score': 1.0}},
            'price': {'usd': 1.0}
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        
        with patch('funcs.commandersalt.requests.post', return_value=mock_response) as mock_post:
            fetch_commandersalt_deck_data('https://archidekt.com/decks/123')
            
            # Verify headers were set
            call_headers = mock_post.call_args[1]['headers']
            assert 'User-Agent' in call_headers
            assert 'Content-Type' in call_headers
            assert 'application/json' in call_headers['Content-Type']
            assert 'Referer' in call_headers
            assert 'Origin' in call_headers
    
    def test_fetch_commandersalt_deck_data_http_error(self):
        """Test handling of HTTP errors"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        
        with patch('funcs.commandersalt.requests.post', return_value=mock_response):
            with pytest.raises(Exception, match="API Error"):
                fetch_commandersalt_deck_data('https://archidekt.com/decks/error')
    
    def test_fetch_commandersalt_deck_data_type_conversion(self):
        """Test that values are converted to correct types"""
        mock_response_data = {
            'saltRating': '2.5',  # String that should be converted to float
            'synergyRating': '7.8',
            'powerLevelRating': '6.5',
            'threatRating': '5.5',
            'bracketRating': '3.0',
            'overallRating': '7.0',
            'powerLevelDisplayValue': '7',  # String that should be converted to int
            'comboRating': '4.5',
            'archetypeMinor': 'Voltron',
            'archetypeMajor': 'Aggro',
            'details': {
                'manabase': {
                    'score': '8.2'
                }
            },
            'price': {
                'usd': '250.50'
            }
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        
        with patch('funcs.commandersalt.requests.post', return_value=mock_response):
            result = fetch_commandersalt_deck_data('https://archidekt.com/decks/123')
            
            # Verify types are correct
            assert isinstance(result.salt_rating, float)
            assert isinstance(result.power_level_display_value, int)
            assert isinstance(result.price_usd, float)
