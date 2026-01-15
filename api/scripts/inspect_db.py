#!/usr/bin/env python3
"""
Inspect DB schema and index/constraint state for `library_cards` and related tables.

Usage:
  python3 -m api.scripts.inspect_db

This will load DB settings from `api/.env` and print:
 - Columns for `library_cards` and `snapshots`
 - Any constraints for `library_cards` (including UNIQUE)
 - Indexes on `library_cards`
 - Row counts and top (snapshot_id, card_id) groups

Helpful to diagnose why pg_restore or migration scripts may have failed.
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
API_DIR = os.path.dirname(SCRIPT_DIR)
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

env_path = os.path.join(API_DIR, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

import asyncpg

DB_CONFIG = {
    'host': os.getenv('PSQL_HOST', 'localhost'),
    'port': int(os.getenv('PSQL_PORT', '5432')),
    'database': os.getenv('PSQL_DB', ''),
    'user': os.getenv('PSQL_USER', ''),
    'password': os.getenv('PSQL_PASSWORD', '')
}

async def inspect():
    if not DB_CONFIG['database'] or not DB_CONFIG['user']:
        print('PSQL_DB and PSQL_USER must be set in api/.env or environment')
        return
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
    except Exception as e:
        print('Failed to connect to DB:', e)
        return
    try:
        print('\n-- library_cards columns --')
        cols = await conn.fetch("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='library_cards' ORDER BY ordinal_position;")
        for r in cols:
            print(r['column_name'], r['data_type'])

        print('\n-- snapshots columns --')
        cols = await conn.fetch("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='snapshots' ORDER BY ordinal_position;")
        for r in cols:
            print(r['column_name'], r['data_type'])

        print('\n-- table constraints (pg_constraint) for library_cards --')
        cons = await conn.fetch("SELECT conname, contype, pg_get_constraintdef(oid) as def FROM pg_constraint WHERE conrelid = 'library_cards'::regclass ORDER BY contype, conname;")
        if cons:
            for c in cons:
                print(c['conname'], c['contype'], c['def'])
        else:
            print('  (no constraints found)')

        print('\n-- indexes for library_cards --')
        idxs = await conn.fetch("SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'library_cards';")
        if idxs:
            for i in idxs:
                print(i['indexname'], i['indexdef'])
        else:
            print('  (no indexes found)')

        print('\n-- library_cards counts --')
        cnt = await conn.fetchval('SELECT COUNT(*) FROM library_cards;')
        print('total rows in library_cards:', cnt)

        print('\n-- top (snapshot_id, card_id) groups --')
        groups = await conn.fetch("SELECT snapshot_id, card_id, COUNT(*) as qty FROM library_cards GROUP BY snapshot_id, card_id ORDER BY qty DESC LIMIT 20;")
        for g in groups:
            print(g['snapshot_id'], g['card_id'], g['qty'])

    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(inspect())
