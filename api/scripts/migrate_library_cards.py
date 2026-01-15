#!/usr/bin/env python3
"""
Migration script to add a `quantity` column to `library_cards` and collapse
multiple duplicate rows into a single row per (snapshot_id, card_id) with the
correct quantity.

Usage:
  python3 scripts/migrate_library_cards.py --dry-run        # preview changes
  python3 scripts/migrate_library_cards.py --apply --yes   # apply changes

The script reads DB connection info from environment variables (same names
used by the project): PSQL_HOST, PSQL_PORT, PSQL_DB, PSQL_USER, PSQL_PASSWORD.
#!/usr/bin/env python3
"""

import os
import sys
import argparse
import asyncio
from dotenv import load_dotenv

# Ensure `api/` is on sys.path so relative imports like `from db import ...` work
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
API_DIR = os.path.dirname(SCRIPT_DIR)
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

# Load .env from api/ if present
env_path = os.path.join(API_DIR, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

from db import get_connection, get_cards_by_ids, create_cards_bulk, associate_cards_with_snapshot_bulk
from db import get_deck_by_id
from funcs.moxfield import fetch_moxfield_deck
from funcs.archidekt import fetch_archidekt_deck

CARD_NAMES_TO_UPDATE = set([
    'Plains',
    'Island',
    'Swamp',
    'Mountain',
    'Forest',
    'Wastes',
    'Snow-Covered Plains',
    'Snow-Covered Island',
    'Snow-Covered Swamp',
    'Snow-Covered Mountain',
    'Snow-Covered Forest',
    'Snow-Covered Wastes'
])  # basic set of card IDs known to be duplicated


async def process_snapshot(conn, snapshot_id: int, apply: bool):
    row = await conn.fetchrow("SELECT deck_id FROM snapshots WHERE snapshot_id = $1", snapshot_id)
    if not row:
        print(f"Snapshot {snapshot_id} not found; skipping")
        return
    deck_id = row['deck_id']

    deck = await get_deck_by_id(deck_id)
    if not deck:
        print(f"Deck {deck_id} not found for snapshot {snapshot_id}; skipping")
        return

    source = deck.get('source')
    source_deck_url = deck.get('moxfield_deck_url') if source == 'moxfield' else deck.get('archidekt_deck_url')

    if source == 'moxfield':
        proc_deck = fetch_moxfield_deck(source_deck_url)
    elif source == 'archidekt':
        proc_deck = fetch_archidekt_deck(source_deck_url)
    else:
        print(f"Deck {deck_id} has unknown source '{source}'; skipping")
        return

    if not proc_deck or not getattr(proc_deck, 'library', None):
        print(f"No library data for deck {deck_id} (snapshot {snapshot_id}); skipping")
        return

    # Compute quantities from proc_deck.library
    counts = {}
    names = {}
    for card in proc_deck.library:
        cid = getattr(card, 'id', None)
        if cid is None:
            continue
        qty = getattr(card, 'quantity', None)
        qty = qty if isinstance(qty, int) and qty > 0 else 1
        counts[cid] = counts.get(cid, 0) + qty
        names[cid] = getattr(card, 'name', '')

    total_copies = sum(counts.values())
    print(f"Snapshot {snapshot_id}: {len(counts)} distinct cards, total copies {total_copies}")

    if not apply:
        # show a sample
        for cid, qty in list(counts.items())[:20]:
            print(f"  {cid}: {qty}")
        return

    # Ensure there is no UNIQUE constraint on (snapshot_id, card_id)
    # Try to find and drop any unique constraint on the table before modifying rows.
    try:
        con_rows = await conn.fetch(
            "SELECT conname FROM pg_constraint WHERE conrelid = 'library_cards'::regclass AND contype = 'u';"
        )
        for r in con_rows:
            conname = r['conname']
            print(f"Dropping unique constraint {conname} on library_cards...")
            await conn.execute(f"ALTER TABLE library_cards DROP CONSTRAINT {conname};")
    except Exception:
        # If something goes wrong here, continue — constraint may not exist or permissions may vary.
        pass
    # Also drop unique indexes that might enforce uniqueness on (snapshot_id, card_id)
    try:
        idx_rows = await conn.fetch(
            "SELECT indexname FROM pg_indexes WHERE tablename = 'library_cards' AND indexdef LIKE '%UNIQUE%' AND indexdef LIKE '%snapshot_id%' AND indexdef LIKE '%card_id%';"
        )
        for r in idx_rows:
            idxname = r['indexname']
            print(f"Dropping unique index {idxname} on library_cards...")
            await conn.execute(f"DROP INDEX IF EXISTS {idxname};")
    except Exception:
        pass

    # Only update the small set of card NAMES we want to touch (e.g., basic lands).
    # Aggregate counts by name and act only on names in CARD_NAMES_TO_UPDATE.
    counts_by_name = {}
    example_id_by_name = {}
    for cid, name in names.items():
        qty = counts.get(cid, 0)
        if not name:
            continue
        counts_by_name[name] = counts_by_name.get(name, 0) + qty
        if cid and name not in example_id_by_name:
            example_id_by_name[name] = cid

    filtered_counts = {name: qty for name, qty in counts_by_name.items() if name in CARD_NAMES_TO_UPDATE}

    if not filtered_counts:
        print(f"No matching CARD_NAMES_TO_UPDATE present in snapshot {snapshot_id}; leaving rows intact.")
        return

    target_names = list(filtered_counts.keys())

    # Look up existing card rows by name
    rows = await conn.fetch("SELECT oracle_card_id, card_name FROM cards WHERE card_name = ANY($1)", target_names)
    name_to_db_ids = {}
    for r in rows:
        name_to_db_ids.setdefault(r['card_name'], []).append(r['oracle_card_id'])

    # For names missing from DB, create cards using an example oracle id if available
    to_create = []
    for name in target_names:
        if name not in name_to_db_ids:
            example_id = example_id_by_name.get(name)
            if example_id:
                to_create.append((example_id, name))
                name_to_db_ids.setdefault(name, []).append(example_id)
            else:
                print(f"Warning: no oracle id available to create card row for name '{name}'; skipping this name.")

    if to_create:
        print(f"Creating {len(to_create)} missing card rows for target names...")
        await create_cards_bulk(to_create)

    # Collect all db card ids that correspond to our target names
    db_card_ids = []
    for ids in name_to_db_ids.values():
        db_card_ids.extend(ids)

    if not db_card_ids:
        print(f"No card ids found or created for target names in snapshot {snapshot_id}; nothing to do.")
        return

    # Delete only existing library rows for these card IDs for this snapshot
    print(f"Clearing existing library rows for snapshot {snapshot_id} for {len(db_card_ids)} card ids (by name)...")
    await conn.execute(
        "DELETE FROM library_cards WHERE snapshot_id = $1 AND card_id::text = ANY($2::text[])",
        snapshot_id,
        db_card_ids,
    )

    # Insert rows: pick a canonical oracle id per name (first db id) and insert repeated rows equal to aggregated qty
    repeated_ids = []
    for name, qty in filtered_counts.items():
        ids_for_name = name_to_db_ids.get(name)
        if not ids_for_name:
            continue
        chosen_id = ids_for_name[0]
        repeated_ids.extend([chosen_id] * qty)

    if repeated_ids:
        print(f"Inserting {len(repeated_ids)} rows (by name) for snapshot {snapshot_id}...")
        await associate_cards_with_snapshot_bulk(snapshot_id, repeated_ids)
    else:
        print(f"No filtered cards to insert for snapshot {snapshot_id}.")


async def main_async(args):
    conn = await get_connection()
    if not conn:
        print("Unable to connect to DB; aborting")
        return
    try:
        if args.snapshot:
            await process_snapshot(conn, args.snapshot, args.apply)
        else:
            rows = await conn.fetch("SELECT snapshot_id FROM snapshots ORDER BY snapshot_id")
            print(f"Found {len(rows)} snapshots")
            for r in rows:
                await process_snapshot(conn, r['snapshot_id'], args.apply)
    finally:
        await conn.close()


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--snapshot', type=int, help='Process a single snapshot id')
    p.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    p.add_argument('--dry-run', action='store_true', help='Explicitly run in dry-run mode (no changes)')
    p.add_argument('--yes', action='store_true', help='Auto-confirm')
    return p.parse_args()


def main():
    args = parse_args()
    # Validate flags: --dry-run and --apply are mutually exclusive
    if getattr(args, 'dry_run', False) and args.apply:
        print('Error: --dry-run and --apply are mutually exclusive')
        return
    if args.apply and not args.yes:
        confirm = input('This will modify the database. Type YES to continue: ')
        if confirm != 'YES':
            print('Aborting.')
            return
    asyncio.run(main_async(args))


if __name__ == '__main__':
    main()
