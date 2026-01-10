"""Unit tests for API routers"""
import pytest
import sys
import os
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

# Add the api directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from routers import users, decks, snapshots, cards


@pytest.mark.asyncio
class TestUsersRouter:
    """Tests for users router endpoints"""
    
    async def test_read_user_success(self):
        """Test successful user retrieval"""
        mock_user = {'user_id': 1, 'user_name': 'testuser'}
        
        with patch('routers.users.get_user_by_id', return_value=mock_user):
            result = await users.read_user(1)
            
            assert result == mock_user
    
    async def test_read_user_not_found(self):
        """Test user not found scenario"""
        with patch('routers.users.get_user_by_id', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await users.read_user(999)
            
            assert exc_info.value.status_code == 404
            assert "User not found" in str(exc_info.value.detail)
    
    async def test_read_all_users_success(self):
        """Test retrieving all users"""
        mock_users = [
            {'user_id': 1, 'user_name': 'user1'},
            {'user_id': 2, 'user_name': 'user2'}
        ]
        
        with patch('routers.users.get_all_users', return_value=mock_users):
            result = await users.read_all_users()
            
            assert result == mock_users
            assert len(result) == 2
    
    async def test_read_all_users_empty(self):
        """Test retrieving all users when none exist"""
        with patch('routers.users.get_all_users', return_value=[]):
            with pytest.raises(HTTPException) as exc_info:
                await users.read_all_users()
            
            assert exc_info.value.status_code == 404
    
    async def test_register_user_success(self):
        """Test successful user registration"""
        user_data = {'user_name': 'newuser'}
        
        with patch('routers.users.create_user', return_value=123):
            result = await users.register_user(user_data)
            
            assert result['user_id'] == 123
            assert result['user_name'] == 'newuser'
    
    async def test_register_user_missing_name(self):
        """Test user registration with missing username"""
        user_data = {}
        
        with pytest.raises(HTTPException) as exc_info:
            await users.register_user(user_data)
        
        assert exc_info.value.status_code == 400
        assert "user_name is required" in str(exc_info.value.detail)
    
    async def test_register_user_failure(self):
        """Test user registration failure"""
        user_data = {'user_name': 'faileduser'}
        
        with patch('routers.users.create_user', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await users.register_user(user_data)
            
            assert exc_info.value.status_code == 500


@pytest.mark.asyncio
class TestDecksRouter:
    """Tests for decks router endpoints"""
    
    async def test_read_deck_success(self):
        """Test successful deck retrieval"""
        mock_deck = {'deck_id': 1, 'deck_name': 'Test Deck'}
        
        with patch('routers.decks.get_deck_by_id', return_value=mock_deck):
            result = await decks.read_deck(1)
            
            assert result == mock_deck
    
    async def test_read_deck_not_found(self):
        """Test deck not found scenario"""
        with patch('routers.decks.get_deck_by_id', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await decks.read_deck(999)
            
            assert exc_info.value.status_code == 404
            assert "Deck not found" in str(exc_info.value.detail)
    
    async def test_read_all_decks_success(self):
        """Test retrieving all decks"""
        mock_decks = [
            {'deck_id': 1, 'deck_name': 'Deck 1'},
            {'deck_id': 2, 'deck_name': 'Deck 2'}
        ]
        
        with patch('routers.decks.get_all_decks', return_value=mock_decks):
            result = await decks.read_all_decks()
            
            assert result == mock_decks
            assert len(result) == 2
    
    async def test_read_user_decks_success(self):
        """Test retrieving decks for a specific user"""
        mock_decks = [{'deck_id': 1, 'user_id': 1, 'deck_name': 'User Deck'}]
        
        with patch('routers.decks.get_user_decks', return_value=mock_decks):
            result = await decks.read_user_decks(1)
            
            assert result == mock_decks
    
    async def test_read_user_decks_not_found(self):
        """Test retrieving decks when user has none"""
        with patch('routers.decks.get_user_decks', return_value=[]):
            with pytest.raises(HTTPException) as exc_info:
                await decks.read_user_decks(999)
            
            assert exc_info.value.status_code == 404


@pytest.mark.asyncio
class TestCardsRouter:
    """Tests for cards router endpoints"""
    
    async def test_read_card_success(self):
        """Test successful card retrieval"""
        mock_card = {'card_id': 'oracle123', 'card_name': 'Lightning Bolt'}
        
        with patch('routers.cards.get_card_by_id', return_value=mock_card):
            result = await cards.read_card(1)
            
            assert result == mock_card
    
    async def test_read_card_not_found(self):
        """Test card not found scenario"""
        with patch('routers.cards.get_card_by_id', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await cards.read_card(999)
            
            assert exc_info.value.status_code == 404
    
    async def test_read_all_cards_success(self):
        """Test retrieving all cards"""
        mock_cards = [
            {'card_id': 'oracle1', 'card_name': 'Card 1'},
            {'card_id': 'oracle2', 'card_name': 'Card 2'}
        ]
        
        with patch('routers.cards.get_all_cards', return_value=mock_cards):
            result = await cards.read_all_cards()
            
            assert result == mock_cards


@pytest.mark.asyncio
class TestSnapshotsRouter:
    """Tests for snapshots router endpoints"""
    
    async def test_read_snapshot_success(self):
        """Test successful snapshot retrieval"""
        mock_snapshot = {'snapshot_id': 1, 'deck_id': 1}
        
        with patch('routers.snapshots.get_snapshot_by_id', return_value=mock_snapshot):
            result = await snapshots.read_snapshot(1)
            
            assert result == mock_snapshot
    
    async def test_read_snapshot_not_found(self):
        """Test snapshot not found scenario"""
        with patch('routers.snapshots.get_snapshot_by_id', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await snapshots.read_snapshot(999)
            
            assert exc_info.value.status_code == 404
    
    async def test_read_all_snapshots_success(self):
        """Test retrieving all snapshots"""
        mock_snapshots = [
            {'snapshot_id': 1, 'deck_id': 1},
            {'snapshot_id': 2, 'deck_id': 2}
        ]
        
        with patch('routers.snapshots.get_all_snapshots', return_value=mock_snapshots):
            result = await snapshots.read_all_snapshots()
            
            assert result == mock_snapshots
    
    async def test_read_deck_snapshots_success(self):
        """Test retrieving snapshots for a specific deck"""
        mock_snapshots = [{'snapshot_id': 1, 'deck_id': 1}]
        
        with patch('routers.snapshots.get_deck_snapshots', return_value=mock_snapshots):
            result = await snapshots.read_deck_snapshots(1)
            
            assert result == mock_snapshots
    
    async def test_read_snapshot_with_library_success(self):
        """Test retrieving snapshot with library cards"""
        mock_snapshot = {
            'snapshot_id': 1, 
            'deck_id': 1,
            'library_cards': [{'card_id': 'oracle1', 'card_name': 'Sol Ring'}]
        }
        
        with patch('routers.snapshots.get_snapshot_with_library', return_value=mock_snapshot):
            result = await snapshots.read_snapshot_with_library(1)
            
            assert result == mock_snapshot
            assert 'library_cards' in result
