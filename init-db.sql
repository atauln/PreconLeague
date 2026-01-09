
--Drop existing tables if they exist to start fresh
DROP TABLE IF EXISTS library_cards;
DROP TABLE IF EXISTS snapshots;
DROP TABLE IF EXISTS decks;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS cards;


--Create various tables needed for the application
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    user_name TEXT NOT NULL UNIQUE
);

CREATE TABLE cards (
    oracle_card_id TEXT NOT NULL PRIMARY KEY,
    card_name TEXT NOT NULL
);

CREATE TABLE decks (
    deck_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    moxfield_deck_id TEXT NOT NULL UNIQUE,
    archidekt_deck_id INTEGER NOT NULL UNIQUE,
    source ENUM('moxfield', 'archidekt') NOT NULL,
    deck_name TEXT NOT NULL
);

CREATE TABLE snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    deck_id INTEGER REFERENCES decks(deck_id),
    commander_id TEXT REFERENCES cards(card_id),  -- The commander could switch between snapshots
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    est_power DECIMAL
);

CREATE TABLE library_cards (
    library_card_id SERIAL PRIMARY KEY,
    snapshot_id INTEGER REFERENCES snapshots(snapshot_id),
    card_id TEXT REFERhttps://github.com/atauln/PreconLeague/blob/main/api/funcs/archidekt.pyENCES cards(card_id)
);

--Indexes for performance optimization

--Index on snapshot_id as it's frequently queried for each card in the library
CREATE INDEX idx_library_snapshot ON library_cards(snapshot_id);
