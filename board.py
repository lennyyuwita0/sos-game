"""
SOS Game Board Logic - Pygame Version
Mengelola papan permainan dan deteksi SOS untuk pygame
"""

class SOSBoard:
    def __init__(self, size=5):
        self.size = size
        self.board = [['' for _ in range(size)] for _ in range(size)]
        self.sos_sequences = []  # Menyimpan urutan SOS yang ditemukan
    
    def is_valid_move(self, row, col):
        """Check if move is valid"""
        return (0 <= row < self.size and 
                0 <= col < self.size and 
                self.board[row][col] == '')
    
    def make_move(self, row, col, letter):
        """Make a move and return points scored"""
        if not self.is_valid_move(row, col):
            return 0
        
        self.board[row][col] = letter
        points = self.check_sos_formations(row, col)
        return points
    
    def check_sos_formations(self, row, col):
        """Check for SOS formations after placing a letter"""
        points = 0
        letter = self.board[row][col]
        
        # Directions: horizontal, vertical, diagonal
        directions = [
            (0, 1),   # horizontal
            (1, 0),   # vertical
            (1, 1),   # diagonal down-right
            (1, -1)   # diagonal down-left
        ]
        
        for dr, dc in directions:
            # Check if current position is middle of SOS
            if letter == 'O':
                points += self._check_sos_middle(row, col, dr, dc)
            
            # Check if current position is start of SOS
            if letter == 'S':
                points += self._check_sos_start(row, col, dr, dc)
            
            # Check if current position is end of SOS
            if letter == 'S':
                points += self._check_sos_end(row, col, dr, dc)
        
        return points
    
    def _check_sos_middle(self, row, col, dr, dc):
        """Check if O is middle of SOS in given direction"""
        points = 0
        
        # Check S-O-S pattern
        prev_row, prev_col = row - dr, col - dc
        next_row, next_col = row + dr, col + dc
        
        if (self._is_valid_pos(prev_row, prev_col) and 
            self._is_valid_pos(next_row, next_col) and
            self.board[prev_row][prev_col] == 'S' and 
            self.board[next_row][next_col] == 'S'):
            
            # Add SOS sequence
            sos_seq = [(prev_row, prev_col), (row, col), (next_row, next_col)]
            if sos_seq not in self.sos_sequences:
                self.sos_sequences.append(sos_seq)
                points += 1
        
        return points
    
    def _check_sos_start(self, row, col, dr, dc):
        """Check if S is start of SOS in given direction"""
        points = 0
        
        # Check S-O-S pattern starting from current S
        mid_row, mid_col = row + dr, col + dc
        end_row, end_col = row + 2*dr, col + 2*dc
        
        if (self._is_valid_pos(mid_row, mid_col) and 
            self._is_valid_pos(end_row, end_col) and
            self.board[mid_row][mid_col] == 'O' and 
            self.board[end_row][end_col] == 'S'):
            
            # Add SOS sequence
            sos_seq = [(row, col), (mid_row, mid_col), (end_row, end_col)]
            if sos_seq not in self.sos_sequences:
                self.sos_sequences.append(sos_seq)
                points += 1
        
        return points
    
    def _check_sos_end(self, row, col, dr, dc):
        """Check if S is end of SOS in given direction"""
        points = 0
        
        # Check S-O-S pattern ending at current S
        mid_row, mid_col = row - dr, col - dc
        start_row, start_col = row - 2*dr, col - 2*dc
        
        if (self._is_valid_pos(mid_row, mid_col) and 
            self._is_valid_pos(start_row, start_col) and
            self.board[mid_row][mid_col] == 'O' and 
            self.board[start_row][start_col] == 'S'):
            
            # Add SOS sequence
            sos_seq = [(start_row, start_col), (mid_row, mid_col), (row, col)]
            if sos_seq not in self.sos_sequences:
                self.sos_sequences.append(sos_seq)
                points += 1
        
        return points
    
    def _is_valid_pos(self, row, col):
        """Check if position is valid"""
        return 0 <= row < self.size and 0 <= col < self.size
    
    def get_cell(self, row, col):
        """Get cell value"""
        if self._is_valid_pos(row, col):
            return self.board[row][col]
        return None
    
    def is_full(self):
        """Check if board is full"""
        for row in self.board:
            for cell in row:
                if cell == '':
                    return False
        return True
    
    def get_empty_cells(self):
        """Get list of empty cells"""
        empty_cells = []
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == '':
                    empty_cells.append((i, j))
        return empty_cells
    
    def copy(self):
        """Create a copy of the board"""
        new_board = SOSBoard(self.size)
        new_board.board = [row[:] for row in self.board]
        new_board.sos_sequences = [seq[:] for seq in self.sos_sequences]
        return new_board
    
    def display(self):
        """Display board for debugging"""
        print("\n  " + " ".join([str(i) for i in range(self.size)]))
        for i, row in enumerate(self.board):
            print(f"{i} " + " ".join([cell if cell else '.' for cell in row]))
        print(f"SOS sequences found: {len(self.sos_sequences)}")
    
    def get_board_state(self):
        """Get current board state as string"""
        state = ""
        for row in self.board:
            for cell in row:
                state += cell if cell else "."
        return state