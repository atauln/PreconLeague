"""Unit tests for api/db.py database functions"""
import pytest
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

# Add the api directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

import db


@pytest.mark.asyncio
class TestDatabaseConnection:
    """Tests for database connection functions"""
    
    async def test_get_connection_success(self):
        """Test successful database connection"""
        with patch('db.asyncpg.connect', new_callable=AsyncMock) as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            
            result = await db.get_connection()
            
            assert result == mock_conn
            mock_connect.assert_called_once()
    
    async def test_get_connection_failure(self):
        """Test database connection failure"""
        import asyncpg
        with patch('db.asyncpg.connect', new_callable=AsyncMock) as mock_connect:
            mock_connect.side_effect = asyncpg.PostgresError("Connection failed")
            
            result = await db.get_connection()
            
            # Should catch the exception and return None
            assert result is None


@pytest.mark.asyncio
class TestExecuteQuery:
    """Tests for execute_query function"""
    
    async def test_execute_query_success(self):
        """Test successful query execution"""
        mock_conn = AsyncMock()
        mock_result = [
            {'id': 1, 'name': 'test1'},
            {'id': 2, 'name': 'test2'}
        ]
        mock_conn.fetch.return_value = mock_result
        
        with patch('db.get_connection', return_value=mock_conn):
            result = await db.execute_query("SELECT * FROM test")
            
            assert len(result) == 2
            assert result[0]['id'] == 1
            mock_conn.close.assert_called_once()
    
    async def test_execute_query_with_params(self):
        """Test query execution with parameters"""
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = [{'id': 1}]
        
        with patch('db.get_connection', return_value=mock_conn):
            result = await db.execute_query("SELECT * FROM test WHERE id = $1", (1,))
            
            assert len(result) == 1
            mock_conn.fetch.assert_called_once_with("SELECT * FROM test WHERE id = $1", 1)
    
    async def test_execute_query_connection_failure(self):
        """Test query execution when connection fails"""
        with patch('db.get_connection', return_value=None):
            result = await db.execute_query("SELECT * FROM test")
            
            assert result == []
    
    async def test_execute_query_error_handling(self):
        """Test query execution error handling"""
        import asyncpg
        mock_conn = AsyncMock()
        mock_conn.fetch.side_effect = asyncpg.PostgresError("Query error")
        
        with patch('db.get_connection', return_value=mock_conn):
            result = await db.execute_query("SELECT * FROM test")
            
            assert result == []
            mock_conn.close.assert_called_once()


@pytest.mark.asyncio
class TestExecuteUpdate:
    """Tests for execute_update function"""
    
    async def test_execute_update_success(self):
        """Test successful update execution"""
        mock_conn = AsyncMock()
        
        with patch('db.get_connection', return_value=mock_conn):
            result = await db.execute_update("UPDATE test SET name = $1", ("new_name",))
            
            assert result is True
            mock_conn.execute.assert_called_once()
            mock_conn.close.assert_called_once()
    
    async def test_execute_update_connection_failure(self):
        """Test update execution when connection fails"""
        with patch('db.get_connection', return_value=None):
            result = await db.execute_update("UPDATE test SET name = $1", ("new_name",))
            
            assert result is False
    
    async def test_execute_update_error_handling(self):
        """Test update execution error handling"""
        import asyncpg
        mock_conn = AsyncMock()
        mock_conn.execute.side_effect = asyncpg.PostgresError("Update error")
        
        with patch('db.get_connection', return_value=mock_conn):
            result = await db.execute_update("UPDATE test SET name = $1", ("new_name",))
            
            assert result is False
            mock_conn.close.assert_called_once()


@pytest.mark.asyncio
class TestExecuteUpdateReturning:
    """Tests for execute_update_returning function"""
    
    async def test_execute_update_returning_success(self):
        """Test successful update with RETURNING clause"""
        mock_conn = AsyncMock()
        mock_result = {'id': 1, 'name': 'test'}
        mock_conn.fetchrow.return_value = mock_result
        
        with patch('db.get_connection', return_value=mock_conn):
            result = await db.execute_update_returning(
                "INSERT INTO test (name) VALUES ($1) RETURNING id", 
                ("test",)
            )
            
            assert result == mock_result
            mock_conn.close.assert_called_once()
    
    async def test_execute_update_returning_connection_failure(self):
        """Test update returning when connection fails"""
        with patch('db.get_connection', return_value=None):
            result = await db.execute_update_returning(
                "INSERT INTO test (name) VALUES ($1) RETURNING id", 
                ("test",)
            )
            
            assert result is None


