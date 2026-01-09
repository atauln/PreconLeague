import asyncpg
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
import os
load_dotenv()


# Database configuration
DB_CONFIG = {
    'host': os.getenv('PSQL_HOST', 'localhost'),
    'port': int(os.getenv('PSQL_PORT', '5432')),
    'database': os.getenv('PSQL_DB', 'preconleage'),
    'user': os.getenv('PSQL_USER', 'preconleague'),
    'password': os.getenv('PSQL_PASSWORD', 'preconleague')
}

async def get_connection():
    """Establish an async connection to the remote PostgreSQL database"""
    try:
        conn = await asyncpg.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        return conn
    except asyncpg.PostgresError as e:
        print(f"Database connection error: {e}")
        return None

async def execute_query(query: str, params: tuple = None) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return results"""
    conn = await get_connection()
    if not conn:
        return []
    
    try:
        results = await conn.fetch(query, *(params or []))
        return [dict(result) for result in results]
    except asyncpg.PostgresError as e:
        print(f"Query execution error: {e}")
        return []
    finally:
        await conn.close()

async def execute_update(query: str, params: tuple = None) -> bool:
    """Execute an INSERT, UPDATE, or DELETE query"""
    conn = await get_connection()
    if not conn:
        return False
    
    try:
        await conn.execute(query, *(params or []))
        return True
    except asyncpg.PostgresError as e:
        print(f"Update execution error: {e}")
        return False
    finally:
        await conn.close()

async def execute_update_returning(query: str, params: tuple = None) -> Any:
    """Execute an INSERT, UPDATE, or DELETE query with RETURNING clause"""
    conn = await get_connection()
    if not conn:
        return None
    
    try:
        result = await conn.fetchrow(query, *(params or []))
        return result
    except asyncpg.PostgresError as e:
        print(f"Update with returning execution error: {e}")
        return None
    finally:
        await conn.close()


# Creation functions
async def create_user(user_name: str) -> Optional[int]:
    """Create a new user and return the user_id"""
    query = """
    INSERT INTO users (user_name) 
    VALUES ($1) 
    RETURNING user_id;
    """
    result = await execute_update_returning(query, (user_name,))
    return result['user_id'] if result else None

async def create_card(oracle_card_id: str, card_name: str) -> bool:
    """Create a new card"""
    query = """
    INSERT INTO cards (oracle_card_id, card_name) 
    VALUES ($1, $2)
    ON CONFLICT (oracle_card_id) DO NOTHING;
    """
    return await execute_update(query, (oracle_card_id, card_name))

async def create_deck(user_id: int, deck_name: str, source: str, moxfield_deck_id: Optional[int], archidekt_deck_id: Optional[str]) -> Optional[int]:
    """Create a new deck and return the deck_id"""
    if source not in ['moxfield', 'archidekt']:
        print(f"Invalid source: {source}")
        return None
    if source == 'moxfield':
        query = """
        INSERT INTO decks (user_id, deck_name, source, moxfield_deck_id) 
        VALUES ($1, $2, $3, $4) 
        RETURNING deck_id;
        """
        params = (user_id, deck_name, source, moxfield_deck_id)
    else:  # archidekt
        query = """
        INSERT INTO decks (user_id, deck_name, source, archidekt_deck_id) 
        VALUES ($1, $2, $3, $4) 
        RETURNING deck_id;
        """
        params = (user_id, deck_name, source, archidekt_deck_id)
    result = await execute_update_returning(query, params)
    return result['deck_id'] if result else None

async def create_snapshot(deck_id: int, commander_id: str, est_power: float, created_at: str = None) -> Optional[int]:
    """Create a new snapshot and return the snapshot_id"""
    if not created_at:
        query = """
        INSERT INTO snapshots (deck_id, commander_id, created_at, est_power)
        VALUES ($1, $2, NOW(), $3)
        RETURNING snapshot_id;
        """
        params = (deck_id, commander_id, est_power)
    else:
        query = """
        INSERT INTO snapshots (deck_id, commander_id, created_at, est_power) 
        VALUES ($1, $2, $3, $4) 
        RETURNING snapshot_id;
        """
        params = (deck_id, commander_id, created_at, est_power)
    result = await execute_update_returning(query, params)
    return result['snapshot_id'] if result else None

async def associate_card_with_snapshot(snapshot_id: int, card_id: str) -> bool:
    """Associate a card with a snapshot in the library"""
    query = """
    INSERT INTO library_cards (snapshot_id, card_id) 
    VALUES ($1, $2)
    ON CONFLICT (snapshot_id, card_id) DO NOTHING;
    """
    return await execute_update(query, (snapshot_id, card_id))

# Basic retrieval functions
async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a user by user_id"""
    query = "SELECT * FROM users WHERE user_id = $1;"
    results = await execute_query(query, (user_id,))
    return results[0] if results else None

