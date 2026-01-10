# PreconLeague API

Internal API for @atauln's MTG Preconstructed Deck League

## Overview

This is a FastAPI-based REST API for managing MTG (Magic: The Gathering) preconstructed deck leagues. It supports deck tracking from Moxfield and Archidekt, snapshot management, and integration with Commander Salt for deck analysis.

## Features

- **User Management**: Create and manage users
- **Deck Management**: Register decks from Moxfield or Archidekt
- **Snapshot System**: Track deck evolution over time
- **Card Database**: Store and retrieve card information
- **Commander Salt Integration**: Fetch deck ratings and analysis

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with asyncpg
- **External APIs**: Moxfield, Archidekt, Commander Salt
- **Testing**: pytest with coverage reporting

## Installation

1. Clone the repository:
```bash
git clone https://github.com/atauln/PreconLeague.git
cd PreconLeague
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r api/requirements.txt
```

4. Set up environment variables:
```bash
cp api/.env.template api/.env
# Edit api/.env with your database credentials
```

5. Initialize the database:
```bash
cd api
python db.py
```

## Running the API

Start the development server:
```bash
cd api
python api.py
```

The API will be available at `http://localhost:8000`

Access the interactive API documentation at `http://localhost:8000/docs`

## Testing

### Running Tests Locally

The project uses pytest for testing. All tests are located in the `tests/` directory.

**Run all tests:**
```bash
pytest
```

**Run tests with coverage:**
```bash
pytest --cov=api --cov-report=term-missing
```

**Run tests with detailed output:**
```bash
pytest -v
```

**Run tests with coverage HTML report:**
```bash
pytest --cov=api --cov-report=html
# Open htmlcov/index.html in your browser
```

**Run specific test file:**
```bash
pytest tests/test_models.py
```

**Run tests matching a pattern:**
```bash
pytest -k "test_user"
```

### Test Structure

- `tests/test_models.py` - Tests for data models (Card, Deck, CommanderSaltData)
- `tests/test_db.py` - Tests for database functions
- `tests/test_routers.py` - Tests for API endpoints
- `tests/test_archidekt.py` - Tests for Archidekt integration
- `tests/conftest.py` - Shared fixtures and configuration

### CI/CD Pipeline

The project includes a GitHub Actions workflow that automatically runs tests on:
- Every push to the `main` branch
- Every pull request targeting the `main` branch

**Workflow features:**
- Tests on Python 3.11 and 3.12
- Automatic dependency caching
- Code coverage reporting
- Test result summaries in PR checks
- Basic linting with flake8

**Viewing test results:**
1. Navigate to the "Actions" tab in the GitHub repository
2. Click on a workflow run to see detailed results
3. Check the "Run Tests" job for test output and coverage
4. Pull requests will show test status in the checks section

**Coverage reports:**
- Coverage is automatically uploaded to Codecov (if configured)
- Coverage summary appears in the GitHub Actions workflow summary
- HTML coverage reports are generated but not uploaded (run locally to view)

## API Endpoints

### Users
- `GET /users/` - Get all users
- `GET /users/{user_id}` - Get user by ID
- `POST /users/` - Create a new user

### Decks
- `GET /decks/` - Get all decks
- `GET /decks/{deck_id}` - Get deck by ID
- `GET /decks/user/{user_id}` - Get all decks for a user
- `POST /decks/` - Register a new deck

### Snapshots
- `GET /snapshots/` - Get all snapshots
- `GET /snapshots/{snapshot_id}` - Get snapshot by ID
- `GET /snapshots/deck/{deck_id}` - Get all snapshots for a deck
- `GET /snapshots/with_library/{snapshot_id}` - Get snapshot with library cards
- `POST /snapshots/create_snapshot/{deck_id}` - Create a new snapshot

### Cards
- `GET /cards/` - Get all cards
- `GET /cards/{card_id}` - Get card by ID
- `POST /cards/` - Create a new card
- `POST /cards/associate` - Associate a card with a snapshot

## Database Schema

The application uses PostgreSQL with the following main tables:
- `users` - User information
- `cards` - MTG card data
- `decks` - Deck information with source URLs
- `snapshots` - Deck snapshots with ratings and metrics
- `library_cards` - Association between snapshots and cards

## Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Keep functions focused and testable
- Write tests for new functionality

### Testing Conventions
- Use `pytest` for all tests
- Mock external API calls and database connections
- Use `@pytest.mark.asyncio` for async tests
- Organize tests in classes by functionality
- Use descriptive test names that explain what is being tested

### Contributing
1. Create a feature branch
2. Write tests for new functionality
3. Ensure all tests pass locally
4. Submit a pull request
5. Wait for CI checks to pass
6. Address any review feedback

## License

This project is for personal use by @atauln.

## Author

**@atauln** - [GitHub Profile](https://github.com/atauln)