@pytest.mark.asyncio
class TestCreateUser:
    """Tests for create_user function"""
    
    async def test_create_user_success(self):
        """Test successful user creation"""
        mock_result = {'user_id': 123}
        
        with patch('db.execute_update_returning', return_value=mock_result):
            user_id = await db.create_user("testuser")
            
            assert user_id == 123
    
    async def test_create_user_failure(self):
        """Test user creation failure"""
        with patch('db.execute_update_returning', return_value=None):
            user_id = await db.create_user("testuser")
            
            assert user_id is None


@pytest.mark.asyncio
class TestCreateCard:
    """Tests for create_card function"""
    
    async def test_create_card_success(self):
        """Test successful card creation"""
        with patch('db.execute_update', return_value=True):
            result = await db.create_card("oracle123", "Lightning Bolt")
            
            assert result is True
    
    async def test_create_card_failure(self):
        """Test card creation failure"""
        with patch('db.execute_update', return_value=False):
            result = await db.create_card("oracle456", "Counterspell")
            
            assert result is False


@pytest.mark.asyncio
class TestCreateDeck:
    """Tests for create_deck function"""
    
    async def test_create_deck_moxfield_success(self):
        """Test successful deck creation with Moxfield source"""
        mock_result = {'deck_id': 42}
        
        with patch('db.execute_update_returning', return_value=mock_result):
            deck_id = await db.create_deck(
                user_id=1,
                deck_name="Test Deck",
                source="moxfield",
                moxfield_deck_url="https://moxfield.com/decks/abc123"
            )
            
            assert deck_id == 42
    
    async def test_create_deck_archidekt_success(self):
        """Test successful deck creation with Archidekt source"""
        mock_result = {'deck_id': 99}
        
        with patch('db.execute_update_returning', return_value=mock_result):
            deck_id = await db.create_deck(
                user_id=2,
                deck_name="Archidekt Deck",
                source="archidekt",
                archidekt_deck_url="https://archidekt.com/decks/12345"
            )
            
            assert deck_id == 99
    
    async def test_create_deck_invalid_source(self):
        """Test deck creation with invalid source"""
        deck_id = await db.create_deck(
            user_id=3,
            deck_name="Invalid Deck",
            source="invalid_source"
        )
        
        assert deck_id is None
    
    async def test_create_deck_failure(self):
        """Test deck creation failure"""
        with patch('db.execute_update_returning', return_value=None):
            deck_id = await db.create_deck(
                user_id=4,
                deck_name="Failed Deck",
                source="moxfield",
                moxfield_deck_url="https://moxfield.com/decks/fail"
            )
            
            assert deck_id is None


@pytest.mark.asyncio
class TestGetFunctions:
    """Tests for retrieval functions"""
    
    async def test_get_user_by_id_success(self):
        """Test successful user retrieval"""
        mock_users = [{'user_id': 1, 'user_name': 'testuser'}]
        
        with patch('db.execute_query', return_value=mock_users):
            user = await db.get_user_by_id(1)
            
            assert user is not None
            assert user['user_id'] == 1
            assert user['user_name'] == 'testuser'
    
    async def test_get_user_by_id_not_found(self):
        """Test user retrieval when user doesn't exist"""
        with patch('db.execute_query', return_value=[]):
            user = await db.get_user_by_id(999)
            
            assert user is None
    
    async def test_get_deck_by_id_success(self):
        """Test successful deck retrieval"""
        mock_decks = [{'deck_id': 1, 'deck_name': 'Test Deck'}]
        
        with patch('db.execute_query', return_value=mock_decks):
            deck = await db.get_deck_by_id(1)
            
            assert deck is not None
            assert deck['deck_id'] == 1
    
    async def test_get_all_users(self):
        """Test retrieving all users"""
        mock_users = [
            {'user_id': 1, 'user_name': 'user1'},
            {'user_id': 2, 'user_name': 'user2'}
        ]
        
        with patch('db.execute_query', return_value=mock_users):
            users = await db.get_all_users()
            
            assert len(users) == 2
            assert users[0]['user_name'] == 'user1'
    
    async def test_get_user_decks(self):
        """Test retrieving all decks for a user"""
        mock_decks = [
            {'deck_id': 1, 'deck_name': 'Deck 1', 'user_id': 1},
            {'deck_id': 2, 'deck_name': 'Deck 2', 'user_id': 1}
        ]
        
        with patch('db.execute_query', return_value=mock_decks):
            decks = await db.get_user_decks(1)
            
            assert len(decks) == 2
            assert all(deck['user_id'] == 1 for deck in decks)


