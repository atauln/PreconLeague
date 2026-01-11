"""Unit tests for API routers"""
import pytest
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock
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


@pytest.mark.asyncio
class TestCardsRouterAdditional:
    """Additional tests for cards router endpoints"""
    
    async def test_create_new_card_with_dict(self):
        """Test creating a card with dict input"""
        card_data = {'card_id': 'oracle123', 'card_name': 'Test Card'}
        
        # create_card returns bool, but router should return card_id if successful
        with patch('routers.cards.create_card', return_value='oracle123'):
            result = await cards.create_new_card(card_data)
            
            assert result['card_id'] == 'oracle123'
            assert result['card_name'] == 'Test Card'
    
    async def test_create_new_card_with_pydantic_model(self):
        """Test creating a card with Pydantic model"""
        card_data = MagicMock()
        card_data.card_id = 'oracle456'
        card_data.card_name = 'Another Card'
        
        with patch('routers.cards.create_card', return_value='oracle456'):
            result = await cards.create_new_card(card_data)
            
            assert result['card_id'] == 'oracle456'
            assert result['card_name'] == 'Another Card'
    
    async def test_create_new_card_missing_card_id(self):
        """Test creating a card with missing card_id"""
        card_data = {'card_name': 'Incomplete Card'}
        
        with pytest.raises(HTTPException) as exc_info:
            await cards.create_new_card(card_data)
        
        assert exc_info.value.status_code == 400
        assert 'card_name and card_id are required' in str(exc_info.value.detail)
    
    async def test_create_new_card_missing_card_name(self):
        """Test creating a card with missing card_name"""
        card_data = {'card_id': 'oracle789'}
        
        with pytest.raises(HTTPException) as exc_info:
            await cards.create_new_card(card_data)
        
        assert exc_info.value.status_code == 400
    
    async def test_create_new_card_failure(self):
        """Test card creation failure"""
        card_data = {'card_id': 'oracle999', 'card_name': 'Failed Card'}
        
        with patch('routers.cards.create_card', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await cards.create_new_card(card_data)
            
            assert exc_info.value.status_code == 500
    
    async def test_associate_card_with_dict(self):
        """Test associating a card with dict input"""
        association_data = {'snapshot_id': 1, 'card_id': 'oracle123'}
        
        with patch('routers.cards.associate_card_with_snapshot', return_value=True):
            result = await cards.associate_card(association_data)
            
            assert 'message' in result
            assert 'successfully' in result['message']
    
    async def test_associate_card_with_pydantic_model(self):
        """Test associating a card with Pydantic model"""
        association_data = MagicMock()
        association_data.snapshot_id = 2
        association_data.card_id = 'oracle456'
        
        with patch('routers.cards.associate_card_with_snapshot', return_value=True):
            result = await cards.associate_card(association_data)
            
            assert 'message' in result
    
    async def test_associate_card_missing_snapshot_id(self):
        """Test associating card with missing snapshot_id"""
        association_data = {'card_id': 'oracle123'}
        
        with pytest.raises(HTTPException) as exc_info:
            await cards.associate_card(association_data)
        
        assert exc_info.value.status_code == 400
    
    async def test_associate_card_missing_card_id(self):
        """Test associating card with missing card_id"""
        association_data = {'snapshot_id': 1}
        
        with pytest.raises(HTTPException) as exc_info:
            await cards.associate_card(association_data)
        
        assert exc_info.value.status_code == 400
    
    async def test_associate_card_failure(self):
        """Test card association failure"""
        association_data = {'snapshot_id': 1, 'card_id': 'oracle123'}
        
        with patch('routers.cards.associate_card_with_snapshot', return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await cards.associate_card(association_data)
            
            assert exc_info.value.status_code == 500


@pytest.mark.asyncio
class TestDecksRouterAdditional:
    """Additional tests for decks router endpoints"""
    
    async def test_read_all_decks_not_found(self):
        """Test reading all decks when none exist"""
        with patch('routers.decks.get_all_decks', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await decks.read_all_decks()
            
            assert exc_info.value.status_code == 404
    
    async def test_register_deck_moxfield_already_exists(self):
        """Test registering a Moxfield deck that already exists"""
        request_data = MagicMock()
        request_data.source = 'moxfield'
        request_data.deck_url = 'https://moxfield.com/decks/existing123'
        
        with patch('routers.decks.find_deck_by_moxfield_url', return_value={'deck_id': 1}):
            with pytest.raises(HTTPException) as exc_info:
                await decks.register_deck(request_data)
            
            assert exc_info.value.status_code == 400
            assert 'already exists' in str(exc_info.value.detail)
    
    async def test_register_deck_archidekt_already_exists(self):
        """Test registering an Archidekt deck that already exists"""
        request_data = MagicMock()
        request_data.source = 'archidekt'
        request_data.deck_url = 'https://archidekt.com/decks/123/existing'
        
        with patch('routers.decks.find_deck_by_archidekt_url', return_value={'deck_id': 1}):
            with pytest.raises(HTTPException) as exc_info:
                await decks.register_deck(request_data)
            
            assert exc_info.value.status_code == 400
    
    async def test_register_deck_moxfield_new_user(self):
        """Test registering a Moxfield deck with a new user"""
        from funcs.models import Deck
        
        request_data = MagicMock()
        request_data.source = 'moxfield'
        request_data.deck_url = 'https://moxfield.com/decks/new123'
        
        mock_deck = Deck(
            deck_id='new123',
            name='New Deck',
            owner_id='newuser',
            owner_name='New User',
            source='Moxfield'
        )
        
        with patch('routers.decks.find_deck_by_moxfield_url', return_value=None), \
             patch('routers.decks.fetch_moxfield_deck', return_value=mock_deck), \
             patch('routers.decks.get_user_by_name', return_value=None), \
             patch('routers.decks.create_user', return_value=100), \
             patch('routers.decks.create_deck', return_value=200):
            
            result = await decks.register_deck(request_data)
            
            assert result.deck_id == 200
    
    async def test_register_deck_archidekt_existing_user(self):
        """Test registering an Archidekt deck with an existing user"""
        from funcs.models import Deck
        
        request_data = MagicMock()
        request_data.source = 'archidekt'
        request_data.deck_url = 'https://archidekt.com/decks/456/new-deck'
        
        mock_deck = Deck(
            deck_id=456,
            name='Archidekt Deck',
            owner_id='existinguser',
            owner_name='Existing User',
            source='Archidekt'
        )
        
        with patch('routers.decks.find_deck_by_archidekt_url', return_value=None), \
             patch('routers.decks.fetch_archidekt_deck', return_value=mock_deck), \
             patch('routers.decks.get_user_by_name', return_value={'user_id': 50}), \
             patch('routers.decks.create_deck', return_value=300):
            
            result = await decks.register_deck(request_data)
            
            assert result.deck_id == 300
    
    async def test_register_deck_create_user_failure(self):
        """Test registering a deck when user creation fails"""
        from funcs.models import Deck
        
        request_data = MagicMock()
        request_data.source = 'moxfield'
        request_data.deck_url = 'https://moxfield.com/decks/fail123'
        
        mock_deck = Deck(
            deck_id='fail123',
            name='Fail Deck',
            owner_id='failuser',
            owner_name='Fail User',
            source='Moxfield'
        )
        
        with patch('routers.decks.find_deck_by_moxfield_url', return_value=None), \
             patch('routers.decks.fetch_moxfield_deck', return_value=mock_deck), \
             patch('routers.decks.get_user_by_name', return_value=None), \
             patch('routers.decks.create_user', return_value=None):
            
            with pytest.raises(HTTPException) as exc_info:
                await decks.register_deck(request_data)
            
            assert exc_info.value.status_code == 500
    
    async def test_register_deck_create_deck_failure(self):
        """Test registering a deck when deck creation fails"""
        from funcs.models import Deck
        
        request_data = MagicMock()
        request_data.source = 'moxfield'
        request_data.deck_url = 'https://moxfield.com/decks/fail456'
        
        mock_deck = Deck(
            deck_id='fail456',
            name='Fail Deck',
            owner_id='user',
            owner_name='User',
            source='Moxfield'
        )
        
        with patch('routers.decks.find_deck_by_moxfield_url', return_value=None), \
             patch('routers.decks.fetch_moxfield_deck', return_value=mock_deck), \
             patch('routers.decks.get_user_by_name', return_value={'user_id': 1}), \
             patch('routers.decks.create_deck', return_value=None):
            
            with pytest.raises(HTTPException) as exc_info:
                await decks.register_deck(request_data)
            
            assert exc_info.value.status_code == 500
    
    async def test_read_most_recent_snapshot_success(self):
        """Test reading most recent snapshot for a deck"""
        mock_snapshot = {'snapshot_id': 1, 'deck_id': 1}
        
        with patch('routers.decks.get_most_recent_snapshot_for_deck', return_value=mock_snapshot):
            result = await decks.read_most_recent_snapshot(1)
            
            assert result == mock_snapshot
    
    async def test_read_most_recent_snapshot_not_found(self):
        """Test reading most recent snapshot when none exists"""
        with patch('routers.decks.get_most_recent_snapshot_for_deck', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await decks.read_most_recent_snapshot(1)
            
            assert exc_info.value.status_code == 404


@pytest.mark.asyncio
class TestSnapshotsRouterAdditional:
    """Additional tests for snapshots router endpoints"""
    
    async def test_create_new_snapshot_with_dict(self):
        """Test creating a snapshot with dict input"""
        snapshot_data = {'deck_id': 1, 'snapshot_name': 'Week 1'}
        
        with patch('routers.snapshots.create_snapshot', return_value=100):
            result = await snapshots.create_new_snapshot(snapshot_data)
            
            assert result['snapshot_id'] == 100
            assert result['snapshot_name'] == 'Week 1'
            assert result['deck_id'] == 1
    
    async def test_create_new_snapshot_with_pydantic_model(self):
        """Test creating a snapshot with Pydantic model"""
        snapshot_data = MagicMock()
        snapshot_data.deck_id = 2
        snapshot_data.snapshot_name = 'Week 2'
        
        with patch('routers.snapshots.create_snapshot', return_value=200):
            result = await snapshots.create_new_snapshot(snapshot_data)
            
            assert result['snapshot_id'] == 200
    
    async def test_create_new_snapshot_missing_deck_id(self):
        """Test creating a snapshot with missing deck_id"""
        snapshot_data = {'snapshot_name': 'Incomplete'}
        
        with pytest.raises(HTTPException) as exc_info:
            await snapshots.create_new_snapshot(snapshot_data)
        
        assert exc_info.value.status_code == 400
    
    async def test_create_new_snapshot_missing_snapshot_name(self):
        """Test creating a snapshot with missing snapshot_name"""
        snapshot_data = {'deck_id': 1}
        
        with pytest.raises(HTTPException) as exc_info:
            await snapshots.create_new_snapshot(snapshot_data)
        
        assert exc_info.value.status_code == 400
    
    async def test_create_new_snapshot_failure(self):
        """Test snapshot creation failure"""
        snapshot_data = {'deck_id': 1, 'snapshot_name': 'Failed'}
        
        with patch('routers.snapshots.create_snapshot', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await snapshots.create_new_snapshot(snapshot_data)
            
            assert exc_info.value.status_code == 500
    
    async def test_trigger_create_snapshot_deck_not_found(self):
        """Test triggering snapshot creation when deck doesn't exist"""
        with patch('routers.snapshots.get_deck_by_id', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await snapshots.trigger_create_snapshot(999)
            
            assert exc_info.value.status_code == 404
    
    async def test_trigger_create_snapshot_invalid_source(self):
        """Test triggering snapshot creation with invalid source"""
        mock_deck = {'deck_id': 1, 'source': 'invalid'}
        
        with patch('routers.snapshots.get_deck_by_id', return_value=mock_deck):
            with pytest.raises(HTTPException) as exc_info:
                await snapshots.trigger_create_snapshot(1)
            
            assert exc_info.value.status_code == 400
    
    async def test_trigger_create_snapshot_no_commanders(self):
        """Test triggering snapshot creation with no commanders"""
        from funcs.models import Deck
        
        mock_deck = {
            'deck_id': 1,
            'source': 'moxfield',
            'moxfield_deck_url': 'https://moxfield.com/decks/test123'
        }
        
        mock_proc_deck = Deck(
            deck_id='test123',
            name='No Commander Deck',
            owner_id='user',
            owner_name='User',
            source='Moxfield'
        )
        mock_proc_deck.commanders = []
        
        mock_cs_data = MagicMock()
        
        with patch('routers.snapshots.get_deck_by_id', return_value=mock_deck), \
             patch('routers.snapshots.fetch_moxfield_deck', return_value=mock_proc_deck), \
             patch('routers.snapshots.fetch_commandersalt_deck_data', return_value=mock_cs_data):
            
            with pytest.raises(HTTPException) as exc_info:
                await snapshots.trigger_create_snapshot(1)
            
            assert exc_info.value.status_code == 400
    
    async def test_trigger_create_snapshot_moxfield_success(self):
        """Test successfully triggering snapshot creation for Moxfield deck"""
        from funcs.models import Deck, Card, CommanderSaltData
        
        mock_deck = {
            'deck_id': 1,
            'source': 'moxfield',
            'moxfield_deck_url': 'https://moxfield.com/decks/test123'
        }
        
        mock_proc_deck = Deck(
            deck_id='test123',
            name='Test Deck',
            owner_id='user',
            owner_name='User',
            source='Moxfield'
        )
        mock_proc_deck.commanders = [Card('cmd123', 'Commander', 1)]
        mock_proc_deck.library = [Card('card456', 'Card', 1)]
        
        mock_cs_data = CommanderSaltData(
            salt_rating=2.5,
            synergy_rating=7.8,
            power_level_rating=6.5,
            threat_rating=5.5,
            bracket_rating=3.0,
            overall_rating=7.0,
            manabase_score=8.2,
            power_level_display_value=7,
            combo_rating=4.5,
            archetype_minor='Voltron',
            archetype_major='Aggro',
            price_usd=250.50
        )
        
        with patch('routers.snapshots.get_deck_by_id', return_value=mock_deck), \
             patch('routers.snapshots.fetch_moxfield_deck', return_value=mock_proc_deck), \
             patch('routers.snapshots.fetch_commandersalt_deck_data', return_value=mock_cs_data), \
             patch('routers.snapshots.get_card_by_id', return_value=None), \
             patch('routers.snapshots.create_card', return_value=True), \
             patch('routers.snapshots.get_most_recent_snapshot_for_deck', return_value=None), \
             patch('routers.snapshots.create_snapshot', return_value=100), \
             patch('routers.snapshots.associate_card_with_snapshot', return_value=True):
            
            result = await snapshots.trigger_create_snapshot(1)
            
            assert result['snapshot_id'] == 100
            assert result['deck_id'] == 1
    
    async def test_trigger_create_snapshot_archidekt_with_existing_commander(self):
        """Test triggering snapshot creation for Archidekt deck with existing commander"""
        from funcs.models import Deck, Card, CommanderSaltData
        
        mock_deck = {
            'deck_id': 2,
            'source': 'archidekt',
            'archidekt_deck_url': 'https://archidekt.com/decks/456/test'
        }
        
        mock_proc_deck = Deck(
            deck_id=456,
            name='Archidekt Deck',
            owner_id='user',
            owner_name='User',
            source='Archidekt'
        )
        mock_proc_deck.commanders = [Card('cmd789', 'Commander 2', 1)]
        mock_proc_deck.library = []
        
        mock_cs_data = CommanderSaltData(
            salt_rating=3.0,
            synergy_rating=8.0,
            power_level_rating=7.0,
            threat_rating=6.0,
            bracket_rating=4.0,
            overall_rating=8.0,
            manabase_score=9.0,
            power_level_display_value=8,
            combo_rating=5.0,
            archetype_minor='Control',
            archetype_major='Control',
            price_usd=300.00
        )
        
        with patch('routers.snapshots.get_deck_by_id', return_value=mock_deck), \
             patch('routers.snapshots.fetch_archidekt_deck', return_value=mock_proc_deck), \
             patch('routers.snapshots.fetch_commandersalt_deck_data', return_value=mock_cs_data), \
             patch('routers.snapshots.get_card_by_id', return_value={'oracle_card_id': 'cmd789'}), \
             patch('routers.snapshots.get_most_recent_snapshot_for_deck', return_value={'week_of_league': 1}), \
             patch('routers.snapshots.create_snapshot', return_value=200):
            
            result = await snapshots.trigger_create_snapshot(2)
            
            assert result['snapshot_id'] == 200
    
    async def test_trigger_create_snapshot_failure(self):
        """Test triggering snapshot creation when creation fails"""
        from funcs.models import Deck, Card, CommanderSaltData
        
        mock_deck = {
            'deck_id': 1,
            'source': 'moxfield',
            'moxfield_deck_url': 'https://moxfield.com/decks/fail123'
        }
        
        mock_proc_deck = Deck(
            deck_id='fail123',
            name='Fail Deck',
            owner_id='user',
            owner_name='User',
            source='Moxfield'
        )
        mock_proc_deck.commanders = [Card('cmd999', 'Fail Commander', 1)]
        mock_proc_deck.library = []
        
        mock_cs_data = CommanderSaltData(
            salt_rating=1.0,
            synergy_rating=1.0,
            power_level_rating=1.0,
            threat_rating=1.0,
            bracket_rating=1.0,
            overall_rating=1.0,
            manabase_score=1.0,
            power_level_display_value=1,
            combo_rating=1.0,
            archetype_minor='Test',
            archetype_major='Test',
            price_usd=1.0
        )
        
        with patch('routers.snapshots.get_deck_by_id', return_value=mock_deck), \
             patch('routers.snapshots.fetch_moxfield_deck', return_value=mock_proc_deck), \
             patch('routers.snapshots.fetch_commandersalt_deck_data', return_value=mock_cs_data), \
             patch('routers.snapshots.get_card_by_id', return_value=None), \
             patch('routers.snapshots.create_card', return_value=True), \
             patch('routers.snapshots.get_most_recent_snapshot_for_deck', return_value=None), \
             patch('routers.snapshots.create_snapshot', return_value=None):
            
            with pytest.raises(HTTPException) as exc_info:
                await snapshots.trigger_create_snapshot(1)
            
            assert exc_info.value.status_code == 500
    
    async def test_read_snapshots_for_week_success(self):
        """Test reading snapshots for a specific week"""
        mock_snapshots = [
            {'snapshot_id': 1, 'week_of_league': 1},
            {'snapshot_id': 2, 'week_of_league': 1}
        ]
        
        with patch('routers.snapshots.get_all_snapshots_for_week', return_value=mock_snapshots):
            result = await snapshots.read_snapshots_for_week(1)
            
            assert result == mock_snapshots
    
    async def test_read_snapshots_for_week_not_found(self):
        """Test reading snapshots for a week when none exist"""
        with patch('routers.snapshots.get_all_snapshots_for_week', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await snapshots.read_snapshots_for_week(99)
            
            assert exc_info.value.status_code == 404
