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