@pytest.mark.asyncio
class TestFindDeckByUrl:
    """Tests for find_deck_by_url functions"""
    
    async def test_find_deck_by_moxfield_url_success(self):
        """Test finding deck by Moxfield URL"""
        mock_deck = [{'deck_id': 1, 'moxfield_deck_url': 'https://moxfield.com/decks/abc'}]
        
        with patch('db.execute_query', return_value=mock_deck):
            deck = await db.find_deck_by_moxfield_url('https://moxfield.com/decks/abc')
            
            assert deck is not None
            assert deck['deck_id'] == 1
    
    async def test_find_deck_by_moxfield_url_not_found(self):
        """Test finding deck by Moxfield URL when not found"""
        with patch('db.execute_query', return_value=[]):
            deck = await db.find_deck_by_moxfield_url('https://moxfield.com/decks/notfound')
            
            assert deck is None
    
    async def test_find_deck_by_archidekt_url_success(self):
        """Test finding deck by Archidekt URL"""
        mock_deck = [{'deck_id': 2, 'archidekt_deck_url': 'https://archidekt.com/decks/12345'}]
        
        with patch('db.execute_query', return_value=mock_deck):
            deck = await db.find_deck_by_archidekt_url('https://archidekt.com/decks/12345')
            
            assert deck is not None
            assert deck['deck_id'] == 2


