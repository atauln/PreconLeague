import asyncpg
import requests

from dotenv import load_dotenv
import os
load_dotenv()

from models import Decklist

def get_db_connection():
    return asyncpg.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )

def get_card_name_by_id(card_id: int) -> str | None:
    try:
        response = requests.get(f"https://api.scryfall.com/cards/{card_id}")
        response.raise_for_status()
        card_data = response.json()
        return card_data.get("name")
    except requests.RequestException as e:
        print(f"Error fetching card name for card ID {card_id}: {e}")
        return None

async def get_most_recent_snapshot_id(deck_id: int) -> int | None:
    conn = await get_db_connection()
    try:
        snapshot = await conn.fetchrow(
            "SELECT snapshot_id FROM snapshots WHERE deck_id = $1 ORDER BY created_at DESC LIMIT 1",
            deck_id
        )
        return int(snapshot[0])
    except Exception as e:
        print(f"Error fetching most recent snapshot ID for deck {deck_id}: {e}")
        return None
    finally:
        await conn.close()

async def get_most_recent_decklist(deck_id: int) -> Decklist | None:
    conn = await get_db_connection()
    try:
        most_recent_snap_id = await get_most_recent_snapshot_id(deck_id)
        if most_recent_snap_id is None:
            print(f"No snapshots found for deck {deck_id}")
            return None
        snapshot = await conn.fetch(
            "SELECT card_name FROM library_cards" \
            " JOIN snapshots ON library_cards.snapshot_id = snapshots.snapshot_id" \
            " JOIN cards ON library_cards.card_id = cards.oracle_card_id" \
            " WHERE snapshots.snapshot_id = $1",
            most_recent_snap_id
        )
        decklist = [snapshot[i][0] for i in range(len(snapshot))]

        # get commander
        commander = await conn.fetchrow(
            """
            SELECT commander_id FROM snapshots
            WHERE snapshot_id = $1
            """,
            most_recent_snap_id
        )

        if commander and commander[0] is not None:
            commander_name = get_card_name_by_id(commander[0])
        else:
            print(f"No commander found for snapshot {most_recent_snap_id}")

        return Decklist(commander=commander_name if commander else "Unknown", cards=decklist)
    except Exception as e:
        print(f"Error fetching most recent decklist for deck {deck_id}: {e}")
        return None
    finally:
        await conn.close()

if __name__ == "__main__":
    import asyncio
    deck_id = 1  # Example deck ID
    decklist = asyncio.run(get_most_recent_decklist(deck_id))
    if decklist:
        print(f"Most recent decklist for deck {deck_id}:\n{decklist}")
    else:
        print(f"No decklist found for deck {deck_id}.")