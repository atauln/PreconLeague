# Precon League Front-End

A makeshift front-end for the Precon League application with a simple login screen and deck preview functionality.

## Features

- **Simple Login**: No password required, just enter your username
- **Deck Input**: Paste your decklist in various formats
- **Deck Preview**: View your parsed decklist with commander detection and card count

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The application uses environment variables for configuration:

- `FLASK_SECRET_KEY`: Secret key for session management (required for production)
- `FLASK_DEBUG`: Set to `0` to disable debug mode in production (default: `1`)

For production deployment:
```bash
export FLASK_SECRET_KEY="your-secure-random-secret-key"
export FLASK_DEBUG=0
```

## Running the Application

1. Start the Flask server:
```bash
python3 app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Login
1. Enter your username in the login screen
2. Click "Continue" to proceed to the deck page

### Deck Preview
1. Paste your decklist in the text area
   - Supported formats:
     - `1 Card Name`
     - `1x Card Name`
     - `Card Name` (assumes quantity of 1)
2. Click "Preview Deck" to parse and display your decklist
3. The preview will show:
   - Commander (automatically detected as the first card)
   - Total card count
   - Complete decklist with quantities

### Logout
- Click the "Logout" button in the top right to return to the login screen

## Deck Format Examples

```
1 Anikthea, Hand of Erebos
1 Sol Ring
1 Command Tower
1 Arcane Signet
...
```

or

```
1x Lightning Greaves
1x Swiftfoot Boots
...
```

## Technical Details

- **Framework**: Flask (Python web framework)
- **Frontend**: HTML, CSS, JavaScript
- **Session Management**: Flask sessions for user authentication
- **Deck Parsing**: Regular expression-based parser supporting multiple formats

## Notes

- This is a makeshift solution for quick deck previews
- No data is persisted to the database in the current implementation
- The application runs in debug mode by default (not suitable for production)
