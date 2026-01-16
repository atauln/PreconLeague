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
        conn = await asyncpg.connect(**DB_CONFIG)
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

async def create_deck(user_id: int, deck_name: str, source: str, moxfield_deck_url: Optional[str] = None, archidekt_deck_url: Optional[str] = None) -> Optional[int]:
    """Create a new deck and return the deck_id"""
    if source not in ['moxfield', 'archidekt']:
        print(f"Invalid source: {source}")
        return None
    if source == 'moxfield':
        query = """
        INSERT INTO decks (user_id, deck_name, source, moxfield_deck_url) 
        VALUES ($1, $2, $3, $4) 
        RETURNING deck_id;
        """
        params = (user_id, deck_name, source, moxfield_deck_url)
    else:  # archidekt
        query = """
        INSERT INTO decks (user_id, deck_name, source, archidekt_deck_url) 
        VALUES ($1, $2, $3, $4) 
        RETURNING deck_id;
        """
        params = (user_id, deck_name, source, archidekt_deck_url)
    result = await execute_update_returning(query, params)
    return result['deck_id'] if result else None

async def create_snapshot(
    deck_id: int,
    commander_id: str,
    salt_rating: Optional[float] = None,
    synergy_rating: Optional[float] = None,
    power_level_rating: Optional[float] = None,
    threat_rating: Optional[float] = None,
    bracket_rating: Optional[float] = None,
    overall_rating: Optional[float] = None,
    manabase_score: Optional[float] = None,
    power_level_display_value: Optional[int] = None,
    combo_rating: Optional[float] = None,
    archetype_minor: Optional[str] = None,
    archetype_major: Optional[str] = None,
    price_usd: Optional[float] = None,
    created_at: Optional[str] = None,
    week_of_league: Optional[int] = None,
    mana_fixing_score: Optional[float] = None,
    competitive_intent: Optional[int] = None,
    commander_tier: Optional[int] = None,
    card_quality: Optional[float] = None,
) -> Optional[int]:
    """Create a new snapshot and return the snapshot_id"""
    if created_at:
        query = """
        INSERT INTO snapshots (
            deck_id,
            commander_id,
            created_at,
            salt_rating,
            synergy_rating,
            power_level_rating,
            threat_rating,
            bracket_rating,
            overall_rating,
            manabase_score,
            power_level_display_value,
            combo_rating,
            archetype_minor,
            archetype_major,
            price_usd,
            week_of_league,
            mana_fixing_score,
            competitive_intent,
            commander_tier,
            card_quality
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20
        )
        RETURNING snapshot_id;
        """
        params = (
            deck_id,
            commander_id,
            created_at,
            salt_rating,
            synergy_rating,
            power_level_rating,
            threat_rating,
            bracket_rating,
            overall_rating,
            manabase_score,
            power_level_display_value,
            combo_rating,
            archetype_minor,
            archetype_major,
            price_usd,
            week_of_league,
            mana_fixing_score,
            competitive_intent,
            commander_tier,
            card_quality
        )
    else:
        query = """
        INSERT INTO snapshots (
            deck_id,
            commander_id,
            salt_rating,
            synergy_rating,
            power_level_rating,
            threat_rating,
            bracket_rating,
            overall_rating,
            manabase_score,
            power_level_display_value,
            combo_rating,
            archetype_minor,
            archetype_major,
            price_usd,
            week_of_league,
            mana_fixing_score,
            competitive_intent,
            commander_tier,
            card_quality
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19
        )
        RETURNING snapshot_id;
        """
        params = (
            deck_id,
            commander_id,
            salt_rating,
            synergy_rating,
            power_level_rating,
            threat_rating,
            bracket_rating,
            overall_rating,
            manabase_score,
            power_level_display_value,
            combo_rating,
            archetype_minor,
            archetype_major,
            price_usd,
            week_of_league,
            mana_fixing_score,
            competitive_intent,
            commander_tier,
            card_quality
        )
    result = await execute_update_returning(query, params)
    return result['snapshot_id'] if result else None

async def associate_card_with_snapshot(snapshot_id: int, card_id: str) -> bool:
    """Associate a card with a snapshot in the library"""
    query = """
    INSERT INTO library_cards (snapshot_id, card_id)
    VALUES ($1, $2);
    """
    return await execute_update(query, (snapshot_id, card_id))


async def get_cards_by_ids(card_ids: List[str]) -> List[Dict[str, Any]]:
    """Retrieve cards by a list of oracle_card_id values in a single query."""
    if not card_ids:
        return []
    query = "SELECT * FROM cards WHERE oracle_card_id = ANY($1);"
    return await execute_query(query, (card_ids,))


async def create_cards_bulk(cards: List[tuple]) -> bool:
    """Insert multiple cards using a single connection and executemany.
    `cards` should be an iterable of tuples (oracle_card_id, card_name).
    """
    if not cards:
        return True
    conn = await get_connection()
    if not conn:
        return False
    try:
        await conn.executemany(
            "INSERT INTO cards (oracle_card_id, card_name) VALUES ($1, $2) ON CONFLICT (oracle_card_id) DO NOTHING;",
            cards,
        )
        return True
    except asyncpg.PostgresError as e:
        print(f"Bulk create cards error: {e}")
        return False
    finally:
        await conn.close()