@pytest.mark.asyncio
class TestAdditionalDBFunctions:
    """Tests for additional database functions"""
    
    async def test_get_user_by_name_success(self):
        """Test getting user by name"""
        mock_user = [{'user_id': 1, 'user_name': 'testuser'}]
        
        with patch('db.execute_query', return_value=mock_user):
            user = await db.get_user_by_name('testuser')
            
            assert user is not None
            assert user['user_name'] == 'testuser'
    
    async def test_get_user_by_name_not_found(self):
        """Test getting user by name when not found"""
        with patch('db.execute_query', return_value=[]):
            user = await db.get_user_by_name('nonexistent')
            
            assert user is None
    
    async def test_get_library_cards_by_snapshot(self):
        """Test getting library cards for a snapshot"""
        mock_cards = [
            {'snapshot_id': 1, 'card_id': 'card1'},
            {'snapshot_id': 1, 'card_id': 'card2'}
        ]
        
        with patch('db.execute_query', return_value=mock_cards):
            cards = await db.get_library_cards_by_snapshot(1)
            
            assert len(cards) == 2
    
    async def test_get_deck_with_snapshots_success(self):
        """Test getting deck with snapshots"""
        mock_deck = {'deck_id': 1, 'deck_name': 'Test Deck'}
        mock_snapshots = [
            {'snapshot_id': 1, 'deck_id': 1},
            {'snapshot_id': 2, 'deck_id': 1}
        ]
        
        with patch('db.get_deck_by_id', return_value=mock_deck), \
             patch('db.execute_query', return_value=mock_snapshots):
            
            deck = await db.get_deck_with_snapshots(1)
            
            assert deck is not None
            assert 'snapshots' in deck
            assert len(deck['snapshots']) == 2
    
    async def test_get_deck_with_snapshots_not_found(self):
        """Test getting deck with snapshots when deck not found"""
        with patch('db.get_deck_by_id', return_value=None):
            deck = await db.get_deck_with_snapshots(999)
            
            assert deck is None
    
    async def test_get_most_recent_snapshot_for_deck_success(self):
        """Test getting most recent snapshot for deck"""
        mock_snapshot = [{'snapshot_id': 5, 'deck_id': 1, 'created_at': '2024-01-01'}]
        
        with patch('db.execute_query', return_value=mock_snapshot):
            snapshot = await db.get_most_recent_snapshot_for_deck(1)
            
            assert snapshot is not None
            assert snapshot['snapshot_id'] == 5
    
    async def test_get_most_recent_snapshot_for_deck_not_found(self):
        """Test getting most recent snapshot when none exist"""
        with patch('db.execute_query', return_value=[]):
            snapshot = await db.get_most_recent_snapshot_for_deck(999)
            
            assert snapshot is None
    
    async def test_get_all_snapshots_for_week(self):
        """Test getting all snapshots for a specific week"""
        mock_snapshots = [
            {'snapshot_id': 1, 'week_of_league': 1},
            {'snapshot_id': 2, 'week_of_league': 1}
        ]
        
        with patch('db.execute_query', return_value=mock_snapshots):
            snapshots = await db.get_all_snapshots_for_week(1)
            
            assert len(snapshots) == 2
    
    async def test_get_all_users(self):
        """Test getting all users"""
        mock_users = [
            {'user_id': 1, 'user_name': 'user1'},
            {'user_id': 2, 'user_name': 'user2'}
        ]
        
        with patch('db.execute_query', return_value=mock_users):
            users = await db.get_all_users()
            
            assert len(users) == 2
    
    async def test_get_all_cards(self):
        """Test getting all cards"""
        mock_cards = [
            {'oracle_card_id': 'card1', 'card_name': 'Card 1'},
            {'oracle_card_id': 'card2', 'card_name': 'Card 2'}
        ]
        
        with patch('db.execute_query', return_value=mock_cards):
            cards = await db.get_all_cards()
            
            assert len(cards) == 2
    
    async def test_get_all_decks(self):
        """Test getting all decks"""
        mock_decks = [
            {'deck_id': 1, 'deck_name': 'Deck 1'},
            {'deck_id': 2, 'deck_name': 'Deck 2'}
        ]
        
        with patch('db.execute_query', return_value=mock_decks):
            decks = await db.get_all_decks()
            
            assert len(decks) == 2
    
    async def test_get_all_snapshots(self):
        """Test getting all snapshots with join data"""
        mock_snapshots = [
            {'snapshot_id': 1, 'deck_name': 'Deck 1', 'user_name': 'User 1'},
            {'snapshot_id': 2, 'deck_name': 'Deck 2', 'user_name': 'User 2'}
        ]
        
        with patch('db.execute_query', return_value=mock_snapshots):
            snapshots = await db.get_all_snapshots()
            
            assert len(snapshots) == 2
    
    async def test_get_deck_snapshots(self):
        """Test getting all snapshots for a deck"""
        mock_snapshots = [
            {'snapshot_id': 1, 'deck_id': 1},
            {'snapshot_id': 2, 'deck_id': 1}
        ]
        
        with patch('db.execute_query', return_value=mock_snapshots):
            snapshots = await db.get_deck_snapshots(1)
            
            assert len(snapshots) == 2
    
    async def test_create_snapshot_with_created_at(self):
        """Test creating snapshot with created_at parameter"""
        mock_result = {'snapshot_id': 100}
        
        with patch('db.execute_update_returning', return_value=mock_result):
            snapshot_id = await db.create_snapshot(
                deck_id=1,
                commander_id='cmd123',
                created_at='2024-01-01 00:00:00',
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
                price_usd=250.50,
                week_of_league=1
            )
            
            assert snapshot_id == 100
    
    async def test_create_snapshot_without_created_at(self):
        """Test creating snapshot without created_at parameter"""
        mock_result = {'snapshot_id': 200}
        
        with patch('db.execute_update_returning', return_value=mock_result):
            snapshot_id = await db.create_snapshot(
                deck_id=2,
                commander_id='cmd456',
                week_of_league=2
            )
            
            assert snapshot_id == 200
    
    async def test_create_snapshot_returning_none(self):
        """Test creating snapshot when database returns None"""
        with patch('db.execute_update_returning', return_value=None):
            snapshot_id = await db.create_snapshot(
                deck_id=3,
                commander_id='cmd789'
            )
            
            assert snapshot_id is None
    
    async def test_associate_card_with_snapshot_success(self):
        """Test successfully associating a card with snapshot"""
        with patch('db.execute_update', return_value=True):
            result = await db.associate_card_with_snapshot(1, 'card123')
            
            assert result is True
    
    async def test_associate_card_with_snapshot_failure(self):
        """Test failing to associate a card with snapshot"""
        with patch('db.execute_update', return_value=False):
            result = await db.associate_card_with_snapshot(999, 'card999')
            
            assert result is False
    
    async def test_initialize_database_success(self):
        """Test successful database initialization"""
        mock_conn = AsyncMock()
        mock_file_content = "CREATE TABLE test;"
        
        with patch('db.get_connection', return_value=mock_conn), \
             patch('builtins.open', MagicMock(return_value=MagicMock(__enter__=lambda s: s, __exit__=lambda s, *args: None, read=lambda: mock_file_content))):
            
            await db.initialize_database()
            
            mock_conn.execute.assert_called_once_with(mock_file_content)
            mock_conn.close.assert_called_once()
    
    async def test_initialize_database_connection_failure(self):
        """Test database initialization when connection fails"""
        with patch('db.get_connection', return_value=None):
            # Should not raise an error, just print a message
            await db.initialize_database()
    
    async def test_initialize_database_file_not_found(self):
        """Test database initialization when SQL file not found"""
        mock_conn = AsyncMock()
        
        with patch('db.get_connection', return_value=mock_conn), \
             patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            
            await db.initialize_database()
            
            mock_conn.close.assert_called_once()
    
    async def test_initialize_database_postgres_error(self):
        """Test database initialization with Postgres error"""
        import asyncpg
        mock_conn = AsyncMock()
        mock_conn.execute.side_effect = asyncpg.PostgresError("SQL Error")
        mock_file_content = "CREATE TABLE test;"
        
        with patch('db.get_connection', return_value=mock_conn), \
             patch('builtins.open', MagicMock(return_value=MagicMock(__enter__=lambda s: s, __exit__=lambda s, *args: None, read=lambda: mock_file_content))):
            
            await db.initialize_database()
            
            mock_conn.close.assert_called_once()
