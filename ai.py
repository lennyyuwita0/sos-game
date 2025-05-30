"""
SOS Game AI Logic - INSTANT VERSION
AI yang memberikan respons instant tanpa delay
"""

import random
from player import Player

class AIPlayer(Player):
    """AI Player with instant response - NO DELAYS"""
    
    def __init__(self, name="AI", difficulty="medium"):
        super().__init__(name)
        self.difficulty = difficulty
    
    def get_move(self, board):
        """Get AI's next move - INSTANT NO THINKING TIME"""
        empty_cells = board.get_empty_cells()
        
        if not empty_cells:
            return None, None, None
        
        # INSTANT Step 1: Check for immediate win (first 3 cells only)
        for i, (row, col) in enumerate(empty_cells):
            if i >= 3:  # Only check first 3 positions
                break
                
            # Quick win check without board copy
            if self._can_win_here(board, row, col, 'S'):
                return row, col, 'S'
            if self._can_win_here(board, row, col, 'O'):
                return row, col, 'O'
        
        # INSTANT Step 2: Quick block (only if hard mode)
        if self.difficulty == "hard":
            for i, (row, col) in enumerate(empty_cells):
                if i >= 2:  # Only check first 2 positions
                    break
                if self._should_block_here(board, row, col):
                    return row, col, random.choice(['S', 'O'])
        
        # INSTANT Step 3: Strategic positioning
        move = self._get_quick_strategic_move(board, empty_cells)
        if move:
            return move
        
        # INSTANT Step 4: Random fallback
        row, col = random.choice(empty_cells)
        letter = random.choice(['S', 'O'])
        return row, col, letter
    
    def _can_win_here(self, board, row, col, letter):
        """Check if placing letter here creates SOS - NO BOARD COPY"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # horizontal, vertical, diagonal
        
        for dr, dc in directions:
            if self._check_sos_pattern(board, row, col, letter, dr, dc):
                return True
        return False
    
    def _check_sos_pattern(self, board, row, col, letter, dr, dc):
        """Check SOS pattern in one direction - ULTRA FAST"""
        if letter == 'S':
            # S at start: S-O-S
            if (self._valid_and_equals(board, row + dr, col + dc, 'O') and
                self._valid_and_equals(board, row + 2*dr, col + 2*dc, 'S')):
                return True
            # S at end: S-O-S
            if (self._valid_and_equals(board, row - dr, col - dc, 'O') and
                self._valid_and_equals(board, row - 2*dr, col - 2*dc, 'S')):
                return True
        
        elif letter == 'O':
            # O in middle: S-O-S
            if (self._valid_and_equals(board, row - dr, col - dc, 'S') and
                self._valid_and_equals(board, row + dr, col + dc, 'S')):
                return True
        
        return False
    
    def _valid_and_equals(self, board, row, col, expected):
        """Check if position is valid and has expected value"""
        return (board._is_valid_pos(row, col) and 
                board.get_cell(row, col) == expected)
    
    def _should_block_here(self, board, row, col):
        """Quick check if opponent can win here"""
        return (self._can_win_here(board, row, col, 'S') or 
                self._can_win_here(board, row, col, 'O'))
    
    def _get_quick_strategic_move(self, board, empty_cells):
        """Get strategic move instantly"""
        if not empty_cells:
            return None
        
        center = board.size // 2
        
        # Priority 1: Center (if available)
        if (center, center) in empty_cells:
            letter = self._quick_letter_choice(board, center, center)
            return center, center, letter
        
        # Priority 2: Near center (1 cell away)
        for row, col in empty_cells:
            if abs(row - center) <= 1 and abs(col - center) <= 1:
                letter = self._quick_letter_choice(board, row, col)
                return row, col, letter
        
        # Priority 3: Corners
        corners = [(0, 0), (0, board.size-1), (board.size-1, 0), (board.size-1, board.size-1)]
        for row, col in corners:
            if (row, col) in empty_cells:
                letter = self._quick_letter_choice(board, row, col)
                return row, col, letter
        
        # Priority 4: Edges
        for row, col in empty_cells:
            if (row == 0 or row == board.size-1 or 
                col == 0 or col == board.size-1):
                letter = self._quick_letter_choice(board, row, col)
                return row, col, letter
        
        # Priority 5: Any remaining cell
        row, col = empty_cells[0]
        letter = self._quick_letter_choice(board, row, col)
        return row, col, letter
    
    def _quick_letter_choice(self, board, row, col):
        """Instant letter selection based on neighbors"""
        s_count = 0
        o_count = 0
        
        # Only check 4 main directions for speed
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if board._is_valid_pos(nr, nc):
                cell = board.get_cell(nr, nc)
                if cell == 'S':
                    s_count += 1
                elif cell == 'O':
                    o_count += 1
        
        # Quick decision
        if s_count > o_count:
            return 'O'  # Balance with O
        elif o_count > s_count:
            return 'S'  # Balance with S
        else:
            return 'S' if random.random() > 0.5 else 'O'  # Random when equal
    
    def set_difficulty(self, difficulty):
        """Set AI difficulty level"""
        if difficulty in ["easy", "medium", "hard"]:
            self.difficulty = difficulty
    
    def get_difficulty(self):
        """Get current difficulty level"""
        return self.difficulty
    
    def get_stats(self):
        """Get AI player statistics"""
        return {
            'name': self.name,
            'score': self.score,
            'type': 'AI',
            'difficulty': self.difficulty
        }
    
    def suggest_move(self, board):
        """Suggest a move with explanation"""
        move = self.get_move(board)
        if not move or move[0] is None:
            return None, "No valid moves available"
        
        row, col, letter = move
        explanation = f"AI plays {letter} at position ({row+1},{col+1})"
        
        return move, explanation
    
    def analyze_board(self, board):
        """Quick board analysis"""
        empty_cells = len(board.get_empty_cells())
        total_cells = board.size * board.size
        
        return {
            'empty_cells': empty_cells,
            'completion_percentage': ((total_cells - empty_cells) / total_cells * 100)
        }
    
    def __str__(self):
        return f"InstantAI ({self.difficulty})"

# Untuk backward compatibility
class FastAI(AIPlayer):
    """Alias untuk AIPlayer"""
    pass