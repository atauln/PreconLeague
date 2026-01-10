"""Shared pytest fixtures and configuration"""
import pytest
import sys
import os

# Add the api directory to sys.path for all tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))


@pytest.fixture
def sample_user():
    """Fixture providing sample user data"""
    return {
        'user_id': 1,
        'user_name': 'testuser'
    }


@pytest.fixture
def sample_deck():
    """Fixture providing sample deck data"""
    return {
        'deck_id': 1,
        'user_id': 1,
        'deck_name': 'Test Deck',
        'source': 'moxfield',
        'moxfield_deck_url': 'https://moxfield.com/decks/test123'
    }


@pytest.fixture
def sample_card():
    """Fixture providing sample card data"""
    return {
        'oracle_card_id': 'oracle123',
        'card_name': 'Lightning Bolt'
    }


@pytest.fixture
def sample_snapshot():
    """Fixture providing sample snapshot data"""
    return {
        'snapshot_id': 1,
        'deck_id': 1,
        'commander_id': 'oracle_commander',
        'salt_rating': 2.5,
        'synergy_rating': 7.8,
        'power_level_rating': 6.5,
        'threat_rating': 5.5,
        'bracket_rating': 3.0,
        'overall_rating': 7.0,
        'manabase_score': 8.2,
        'power_level_display_value': 7,
        'combo_rating': 4.5,
        'archetype_minor': 'Voltron',
        'archetype_major': 'Aggro',
        'price_usd': 250.50
    }
