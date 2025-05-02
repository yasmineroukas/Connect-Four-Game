def evaluate_board(board, player):
    """
    Evaluate the board for the given player.
    Returns a score: higher is better for the player.
    """
    opponent = 1 if player == 2 else 2
    score = 0
    rows, cols = 6, 7

    # Heuristic weights
    center_bonus = 3
    three_in_row = 5
    two_in_row = 2
    one_in_row = 0.5

    # Bonus for controlling the center
    center_column = [row[3] for row in board]
    center_count = center_column.count(player)
    score += center_count * center_bonus

    # Helper function: count groups in a sequence of 4 cells
    def count_group(group):
        count = group.count(player)
        opponent_count = group.count(opponent)
        empty_count = group.count(0)
        
        if count == 4:
            return 100  # Winning position
        elif count == 3 and empty_count == 1:
            return three_in_row
        elif count == 2 and empty_count == 2:
            return two_in_row
        elif count == 1 and empty_count == 3:
            return one_in_row
        elif opponent_count == 3 and empty_count == 1:
            return -10  # Block opponent's potential win
        elif opponent_count == 2 and empty_count == 2:
            return -3   # Block opponent's potential threat
        return 0

    # Horizontal
    for row in range(rows):
        for col in range(cols - 3):
            window = [board[row][col+i] for i in range(4)]
            score += count_group(window)

    # Vertical
    for col in range(cols):
        for row in range(rows - 3):
            window = [board[row+i][col] for i in range(4)]
            score += count_group(window)

    # Diagonals ↘
    for row in range(rows - 3):
        for col in range(cols - 3):
            window = [board[row+i][col+i] for i in range(4)]
            score += count_group(window)

    # Diagonals ↙
    for row in range(rows - 3):
        for col in range(3, cols):
            window = [board[row+i][col-i] for i in range(4)]
            score += count_group(window)

    return score