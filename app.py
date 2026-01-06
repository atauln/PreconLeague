from flask import Flask, render_template, request, jsonify, session
import re
import os
from typing import List, Dict, Tuple

app = Flask(__name__)
# Use environment variable for secret key in production
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'preconleague-secret-key-dev-only')

def parse_decklist(decklist_text: str) -> Tuple[str, List[Dict[str, any]]]:
    """
    Parse a decklist in various formats and return commander and card list.
    Expected format examples:
    - "1 Card Name"
    - "1x Card Name"
    - "Card Name"
    """
    lines = decklist_text.strip().split('\n')
    cards = []
    commander = None
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('//'):
            continue
        
        # Try to parse "1 Card Name" or "1x Card Name" format
        match = re.match(r'^(\d+)x?\s+(.+)$', line)
        if match:
            quantity = int(match.group(1))
            card_name = match.group(2).strip()
        else:
            # Just a card name without quantity
            quantity = 1
            card_name = line
        
        # Simple heuristic: first card or card with "Commander" in line is the commander
        if commander is None or 'commander' in line.lower():
            commander = card_name
        
        cards.append({
            'name': card_name,
            'quantity': quantity
        })
    
    return commander, cards

@app.route('/')
def index():
    """Main landing page with login"""
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle login (just username, no password)"""
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    # Store username in session
    session['username'] = username
    
    return jsonify({'success': True, 'username': username})

@app.route('/deck')
def deck_page():
    """Deck input and preview page"""
    if 'username' not in session:
        return render_template('index.html')
    
    return render_template('deck.html', username=session['username'])

@app.route('/parse_deck', methods=['POST'])
def parse_deck():
    """Parse deck text and return structured data"""
    data = request.get_json()
    decklist_text = data.get('decklist', '')
    
    if not decklist_text:
        return jsonify({'error': 'Decklist is required'}), 400
    
    try:
        commander, cards = parse_decklist(decklist_text)
        
        return jsonify({
            'success': True,
            'commander': commander,
            'cards': cards,
            'total_cards': sum(card['quantity'] for card in cards)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    """Handle logout"""
    session.clear()
    return jsonify({'success': True})

if __name__ == '__main__':
    # Debug mode should be disabled in production
    # Set environment variable FLASK_DEBUG=0 to disable debug mode
    import os
    debug_mode = os.getenv('FLASK_DEBUG', '1') == '1'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
