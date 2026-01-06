import psycopg2
from psycopg2 import sql
from typing import List, Dict, Any

from dotenv import load_dotenv
import os
load_dotenv()


# Database configuration
DB_CONFIG = {
    'host': os.getenv('PSQL_HOST', 'localhost'),
    'port': os.getenv('PSQL_PORT', '5432'),
    'database': os.getenv('PSQL_DB', 'preconleage'),
    'user': os.getenv('PSQL_USER', 'preconleague'),
    'password': os.getenv('PSQL_PASSWORD', 'preconleague')
}

def get_connection():
    """Establish a connection to the remote PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

def execute_query(query: str, params: tuple = None) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return results"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return results
    except psycopg2.Error as e:
        print(f"Query execution error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def execute_update(query: str, params: tuple = None) -> bool:
    """Execute an INSERT, UPDATE, or DELETE query"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Update execution error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def execute_update_returning(query: str, params: tuple = None) -> Any:
    """Execute an INSERT, UPDATE, or DELETE query with RETURNING clause"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.commit()
        return result
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Update with returning execution error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# Creation functions
def create_user(user_name: str) -> int:
    """Create a new user and return the user_id"""
    query = """
    INSERT INTO users (user_name) 
    VALUES (%s) 
    RETURNING user_id;
    """
    result = execute_update_returning(query, (user_name,))
    return result[0] if result else None

def create_card(card_id: str, card_name: str) -> bool:
    """Create a new card"""
    query = """
    INSERT INTO cards (card_id, card_name) 
    VALUES (%s, %s)
    ON CONFLICT (card_id) DO NOTHING;
    """
    return execute_update(query, (card_id, card_name))

def create_deck(user_id: int, deck_name: str) -> int:
    """Create a new deck and return the deck_id"""
    query = """
    INSERT INTO decks (user_id, deck_name) 
    VALUES (%s, %s) 
    RETURNING deck_id;
    """
    result = execute_update_returning(query, (user_id, deck_name))
    return result[0] if result else None

def create_snapshot(deck_id: int, commander_id: str, est_power: float) -> int:
    """Create a new snapshot and return the snapshot_id"""
    query = """
    INSERT INTO snapshots (deck_id, commander_id, est_power) 
    VALUES (%s, %s, %s) 
    RETURNING snapshot_id;
    """
    result = execute_update_returning(query, (deck_id, commander_id, est_power))
    return result[0] if result else None

def associate_card_with_snapshot(snapshot_id: int, card_id: str) -> bool:
    """Associate a card with a snapshot in the library"""
    query = """
    INSERT INTO library_cards (snapshot_id, card_id) 
    VALUES (%s, %s)
    ON CONFLICT (snapshot_id, card_id) DO NOTHING;
    """
    return execute_update(query, (snapshot_id, card_id))

# Basic retrieval functions
def get_user_by_id(user_id: int) -> Dict[str, Any]:
    """Retrieve a user by user_id"""
    query = "SELECT * FROM users WHERE user_id = %s;"
    results = execute_query(query, (user_id,))
    return results[0] if results else None

def get_card_by_id(card_id: str) -> Dict[str, Any]:
    """Retrieve a card by card_id"""
    query = "SELECT * FROM cards WHERE card_id = %s;"
    results = execute_query(query, (card_id,))
    return results[0] if results else None

def get_deck_by_id(deck_id: int) -> Dict[str, Any]:
    """Retrieve a deck by deck_id"""
    query = "SELECT * FROM decks WHERE deck_id = %s;"
    results = execute_query(query, (deck_id,))
    return results[0] if results else None

def get_snapshot_by_id(snapshot_id: int) -> Dict[str, Any]:
    """Retrieve a snapshot by snapshot_id"""
    query = "SELECT * FROM snapshots WHERE snapshot_id = %s;"
    results = execute_query(query, (snapshot_id,))
    return results[0] if results else None

def get_library_cards_by_snapshot(snapshot_id: int) -> List[Dict[str, Any]]:
    """Retrieve all library cards associated with a snapshot"""
    query = "SELECT * FROM library_cards WHERE snapshot_id = %s;"
    return execute_query(query, (snapshot_id,))

# Additional complex retrieval functions can be added as needed
