"""
SOS Game Player Classes - Pygame Version
Mengelola input dan aksi pemain untuk pygame
"""

class Player:
    """Base player class"""
    def __init__(self, name):
        self.name = name
        self.score = 0
    
    def add_points(self, points):
        """Add points to player's score"""
        self.score += points
    
    def reset_score(self):
        """Reset player's score"""
        self.score = 0
    
    def get_score(self):
        """Get player's current score"""
        return self.score

class HumanPlayer(Player):
    """Human player class"""
    def __init__(self, name="Human"):
        super().__init__(name)
        self.preferred_letter = 'S'  # Default preference
    
    def set_preferred_letter(self, letter):
        """Set preferred letter (S or O)"""
        if letter in ['S', 'O']:
            self.preferred_letter = letter
    
    def get_preferred_letter(self):
        """Get preferred letter"""
        return self.preferred_letter
    
    def get_move_console(self, board):
        """Get move from console input (for debugging)"""
        while True:
            try:
                print(f"\n{self.name}'s turn (Score: {self.score})")
                board.display()
                
                # Get position
                row = int(input("Enter row (0-4): "))
                col = int(input("Enter column (0-4): "))
                
                if not board.is_valid_move(row, col):
                    print("Invalid move! Cell is already occupied or out of bounds.")
                    continue
                
                # Get letter
                while True:
                    letter = input("Enter letter (S or O): ").upper()
                    if letter in ['S', 'O']:
                        break
                    print("Invalid letter! Please enter S or O.")
                
                return row, col, letter
                
            except ValueError:
                print("Invalid input! Please enter numbers for row and column.")
            except KeyboardInterrupt:
                print("\nGame interrupted by user.")
                return None, None, None
    
    def validate_move(self, board, row, col):
        """Validate if the move is legal"""
        return board.is_valid_move(row, col)
    
    def get_stats(self):
        """Get player statistics"""
        return {
            'name': self.name,
            'score': self.score,
            'type': 'Human'
        }

class GameSession:
    """Manages game session data"""
    def __init__(self):
        self.moves_history = []
        self.game_start_time = None
        self.game_end_time = None
    
    def add_move(self, player_name, row, col, letter, points_scored):
        """Add move to history"""
        move = {
            'player': player_name,
            'position': (row, col),
            'letter': letter,
            'points': points_scored,
            'move_number': len(self.moves_history) + 1
        }
        self.moves_history.append(move)
    
    def get_move_history(self):
        """Get complete move history"""
        return self.moves_history
    
    def get_last_move(self):
        """Get the last move made"""
        return self.moves_history[-1] if self.moves_history else None
    
    def clear_history(self):
        """Clear move history"""
        self.moves_history = []
    
    def get_total_moves(self):
        """Get total number of moves"""
        return len(self.moves_history)
    
    def display_history(self):
        """Display move history"""
        print("\n=== Move History ===")
        for move in self.moves_history:
            print(f"Move {move['move_number']}: {move['player']} placed '{move['letter']}' "
                  f"at ({move['position'][0]}, {move['position'][1]}) - "
                  f"Points: {move['points']}")

class InputValidator:
    """Validates user input for the game"""
    
    @staticmethod
    def validate_position(row, col, board_size=5):
        """Validate board position"""
        try:
            row, col = int(row), int(col)
            return (0 <= row < board_size and 0 <= col < board_size), row, col
        except ValueError:
            return False, None, None
    
    @staticmethod
    def validate_letter(letter):
        """Validate letter input"""
        letter = str(letter).upper().strip()
        return letter in ['S', 'O'], letter
    
    @staticmethod
    def validate_yes_no(response):
        """Validate yes/no response"""
        response = str(response).lower().strip()
        if response in ['y', 'yes', '1', 'true']:
            return True, True
        elif response in ['n', 'no', '0', 'false']:
            return True, False
        return False, None
    
    @staticmethod
    def get_safe_input(prompt, validator_func, error_message="Invalid input. Please try again."):
        """Get input with validation"""
        while True:
            try:
                user_input = input(prompt)
                is_valid, result = validator_func(user_input)
                if is_valid:
                    return result
                print(error_message)
            except KeyboardInterrupt:
                print("\nInput cancelled by user.")
                return None
            except Exception as e:
                print(f"Error: {e}")
                print(error_message)