async def associate_cards_with_snapshot_bulk(snapshot_id: int, card_ids: List[str]) -> bool:
    """Associate multiple card_ids with a snapshot in a single executemany call.

    `card_ids` may include repeated IDs to represent multiple copies; this function
    will insert one row per list entry (no conflict handling).
    """
    if not card_ids:
        return True
    conn = await get_connection()
    if not conn:
        return False
    try:
        params = [(snapshot_id, cid) for cid in card_ids]
        await conn.executemany(
            "INSERT INTO library_cards (snapshot_id, card_id) VALUES ($1, $2);",
            params,
        )
        return True
    except asyncpg.PostgresError as e:
        print(f"Bulk associate cards with snapshot error: {e}")
        return False
    finally:
        await conn.close()

# Basic retrieval functions
async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a user by user_id"""
    query = "SELECT * FROM users WHERE user_id = $1;"
    results = await execute_query(query, (user_id,))
    return results[0] if results else None


async def get_user_by_name(user_name: str) -> Optional[Dict[str, Any]]:
    """Retrieve a user by user_name"""
    query = "SELECT * FROM users WHERE user_name = $1;"
    results = await execute_query(query, (user_name,))
    return results[0] if results else None

async def get_card_by_id(card_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a card by card_id"""
    query = "SELECT * FROM cards WHERE oracle_card_id = $1;"
    results = await execute_query(query, (card_id,))
    return results[0] if results else None

async def get_deck_by_id(deck_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a deck by deck_id"""
    query = """
    SELECT d.*, u.user_name
    FROM decks d
    JOIN users u ON d.user_id = u.user_id
    WHERE d.deck_id = $1;
    """
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
    JOIN cards c ON lc.card_id = c.oracle_card_id
    WHERE lc.snapshot_id = $1;
    """
    library_cards = await execute_query(query, (snapshot_id,))
    snapshot['library_cards'] = library_cards
    return snapshot

async def get_user_decks(user_id: int) -> List[Dict[str, Any]]:
    """Retrieve all decks for a specific user"""
    query = """
    SELECT d.*, u.user_name
    FROM decks d
    JOIN users u ON d.user_id = u.user_id
    WHERE d.user_id = $1;
    """
    return await execute_query(query, (user_id,))

async def find_deck_by_moxfield_url(moxfield_deck_url: str) -> Optional[Dict[str, Any]]:
    """Retrieve a deck by its Moxfield deck URL"""
    query = "SELECT * FROM decks WHERE moxfield_deck_url = $1;"
    results = await execute_query(query, (moxfield_deck_url,))
    return results[0] if results else None

async def find_deck_by_archidekt_url(archidekt_deck_url: str) -> Optional[Dict[str, Any]]:
    """Retrieve a deck by its Archidekt deck URL"""
    query = "SELECT * FROM decks WHERE archidekt_deck_url = $1;"
    results = await execute_query(query, (archidekt_deck_url,))
    return results[0] if results else None

async def get_most_recent_snapshot_for_deck(deck_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve the most recent snapshot for a specific deck"""
    query = """
    SELECT * FROM snapshots 
    WHERE deck_id = $1 
    ORDER BY created_at DESC 
    LIMIT 1;
    """
    results = await execute_query(query, (deck_id,))
    return results[0] if results else None

async def get_most_recent_snapshot_for_deck_and_week(deck_id: int, week_of_league: int) -> Optional[Dict[str, Any]]:
    """Retrieve the most recent snapshot for a specific deck and week of the league"""
    query = """
    SELECT * FROM snapshots 
    WHERE deck_id = $1 AND week_of_league = $2
    ORDER BY created_at DESC 
    LIMIT 1;
    """
    results = await execute_query(query, (deck_id, week_of_league))
    return results[0] if results else None

async def get_all_snapshots_for_week(week_of_league: int) -> List[Dict[str, Any]]:
    """Retrieve all snapshots for a specific week of the league"""
    query = "SELECT * FROM snapshots WHERE week_of_league = $1;"
    return await execute_query(query, (week_of_league,))

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
    query = """
    SELECT d.*, u.user_name
    FROM decks d
    JOIN users u ON d.user_id = u.user_id;
    """
    return await execute_query(query)

async def get_all_snapshots() -> List[Dict[str, Any]]:
    """Retrieve all snapshots"""
    query = """
    SELECT s.*, d.deck_name, d.user_id, u.user_name 
    FROM snapshots s
    JOIN decks d ON s.deck_id = d.deck_id
    JOIN users u ON d.user_id = u.user_id;
    """
    return await execute_query(query)


async def get_most_recent_snapshots_per_deck_all_weeks() -> List[Dict[str, Any]]:
    """Retrieve the most recent snapshot per deck per week_of_league.

    Uses DISTINCT ON to pick the newest snapshot (by created_at) for each
    (deck_id, week_of_league) pair. Only snapshots with a non-null
    `week_of_league` are returned.
    """
    query = """
    SELECT DISTINCT ON (s.deck_id, s.week_of_league) s.*, d.deck_name, u.user_name
    FROM snapshots s
    JOIN decks d ON s.deck_id = d.deck_id
    JOIN users u ON d.user_id = u.user_id
    WHERE s.week_of_league IS NOT NULL
    ORDER BY s.deck_id, s.week_of_league, s.created_at DESC;
    """
    return await execute_query(query)

async def get_deck_snapshots(deck_id: int) -> List[Dict[str, Any]]:
    """Retrieve all snapshots for a specific deck"""
    query = "SELECT * FROM snapshots WHERE deck_id = $1;"
    return await execute_query(query, (deck_id,))

# update functions can be added as needed
async def update_snapshot_week(snapshot_id: int, week_of_league: int) -> bool:
    """Update the week_of_league for a specific snapshot"""
    query = "UPDATE snapshots SET week_of_league = $1 WHERE snapshot_id = $2;"
    return await execute_update(query, (week_of_league, snapshot_id))

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
