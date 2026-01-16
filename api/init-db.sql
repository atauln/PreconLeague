
--Drop existing tables if they exist to start fresh
DROP TABLE IF EXISTS library_cards;
DROP TABLE IF EXISTS snapshots;
DROP TABLE IF EXISTS decks;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS cards;

DROP TYPE IF EXISTS source;


--Create various tables needed for the application
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    user_name TEXT NOT NULL UNIQUE
);

CREATE TABLE cards (
    oracle_card_id TEXT NOT NULL PRIMARY KEY,
    card_name TEXT NOT NULL
);

CREATE TYPE source AS ENUM ('moxfield', 'archidekt');

CREATE TABLE decks (
    deck_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    moxfield_deck_url TEXT UNIQUE,
    archidekt_deck_url TEXT UNIQUE,
    source source NOT NULL,
    deck_name TEXT NOT NULL,
    CHECK (
        (source = 'moxfield' AND moxfield_deck_url IS NOT NULL AND archidekt_deck_url IS NULL) OR
        (source = 'archidekt' AND archidekt_deck_url IS NOT NULL AND moxfield_deck_url IS NULL)
    )
);

CREATE TABLE snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    deck_id INTEGER REFERENCES decks(deck_id),
    commander_id TEXT REFERENCES cards(oracle_card_id),  -- The commander could switch between snapshots
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    salt_rating DECIMAL,
    synergy_rating DECIMAL,
    power_level_rating DECIMAL,
    threat_rating DECIMAL,
    bracket_rating DECIMAL,
    overall_rating DECIMAL,
    manabase_score DECIMAL,
    power_level_display_value INT,
    combo_rating DECIMAL,
    archetype_minor TEXT,
    archetype_major TEXT,
    price_usd DECIMAL,
    week_of_league INTEGER,
    mana_fixing_score DECIMAL,
    competitive_intent DECIMAL,
    commander_tier DECIMAL,
    card_quality DECIMAL
);

CREATE TABLE library_cards (
    library_card_id SERIAL PRIMARY KEY,
    snapshot_id INTEGER REFERENCES snapshots(snapshot_id),
    card_id TEXT REFERENCES cards(oracle_card_id)
);

--Indexes for performance optimization
--Composite unique constraint on (snapshot_id, card_id) automatically creates an index
--Index on card_id for reverse lookups (finding which snapshots contain a card)
CREATE INDEX idx_library_card ON library_cards(card_id);
