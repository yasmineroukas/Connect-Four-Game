from flask import Flask, request, jsonify, send_from_directory
import random
import os
from heuristic import evaluate_board

# Configuration simplifiée de Flask
app = Flask(__name__)

# Constants
PLAYER1 = 1
PLAYER2 = 2
EMPTY = 0
ROWS = 6
COLS = 7

# Game state
board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
current_player = PLAYER1

# Utility functions for game logic
def is_column_full(column):
    """Check if the column is full."""
    return board[0][column] != EMPTY

def make_move(column, player):
    """Make a move in the given column for the player."""
    for row in range(ROWS-1, -1, -1):
        if board[row][column] == EMPTY:
            board[row][column] = player
            return row, column
    return None

def check_win(player):
    """Check if the given player has won."""
    # Horizontal, Vertical, Diagonal check
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == player:
                if check_direction(r, c, 1, 0, player) or \
                   check_direction(r, c, 0, 1, player) or \
                   check_direction(r, c, 1, 1, player) or \
                   check_direction(r, c, 1, -1, player):
                    return True
    return False

def check_direction(row, col, d_row, d_col, player):
    """Check in a specific direction for 4 in a row."""
    count = 1  # Count the starting position
    
    # Check forward
    for i in range(1, 4):
        r, c = row + i * d_row, col + i * d_col
        if r < 0 or r >= ROWS or c < 0 or c >= COLS or board[r][c] != player:
            break
        count += 1
    
    # Check backward
    for i in range(1, 4):
        r, c = row - i * d_row, col - i * d_col
        if r < 0 or r >= ROWS or c < 0 or c >= COLS or board[r][c] != player:
            break
        count += 1
    
    return count >= 4

def is_draw():
    """Check if the game is a draw."""
    return all(board[0][col] != EMPTY for col in range(COLS))

def ai_move():
    """AI makes its move using minimax with heuristic evaluation."""
    available_columns = [c for c in range(COLS) if not is_column_full(c)]
    
    if not available_columns:
        return None
    
    # Use heuristic to evaluate best move
    best_score = -float('inf')
    best_column = available_columns[0]
    
    for col in available_columns:
        # Try move
        row = None
        for r in range(ROWS-1, -1, -1):
            if board[r][col] == EMPTY:
                row = r
                board[r][col] = PLAYER2
                break
        
        # Evaluate move
        score = evaluate_board(board, PLAYER2)
        
        # Undo move
        board[row][col] = EMPTY
        
        # Update best move
        if score > best_score:
            best_score = score
            best_column = col
    
    return best_column

def reset_game():
    """Reset the game state."""
    global board, current_player
    board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
    current_player = PLAYER1

# Routes pour servir les fichiers statiques
@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

@app.route('/<path:filename>', methods=['GET'])
def serve_static(filename):
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), filename)

# Routes API
@app.route('/move', methods=['POST'])
def move():
    global current_player
    data = request.get_json()
    column = data.get('column')
    player = data.get('player')

    # Validation
    if column is None or player is None:
        return jsonify({'status': 'invalid', 'message': 'Missing column or player'}), 400
    if column < 0 or column >= COLS:
        return jsonify({'status': 'invalid', 'message': 'Invalid column'}), 400
    if is_column_full(column):
        return jsonify({'status': 'invalid', 'message': 'Column is full'}), 400
    
    # Make move for human player
    row, col = make_move(column, player)
    
    # Check if human player won
    if check_win(player):
        return jsonify({
            'board': board,
            'status': 'win',
            'winner': player
        })

    # Check for draw
    if is_draw():
        return jsonify({
            'board': board,
            'status': 'draw'
        })
    
    # AI's turn
    current_player = PLAYER2 if player == PLAYER1 else PLAYER1
    ai_column = ai_move()
    ai_row, ai_col = make_move(ai_column, current_player)
    
    response_data = {
        'board': board,
        'ai_move': ai_column,
        'status': 'continue',
        'current_player': PLAYER1  # After AI plays, it's human's turn again
    }
    
    # Check if AI won
    if check_win(current_player):
        response_data['status'] = 'win'
        response_data['winner'] = current_player
    # Check for draw after AI move
    elif is_draw():
        response_data['status'] = 'draw'
    
    current_player = PLAYER1  # Reset to human player
    
    return jsonify(response_data)

@app.route('/reset', methods=['POST'])
def reset():
    """Reset the game."""
    reset_game()
    return jsonify({
        'board': board,
        'current_player': current_player,
        'status': 'continue'
    })

@app.route('/state', methods=['GET'])
def state():
    """Return the current game state."""
    return jsonify({
        'board': board,
        'current_player': current_player,
        'status': 'continue' if not check_win(PLAYER1) and not check_win(PLAYER2) and not is_draw() else 'end'
    })

if __name__ == '__main__':
    print("Jeu connect four démarré!")
    print("Ouvrez votre navigateur à l'adresse: http://127.0.0.1:5000")
    app.run(debug=True)