async def get_card_by_id(card_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a card by card_id"""
    query = "SELECT * FROM cards WHERE card_oracle_card_id = $1;"
    results = await execute_query(query, (card_id,))
    return results[0] if results else None

async def get_deck_by_id(deck_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a deck by deck_id"""
    query = "SELECT * FROM decks WHERE deck_id = $1;"
    results = await execute_query(query, (deck_id,))
    return results[0] if results else None

async def get_snapshot_by_id(snapshot_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a snapshot by snapshot_id"""
    query = "SELECT * FROM snapshots WHERE snapshot_id = $1;"
    results = await execute_query(query, (snapshot_id,))
    return results[0] if results else None

async def get_library_cards_by_snapshot(snapshot_id: int) -> List[Dict[str, Any]]:
    """Retrieve all library cards associated with a snapshot"""
    query = "SELECT * FROM library_cards WHERE snapshot_id = $1;"
    return await execute_query(query, (snapshot_id,))

# Additional complex retrieval functions can be added as needed
async def get_deck_with_snapshots(deck_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a deck along with its snapshots"""
    deck = await get_deck_by_id(deck_id)
    if not deck:
        return None
    
    query = "SELECT * FROM snapshots WHERE deck_id = $1;"
    snapshots = await execute_query(query, (deck_id,))
    deck['snapshots'] = snapshots
    return deck

async def get_snapshot_with_library(snapshot_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a snapshot along with its library cards"""
    snapshot = await get_snapshot_by_id(snapshot_id)
    if not snapshot:
        return None
    
    query = """
    SELECT lc.card_id, c.card_name 
    FROM library_cards lc
    JOIN cards c ON lc.card_id = c.card_id
    WHERE lc.snapshot_id = $1;
    """
    library_cards = await execute_query(query, (snapshot_id,))
    snapshot['library_cards'] = library_cards
    return snapshot

async def get_user_decks(user_id: int) -> List[Dict[str, Any]]:
    """Retrieve all decks for a specific user"""
    query = "SELECT * FROM decks WHERE user_id = $1;"
    return await execute_query(query, (user_id,))

async def find_deck_by_moxfield_id(moxfield_deck_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a deck by its Moxfield deck ID"""
    query = "SELECT * FROM decks WHERE moxfield_deck_id = $1;"
    results = await execute_query(query, (moxfield_deck_id,))
    return results[0] if results else None

async def find_deck_by_archidekt_id(archidekt_deck_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a deck by its Archidekt deck ID"""
    query = "SELECT * FROM decks WHERE archidekt_deck_id = $1;"
    results = await execute_query(query, (archidekt_deck_id,))
    return results[0] if results else None

# Bulk retrieval functions
async def get_all_users() -> List[Dict[str, Any]]:
    """Retrieve all users"""
    query = "SELECT * FROM users;"
    return await execute_query(query)

async def get_all_cards() -> List[Dict[str, Any]]:
    """Retrieve all cards"""
    query = "SELECT * FROM cards;"
    return await execute_query(query)

async def get_all_decks() -> List[Dict[str, Any]]:
    """Retrieve all decks"""
    query = "SELECT * FROM decks;"
    return await execute_query(query)

async def get_all_snapshots() -> List[Dict[str, Any]]:
    """Retrieve all snapshots"""
    query = """
    SELECT s.*, d.deck_name, d.user_id, d.user_name 
    FROM snapshots s
    JOIN decks d ON s.deck_id = d.deck_id;
    """
    return await execute_query(query)

async def get_deck_snapshots(deck_id: int) -> List[Dict[str, Any]]:
    """Retrieve all snapshots for a specific deck"""
    query = "SELECT * FROM snapshots WHERE deck_id = $1;"
    return await execute_query(query, (deck_id,))

async def initialize_database():
    """Initialize the database connection using the file init-db.sql"""
    conn = await get_connection()
    if not conn:
        print("Failed to connect to the database for initialization.")
        return
    
    try:
        with open('init-db.sql', 'r') as f:
            init_sql = f.read()
        await conn.execute(init_sql)
        print("Database initialized successfully.")
    except (asyncpg.PostgresError, FileNotFoundError) as e:
        print(f"Database initialization error: {e}")
    finally:
        await conn.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(initialize_database())
