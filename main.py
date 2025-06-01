#!/usr/bin/env python3
"""
Enhanced SOS Game - Pygame Version
- AI plays as 'O', Human plays as 'S'
- Added: Difficulty levels, Game statistics, Sound effects, Hints system
- Added: Undo/Redo, Game history, Better AI, Animation improvements
"""

import pygame
import sys
import time
import random
import json
import os
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional
import math 

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
BOARD_SIZE = 5
CELL_SIZE = 100
BOARD_OFFSET_X = 150
BOARD_OFFSET_Y = 200

class Difficulty(Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

class GameMode(Enum):
    HUMAN_VS_AI = "Human vs AI"
    HUMAN_VS_HUMAN = "Human vs Human"

# Colors
COLORS = {
    'background': (15, 32, 39),
    'board': (44, 62, 80),
    'cell': (52, 73, 94),
    'cell_hover': (71, 85, 105),
    'grid_line': (26, 42, 55),
    'text_primary': (236, 240, 241),
    'text_secondary': (189, 195, 199),
    'accent_blue': (52, 152, 219),
    'accent_green': (46, 204, 113),
    'accent_red': (231, 76, 60),
    'accent_orange': (230, 126, 34),
    'letter_s': (52, 152, 219),  # Human player color
    'letter_o': (231, 76, 60),   # AI player color
    'button': (39, 174, 96),
    'button_hover': (46, 204, 113),
    'sos_highlight': (241, 196, 15),
    'hint_highlight': (155, 89, 182)
}

@dataclass
class GameStats:
    games_played: int = 0
    human_wins: int = 0
    ai_wins: int = 0
    draws: int = 0
    total_sos_formed: int = 0
    best_score: int = 0

@dataclass
class Move:
    row: int
    col: int
    letter: str
    player: str
    sos_formed: int

class SOSBoard:
    """Enhanced board with undo/redo functionality"""
    
    def __init__(self, size=5):
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.sos_sequences = []
        self.move_history = []
    
    def is_valid_move(self, row, col):
        return (0 <= row < self.size and 
                0 <= col < self.size and 
                self.board[row][col] is None)
    
    def make_move(self, row, col, letter, player_name=""):
        if not self.is_valid_move(row, col):
            return 0
        
        self.board[row][col] = letter
        sos_count = self._check_sos_sequences(row, col)
        
        # Record move in history
        move = Move(row, col, letter, player_name, sos_count)
        self.move_history.append(move)
        
        return sos_count
    
    def undo_last_move(self):
        """Undo the last move"""
        if not self.move_history:
            return None
        
        last_move = self.move_history.pop()
        self.board[last_move.row][last_move.col] = None
        
        # Recalculate SOS sequences
        self.sos_sequences = []
        temp_history = self.move_history.copy()
        self.move_history = []
        
        for move in temp_history:
            self.board[move.row][move.col] = move.letter
            self._check_sos_sequences(move.row, move.col)
            self.move_history.append(move)
        
        return last_move
    
    def _check_sos_sequences(self, row, col):
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        new_sequences = []
        
        for dr, dc in directions:
            # Check SOS with current position as first 'S'
            if self.board[row][col] == 'S':
                r1, c1 = row + dr, col + dc
                r2, c2 = row + 2*dr, col + 2*dc
                if (self._is_valid_pos(r1, c1) and self._is_valid_pos(r2, c2) and
                    self.board[r1][c1] == 'O' and self.board[r2][c2] == 'S'):
                    sequence = [(row, col), (r1, c1), (r2, c2)]
                    if sequence not in self.sos_sequences:
                        self.sos_sequences.append(sequence)
                        new_sequences.append(sequence)
            
            # Check SOS with current position as middle 'O'
            if self.board[row][col] == 'O':
                r1, c1 = row - dr, col - dc
                r2, c2 = row + dr, col + dc
                if (self._is_valid_pos(r1, c1) and self._is_valid_pos(r2, c2) and
                    self.board[r1][c1] == 'S' and self.board[r2][c2] == 'S'):
                    sequence = [(r1, c1), (row, col), (r2, c2)]
                    if sequence not in self.sos_sequences:
                        self.sos_sequences.append(sequence)
                        new_sequences.append(sequence)
            
            # Check SOS with current position as last 'S'
            if self.board[row][col] == 'S':
                r1, c1 = row - dr, col - dc
                r2, c2 = row - 2*dr, col - 2*dc
                if (self._is_valid_pos(r1, c1) and self._is_valid_pos(r2, c2) and
                    self.board[r1][c1] == 'O' and self.board[r2][c2] == 'S'):
                    sequence = [(r2, c2), (r1, c1), (row, col)]
                    if sequence not in self.sos_sequences:
                        self.sos_sequences.append(sequence)
                        new_sequences.append(sequence)
        
        return len(new_sequences)
    
    def _is_valid_pos(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size
    
    def get_cell(self, row, col):
        if self._is_valid_pos(row, col):
            return self.board[row][col]
        return None
    
    def is_full(self):
        for row in self.board:
            for cell in row:
                if cell is None:
                    return False
        return True
    
    def get_empty_cells(self):
        empty_cells = []
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] is None:
                    empty_cells.append((row, col))
        return empty_cells
    
    def get_possible_sos_moves(self):
        """Get moves that would form SOS sequences"""
        possible_moves = []
        empty_cells = self.get_empty_cells()
        
        for row, col in empty_cells:
            for letter in ['S', 'O']: # Ini untuk testing, bukan untuk AI benar-benar menempatkan
                test_board = self.copy()
                sos_count = test_board.make_move(row, col, letter)
                if sos_count > 0:
                    possible_moves.append((row, col, letter, sos_count))
        
        return possible_moves
    
    def copy(self):
        new_board = SOSBoard(self.size)
        new_board.board = [row[:] for row in self.board]
        new_board.sos_sequences = [seq[:] for seq in self.sos_sequences]
        new_board.move_history = self.move_history.copy()
        return new_board

class Player:
    def __init__(self, name, letter, is_ai=False):
        self.name = name
        self.letter = letter  # 'S' for human, 'O' for AI
        self.score = 0
        self.is_ai = is_ai
    
    def add_points(self, points):
        self.score += points
    
    def reset_score(self):
        self.score = 0

class EnhancedAI:
    """Enhanced AI with multiple difficulty levels"""
    
    def __init__(self, difficulty: Difficulty):
        self.difficulty = difficulty
        self.name = f"AI ({difficulty.value})"
        self.letter = 'O'  # AI always plays 'O'
        self.score = 0
        self.is_ai = True
    
    def add_points(self, points):
        self.score += points
    
   
    def reset_score(self):
        self.score = 0
    
    
    def get_move(self, board):
        """Get AI move based on difficulty level"""
        # PERBAIKAN AI LETTER SELEKSI DIMULAI
        # Pastikan AI selalu mengembalikan 'O' sebagai huruf yang akan ditempatkan
        
        row, col, _ = (None, None, None) # Inisialisasi dengan None

        if self.difficulty == Difficulty.EASY:
            row, col, _ = self._get_easy_move(board)
        elif self.difficulty == Difficulty.MEDIUM:
            row, col, _ = self._get_medium_move(board)
        else:  # HARD
            row, col, _ = self._get_hard_move(board)
            
        # Jika tidak ada gerakan yang valid ditemukan, kembali ke acak
        if row is None or col is None:
            row, col, _ = self._get_random_move(board)

        # Pastikan AI selalu menempatkan 'O'
        return row, col, self.letter
        # PERBAIKAN AI LETTER SELEKSI BERAKHIR
    
    def _get_easy_move(self, board):
        """Easy AI - always random for a chaotic experience"""
        empty_cells = board.get_empty_cells()
        if empty_cells:
            row, col = random.choice(empty_cells)
            # AI selalu main 'O'
            return row, col, self.letter
        return None, None, None
    
    def _get_medium_move(self, board):
        """Medium AI - 70% random, 30% smart for more chaos"""
        if random.random() < 0.7: 
            return self._get_random_move(board)

        sos_move = self._find_sos_move(board)
        if sos_move:
            return sos_move

        block_move = self._find_blocking_move(board)
        if block_move:
            return block_move

        strategic_move = self._find_strategic_move(board)
        if strategic_move:
            return strategic_move

        return self._get_random_move(board)
    
    def _get_hard_move(self, board):
        """Hard AI - mostly random for chaos, rarely uses Minimax"""
        if random.random() < 0.8: 
            return self._get_random_move(board)

        sos_move = self._find_sos_move(board)
        if sos_move:
            return sos_move
        
        blocking_move = self._find_blocking_move(board)
        if blocking_move:
            return blocking_move
        
        best_move = self._find_best_move_with_lookahead(board)
        if best_move:
            return best_move
        
        strategic_move = self._find_strategic_move(board)
        if strategic_move:
            return strategic_move
        
        return self._get_random_move(board)
    
    def _find_sos_move(self, board):
        """Find move that creates SOS"""
        empty_cells = board.get_empty_cells()
        best_move = None
        max_sos = 0
        
        for row, col in empty_cells:
            # AI hanya mencoba menempatkan 'O' untuk membentuk SOS
            test_board = board.copy()
            sos_count = test_board.make_move(row, col, self.letter) # Hanya coba 'O'
            if sos_count > max_sos:
                max_sos = sos_count
                best_move = (row, col, self.letter) # Pastikan mengembalikan 'O'
        
        return best_move if max_sos > 0 else None
    
    def _find_blocking_move(self, board):
        """Find move that blocks opponent from forming SOS"""
        empty_cells = board.get_empty_cells()
        
        for row, col in empty_cells:
            # Coba simulasi lawan menempatkan 'S'
            test_board_opponent = board.copy()
            opponent_sos_count = test_board_opponent.make_move(row, col, 'S') # Lawan selalu 'S'
            if opponent_sos_count > 0:
                # Jika lawan bisa membuat SOS, blokir dengan 'O'
                return row, col, self.letter # AI selalu memblokir dengan 'O'
        
        return None
    
    def _find_strategic_move(self, board):
        """Find strategically good positions"""
        empty_cells = board.get_empty_cells()
        if not empty_cells:
            return None
        
        center = board.size // 2
        scored_moves = []
        
        for row, col in empty_cells:
            score = 0
            
            distance_from_center = abs(row - center) + abs(col - center)
            score += (board.size - distance_from_center) * 2
            
            # Hanya perhitungkan potensi SOS jika AI menempatkan 'O'
            test_board = board.copy()
            test_board.board[row][col] = self.letter # Hanya simulasi 'O'
            
            potential_sos = self._count_potential_sos(test_board, row, col)
            score += potential_sos * 5
            
            scored_moves.append((score, row, col))
        
        scored_moves.sort(reverse=True)
        if scored_moves:
            _, row, col = scored_moves[0]
            return row, col, self.letter # Pastikan mengembalikan 'O'
        
        return None
    
    def _count_potential_sos(self, board, row, col):
        """Count how many potential SOS sequences this position could complete"""
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        potential_count = 0
        current_letter = board.board[row][col]
        
        # Perhatikan bahwa current_letter di sini sudah diasumsikan 'O' karena Strategic AI hanya mencoba 'O'
        
        for dr, dc in directions:
            if current_letter == 'O':
                r1, c1 = row - dr, col - dc
                r2, c2 = row + dr, col + dc
                if (board._is_valid_pos(r1, c1) and board._is_valid_pos(r2, c2)):
                    if ((board.board[r1][c1] == 'S' and board.board[r2][c2] is None) or
                        (board.board[r1][c1] is None and board.board[r2][c2] == 'S')):
                        potential_count += 1
            # Tambahkan logika untuk S-O-? jika AI bisa menempatkan S, tapi di sini AI hanya 'O'
            # Jadi, kita hanya fokus pada O sebagai huruf tengah.
        
        return potential_count
    
    def _find_best_move_with_lookahead(self, board):
        """Simple lookahead evaluation"""
        empty_cells = board.get_empty_cells()
        if not empty_cells:
            return None
        
        best_move = None
        best_score = float('-inf')
        
        for row, col in empty_cells:
            # AI hanya mencoba menempatkan 'O'
            test_board = board.copy()
            immediate_score = test_board.make_move(row, col, self.letter, "AI")
            
            # Simple lookahead - check opponent's best response (lawan selalu 'S')
            opponent_best = 0
            for opp_row, opp_col in test_board.get_empty_cells()[:5]:  # Limit for performance
                opp_board = test_board.copy()
                opp_score = opp_board.make_move(opp_row, opp_col, 'S', "Human") # Lawan selalu 'S'
                opponent_best = max(opponent_best, opp_score)
            
            total_score = immediate_score * 10 - opponent_best * 5 # AI memaksimalkan skornya dan meminimalkan skor lawan
            
            if total_score > best_score:
                best_score = total_score
                best_move = (row, col, self.letter) # Pastikan mengembalikan 'O'
        
        return best_move
    
    def _get_random_move(self, board):
        """Fallback random move"""
        empty_cells = board.get_empty_cells()
        if empty_cells:
            row, col = random.choice(empty_cells)
            return row, col, self.letter # AI selalu memilih 'O'
        return None, None, None

class SoundManager:
    """Manage game sounds"""
    
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        self._load_sounds()
    
    def _load_sounds(self):
        """Create simple sound effects using pygame"""
        try:
            # Create basic sound effects
            # Note: In a real implementation, you'd load actual sound files
            pass
        except:
            self.enabled = False
    
    def toggle_sound(self):
        self.enabled = not self.enabled

class EnhancedSOSGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Enhanced SOS Game - Modern Edition")
        self.clock = pygame.time.Clock()
        
        # Game components
        self.board = SOSBoard()
        self.sound_manager = SoundManager()
        self.stats = self._load_stats()
        
        # Game state
        self.game_mode = GameMode.HUMAN_VS_AI
        self.difficulty = Difficulty.MEDIUM
        self.human_player = Player("Human", "S", False)
        self.ai_player = EnhancedAI(self.difficulty)
        self.current_player = self.human_player
        self.game_over = False
        self.winner = None
        
        # UI state
        self.hover_cell = None
        self.show_winner_animation = False
        self.winner_animation_time = 0
        self.particles = []
        self.hint_cells = []
        self.show_hints = False
        
        # Timing
        self.ai_move_timer = 0
        self.ai_move_delay = 1500
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_title = pygame.font.Font(None, 64)
        self.font_tiny = pygame.font.Font(None, 20)
        
        # Enhanced buttons
        self.buttons = {
            'new_game': pygame.Rect(50, 50, 100, 35),
             'undo': pygame.Rect(160, 50, 80, 35),
             'difficulty': pygame.Rect(250, 50, 100, 35),  # Dari 340 ke 250 (90 pixel ke kiri)
             'stats': pygame.Rect(360, 50, 80, 35),        # Dari 450 ke 360 (90 pixel ke kiri)
            'quit': pygame.Rect(880, 50, 70, 35)
}
        
        
        # Highlighting
        self.sos_highlights = []
        self.highlight_timer = 0
    
    def _load_stats(self):
        """Load game statistics from file"""
        try:
            if os.path.exists('sos_stats.json'):
                with open('sos_stats.json', 'r') as f:
                    data = json.load(f)
                    return GameStats(**data)
        except:
            pass
        return GameStats()
    
    def _save_stats(self):
        """Save game statistics to file"""
        try:
            with open('sos_stats.json', 'w') as f:
                json.dump(self.stats.__dict__, f)
        except:
            pass
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._save_stats()
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_click(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_move(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.new_game()
                elif event.key == pygame.K_u:
                    self.undo_move()
                elif event.key == pygame.K_h:
                    self.toggle_hints()
                elif event.key == pygame.K_d:
                    self.cycle_difficulty()
                elif event.key == pygame.K_s:
                    self.sound_manager.toggle_sound()
                elif event.key == pygame.K_ESCAPE:
                    self._save_stats()
                    return False
        
        return True
    
    def handle_click(self, pos):
        # Button clicks
        if self.buttons['new_game'].collidepoint(pos):
            self.new_game()
        elif self.buttons['undo'].collidepoint(pos):
            self.undo_move()
        elif self.buttons['difficulty'].collidepoint(pos):
            self.cycle_difficulty()
        elif self.buttons['stats'].collidepoint(pos):
            self.show_stats()
        elif self.buttons['quit'].collidepoint(pos):
            self._save_stats()
            pygame.quit()
            sys.exit()
        
        # Board clicks (only human player)
        elif (not self.game_over and 
              self.current_player == self.human_player):
            cell = self.get_cell_from_pos(pos)
            if cell:
                row, col = cell
                # Human always plays 'S'
                self.make_move(row, col, 'S')
    
    def handle_mouse_move(self, pos):
        self.hover_cell = self.get_cell_from_pos(pos)
    
    def get_cell_from_pos(self, pos):
        x, y = pos
        if (BOARD_OFFSET_X <= x < BOARD_OFFSET_X + BOARD_SIZE * CELL_SIZE and
            BOARD_OFFSET_Y <= y < BOARD_OFFSET_Y + BOARD_SIZE * CELL_SIZE):
            
            col = (x - BOARD_OFFSET_X) // CELL_SIZE
            row = (y - BOARD_OFFSET_Y) // CELL_SIZE
            
            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                return (row, col)
        return None
    
    def make_move(self, row, col, letter):
        if self.board.is_valid_move(row, col):
            player_name = self.current_player.name
            points = self.board.make_move(row, col, letter, player_name)
            self.current_player.add_points(points)
            
            if points > 0:
                self.add_score_particles(row, col, points)
                self.highlight_new_sos()
                self.stats.total_sos_formed += points
                if self.current_player.score > self.stats.best_score:
                    self.stats.best_score = self.current_player.score
            
            self.hide_hints()
            
            if self.board.is_full():
                self.end_game()
                return
            
            # Switch players if no points scored
            if points == 0:
                if self.current_player == self.human_player:
                    self.current_player = self.ai_player
                    self.ai_move_timer = pygame.time.get_ticks()
                else:
                    self.current_player = self.human_player
    
    def undo_move(self):
        """Undo the last move(s)"""
        if self.game_over or not self.board.move_history:
            return
        
        # Undo AI move if it was the last one
        if (self.board.move_history and 
            self.board.move_history[-1].player == self.ai_player.name):
            last_move = self.board.undo_last_move()
            if last_move:
                self.ai_player.score -= last_move.sos_formed
        
        # Undo human move
        if (self.board.move_history and 
            self.board.move_history[-1].player == self.human_player.name):
            last_move = self.board.undo_last_move()
            if last_move:
                self.human_player.score -= last_move.sos_formed
        
        self.current_player = self.human_player
        self.game_over = False
        self.winner = None
        self.hide_hints()
    
    def toggle_hints(self):
        """Toggle hint system"""
        if self.show_hints:
            self.hide_hints()
        else:
            self.show_hints_for_player()
    
    def show_hints_for_player(self):
        """Show possible SOS moves as hints"""
        if self.game_over or self.current_player != self.human_player:
            return
        
        possible_moves = self.board.get_possible_sos_moves()
        self.hint_cells = [(row, col) for row, col, letter, count in possible_moves 
                           if letter == 'S']  # Only show S moves for human
        self.show_hints = True
    
    def hide_hints(self):
        """Hide hints"""
        self.hint_cells = []
        self.show_hints = False
    
    def cycle_difficulty(self):
        """Cycle through AI difficulty levels"""
        difficulties = list(Difficulty)
        current_index = difficulties.index(self.difficulty)
        next_index = (current_index + 1) % len(difficulties)
        self.difficulty = difficulties[next_index]
        
        # Update AI player
        self.ai_player = EnhancedAI(self.difficulty)
        
        # Reset game if in progress
        if not self.game_over and len(self.board.move_history) > 0:
            self.new_game()
    
    def show_stats(self):
        """Toggle stats display (simple implementation)"""
        # In a full implementation, this would show a stats overlay
        print(f"Games: {self.stats.games_played}, Wins: {self.stats.human_wins}, "
              f"AI Wins: {self.stats.ai_wins}, Draws: {self.stats.draws}")
    
    def update_ai(self):
        """Update AI logic"""
        if (self.current_player == self.ai_player and 
            not self.game_over and 
            pygame.time.get_ticks() - self.ai_move_timer > self.ai_move_delay):
            
            self.ai_move()
    
    def ai_move(self):
        if self.game_over:
            return
        
        # Panggil get_move dari ai_player yang sudah dipastikan hanya mengembalikan 'O'
        row, col, letter = self.ai_player.get_move(self.board)
        
        if row is not None:
            points = self.board.make_move(row, col, letter, self.ai_player.name)
            self.ai_player.add_points(points)
            
            if points > 0:
                self.add_score_particles(row, col, points)
                self.highlight_new_sos()
                self.stats.total_sos_formed += points
            
            if self.board.is_full():
                self.end_game()
                return
            
            if points == 0:
                self.current_player = self.human_player
            else:
                # AI gets another turn
                self.ai_move_timer = pygame.time.get_ticks()
    
    def highlight_new_sos(self):
        # Add new SOS sequences to highlights
        for seq in self.board.sos_sequences:
            if seq not in self.sos_highlights:
                self.sos_highlights.append(seq)
        self.highlight_timer = pygame.time.get_ticks()
    
    def add_score_particles(self, row, col, points):
        x = BOARD_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
        y = BOARD_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2
        
        # Create different colored particles based on player
        if self.current_player == self.human_player:
            color = COLORS['letter_s']
        else:
            color = COLORS['letter_o']
        
        for i in range(points * 8):
            particle = {
                'x': x + random.randint(-15, 15),
                'y': y + random.randint(-15, 15),
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-5, -1),
                'life': 80,
                'color': color,
                'size': random.randint(2, 5)
            }
            self.particles.append(particle)
    
    def update_particles(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.15  # Gravity
            particle['life'] -= 1
            particle['size'] = max(1, particle['size'] - 0.05)
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def new_game(self):
        self.board = SOSBoard()
        self.human_player.reset_score()
        self.ai_player.reset_score()
        self.current_player = self.human_player
        self.game_over = False
        self.winner = None
        self.sos_highlights = []
        self.particles = []
        self.show_winner_animation = False
        self.ai_move_timer = 0
        self.hide_hints()
    
    def end_game(self):
        self.game_over = True
        self.stats.games_played += 1
        
        human_score = self.human_player.score
        ai_score = self.ai_player.score
        
        if human_score > ai_score:
            self.winner = "Human"
            self.stats.human_wins += 1
        elif ai_score > human_score:
            self.winner = "AI"
            self.stats.ai_wins += 1
        else:
            self.winner = "Draw"
            self.stats.draws += 1
        
        self.show_winner_animation = True
        self.winner_animation_time = pygame.time.get_ticks()
        self._save_stats()
    
    def draw(self):
        # Clear screen with enhanced gradient
        self.draw_enhanced_background()
        
        # Draw title
        self.draw_title()
        
        # Draw enhanced buttons
        self.draw_enhanced_buttons()
        
        # Draw board
        self.draw_enhanced_board()
        
        # Draw scores and stats
        self.draw_enhanced_scores()
        
        # Draw game info
        self.draw_game_info()
        
        # Draw particles
        self.draw_particles()
        
        # Draw move history
        self.draw_move_history()
        
        # Draw winner animation
        if self.show_winner_animation:
            self.draw_winner_animation()
        
        pygame.display.flip()
    
    def draw_enhanced_background(self):
        # More sophisticated gradient
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            r = int(15 + (30 - 15) * ratio + 5 * math.sin(ratio * 3.14159))
            g = int(32 + (45 - 32) * ratio + 3 * math.cos(ratio * 3.14159))
            b = int(39 + (60 - 39) * ratio + 2 * math.sin(ratio * 6.28318))
            color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))
        
        # Add subtle pattern
        for i in range(0, WINDOW_WIDTH, 100):
            for j in range(0, WINDOW_HEIGHT, 100):
                alpha = 10
                overlay = pygame.Surface((50, 50))
                overlay.set_alpha(alpha)
                overlay.fill((255, 255, 255))
                self.screen.blit(overlay, (i, j))
    
    def draw_title(self):
        title_text = self.font_title.render("Enhanced SOS Game", True, COLORS['text_primary'])
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 120))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle = f"Human (S) vs AI-{self.difficulty.value} (O)"
        subtitle_text = self.font_small.render(subtitle, True, COLORS['text_secondary'])
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(subtitle_text, subtitle_rect)
    
    def draw_enhanced_buttons(self):
        mouse_pos = pygame.mouse.get_pos()
        
        button_configs = [
            ('new_game', "New Game", COLORS['button']),
            ('undo', "Undo", COLORS['accent_orange']),
            ('difficulty', f"Diff: {self.difficulty.value[:4]}", COLORS['accent_green']),
            ('stats', "Stats", COLORS['accent_blue']),
            ('quit', "Quit", COLORS['accent_red'])
        ]
        
        for key, text, base_color in button_configs:
            rect = self.buttons[key]
            color = self.lighten_color(base_color, 30) if rect.collidepoint(mouse_pos) else base_color
            
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS['text_primary'], rect, 2, border_radius=8)
            
            text_surface = self.font_tiny.render(text, True, COLORS['text_primary'])
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def lighten_color(self, color, amount):
        return tuple(min(255, c + amount) for c in color)
    
    def draw_enhanced_board(self):
        # Enhanced board background with shadow
        shadow_rect = pygame.Rect(BOARD_OFFSET_X - 5, BOARD_OFFSET_Y - 5, 
                                  BOARD_SIZE * CELL_SIZE + 20, BOARD_SIZE * CELL_SIZE + 20)
        pygame.draw.rect(self.screen, (0, 0, 0, 50), shadow_rect, border_radius=15)
        
        board_rect = pygame.Rect(BOARD_OFFSET_X - 10, BOARD_OFFSET_Y - 10, 
                                 BOARD_SIZE * CELL_SIZE + 20, BOARD_SIZE * CELL_SIZE + 20)
        pygame.draw.rect(self.screen, COLORS['board'], board_rect, border_radius=15)
        
        # Draw cells with enhanced styling
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x = BOARD_OFFSET_X + col * CELL_SIZE
                y = BOARD_OFFSET_Y + row * CELL_SIZE
                
                cell_rect = pygame.Rect(x + 3, y + 3, CELL_SIZE - 6, CELL_SIZE - 6)
                
                # Determine cell color
                color = COLORS['cell']
                
                if self.hover_cell == (row, col) and not self.game_over:
                    color = COLORS['cell_hover']
                
                # Hint highlighting
                if (row, col) in self.hint_cells:
                    color = COLORS['hint_highlight']
                
                # SOS highlighting
                current_time = pygame.time.get_ticks()
                if current_time - self.highlight_timer < 3000:
                    for seq in self.sos_highlights:
                        if (row, col) in seq:
                            color = COLORS['sos_highlight']
                            break
                
                pygame.draw.rect(self.screen, color, cell_rect, border_radius=10)
                
                # Add subtle border
                pygame.draw.rect(self.screen, COLORS['grid_line'], cell_rect, 2, border_radius=10)
                
                # Draw letter with enhanced styling
                letter = self.board.get_cell(row, col)
                if letter:
                    letter_color = COLORS['letter_s'] if letter == 'S' else COLORS['letter_o']
                    
                    # Add letter shadow
                    shadow_text = self.font_large.render(letter, True, (0, 0, 0))
                    shadow_rect = shadow_text.get_rect(center=(cell_rect.centerx + 2, cell_rect.centery + 2))
                    self.screen.blit(shadow_text, shadow_rect)
                    
                    # Main letter
                    text = self.font_large.render(letter, True, letter_color)
                    text_rect = text.get_rect(center=cell_rect.center)
                    self.screen.blit(text, text_rect)
                
                # Draw hint indicators
                elif (row, col) in self.hint_cells:
                    hint_text = self.font_medium.render("S", True, COLORS['text_secondary'])
                    hint_rect = hint_text.get_rect(center=cell_rect.center)
                    self.screen.blit(hint_text, hint_rect)
    
    def draw_enhanced_scores(self):
        # Score panel background
        score_rect = pygame.Rect(50, 750, 300, 120)
        pygame.draw.rect(self.screen, COLORS['board'], score_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['text_primary'], score_rect, 2, border_radius=10)
        
        # Player scores with icons
        human_text = f"Human (S): {self.human_player.score}"
        ai_text = f"AI (O): {self.ai_player.score}"
        
        human_surface = self.font_medium.render(human_text, True, COLORS['letter_s'])
        ai_surface = self.font_medium.render(ai_text, True, COLORS['letter_o'])
        
        self.screen.blit(human_surface, (60, 760))
        self.screen.blit(ai_surface, (60, 790))
        
        # Game stats
        stats_text = f"Games: {self.stats.games_played} | Wins: {self.stats.human_wins} | Best: {self.stats.best_score}"
        stats_surface = self.font_small.render(stats_text, True, COLORS['text_secondary'])
        self.screen.blit(stats_surface, (60, 820))
        
        # Total SOS formed
        sos_text = f"Total SOS: {len(self.board.sos_sequences)} | All-time SOS: {self.stats.total_sos_formed}"
        sos_surface = self.font_small.render(sos_text, True, COLORS['text_secondary'])
        self.screen.blit(sos_surface, (60, 840))
    
    def draw_game_info(self):
        # Current player and status
        if not self.game_over:
            if self.current_player == self.human_player:
                status = "Your turn - Place 'S'"
                color = COLORS['letter_s']
            else:
                status = f"AI ({self.difficulty.value}) thinking..."
                color = COLORS['letter_o']
        else:
            if self.winner == "Human":
                status = "🎉 You Win! 🎉"
                color = COLORS['accent_green']
            elif self.winner == "AI":
                status = "🤖 AI Wins! 🤖"
                color = COLORS['accent_red']
            else:
                status = "🤝 It's a Draw! 🤝"
                color = COLORS['accent_orange']
        
        status_surface = self.font_medium.render(status, True, color)
        status_rect = status_surface.get_rect(center=(WINDOW_WIDTH // 2, 780))
        self.screen.blit(status_surface, status_rect)
        
        # Additional info
        if self.show_hints and self.hint_cells:
            hint_info = f"💡 {len(self.hint_cells)} possible SOS moves shown"
            hint_surface = self.font_small.render(hint_info, True, COLORS['hint_highlight'])
            hint_rect = hint_surface.get_rect(center=(WINDOW_WIDTH // 2, 810))
            self.screen.blit(hint_surface, hint_rect)
    
    def draw_particles(self):
        for particle in self.particles:
            if particle['life'] > 0:
                alpha = int(255 * (particle['life'] / 80))
                size = max(1, int(particle['size']))
                
                # Create surface with per-pixel alpha
                particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                color_with_alpha = (*particle['color'], alpha)
                pygame.draw.circle(particle_surface, color_with_alpha, (size, size), size)
                
                self.screen.blit(particle_surface, 
                                 (int(particle['x'] - size), int(particle['y'] - size)))
    
    def draw_move_history(self):
        # Move history panel
        if len(self.board.move_history) > 0:
            history_rect = pygame.Rect(720, 200, 250, 500)
            pygame.draw.rect(self.screen, COLORS['board'], history_rect, border_radius=10)
            pygame.draw.rect(self.screen, COLORS['text_primary'], history_rect, 2, border_radius=10)
            
            # Title
            title_text = self.font_medium.render("Move History", True, COLORS['text_primary'])
            self.screen.blit(title_text, (730, 210))
            
            # Recent moves (last 15)
            recent_moves = self.board.move_history[-15:]
            for i, move in enumerate(recent_moves):
                y_pos = 240 + i * 25
                player_color = COLORS['letter_s'] if move.player == "Human" else COLORS['letter_o']
                
                move_text = f"{move.player}: {move.letter} at ({move.row},{move.col})"
                if move.sos_formed > 0:
                    move_text += f" +{move.sos_formed}"
                
                move_surface = self.font_tiny.render(move_text, True, player_color)
                self.screen.blit(move_surface, (730, y_pos))
    
    def draw_winner_animation(self):
        current_time = pygame.time.get_ticks()
        animation_duration = current_time - self.winner_animation_time
        
        if animation_duration < 4000:  # Show for 4 seconds
            # Pulsing overlay
            pulse = abs(math.sin(animation_duration / 200)) * 100 + 50
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, pulse))
            self.screen.blit(overlay, (0, 0))
            
            # Winner text with effects
            if self.winner == "Human":
                winner_text = "🎉 VICTORY! 🎉"
                color = COLORS['accent_green']
            elif self.winner == "AI":
                winner_text = "🤖 AI DOMINANCE 🤖"
                color = COLORS['accent_red']
            else:
                winner_text = "🤝 PERFECT BALANCE 🤝"
                color = COLORS['accent_orange']
            
            # Animated text size
            size_multiplier = 1 + 0.3 * math.sin(animation_duration / 150)
            big_font = pygame.font.Font(None, int(64 * size_multiplier))
            
            winner_surface = big_font.render(winner_text, True, color)
            winner_rect = winner_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(winner_surface, winner_rect)
            
            # Score summary
            score_text = f"Final Score - Human: {self.human_player.score} | AI: {self.ai_player.score}"
            score_surface = self.font_medium.render(score_text, True, COLORS['text_primary'])
            score_rect = score_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80))
            self.screen.blit(score_surface, score_rect)
    
    def run(self):
        running = True
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update AI
            self.update_ai()
            
            # Update particles
            self.update_particles()
            
            # Draw everything
            self.draw()
            
            # Control frame rate
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    try:
        game = EnhancedSOSGame()
        game.run()
    except Exception as e:
        print(f"Error starting game: {e}")
        pygame.quit()
        sys.exit(1)