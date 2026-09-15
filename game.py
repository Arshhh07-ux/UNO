import pygame
import random
import math
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Tuple

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
DARK_RED = (139, 0, 0)
DARK_BLUE = (0, 0, 139)
DARK_GREEN = (0, 100, 0)
DARK_YELLOW = (139, 139, 0)

class CardColor(Enum):
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    WILD = (200, 200, 200)

class CardType(Enum):
    NUMBER = "number"
    SKIP = "skip"
    REVERSE = "reverse"
    DRAW_TWO = "draw_two"
    WILD = "wild"
    WILD_DRAW_FOUR = "wild_draw_four"

@dataclass
class Card:
    color: CardColor
    card_type: CardType
    number: Optional[int] = None
    
    def __repr__(self):
        if self.card_type == CardType.NUMBER:
            return f"{self.color.name} {self.number}"
        else:
            return f"{self.color.name} {self.card_type.name}"

class UnoGame:
    def __init__(self):
        self.deck: List[Card] = []
        self.discard_pile: List[Card] = []
        self.players: List[List[Card]] = [[], [], [], []]
        self.current_player = 0
        self.direction = 1  # 1 for clockwise, -1 for counter-clockwise
        self.game_over = False
        self.winner = None
        self.create_deck()
        self.shuffle_deck()
        self.deal_cards()
    
    def create_deck(self):
        """Create a standard Uno deck"""
        colors = [CardColor.RED, CardColor.BLUE, CardColor.GREEN, CardColor.YELLOW]
        
        # Number cards (0-9)
        for color in colors:
            self.deck.append(Card(color, CardType.NUMBER, 0))
            for num in range(1, 10):
                self.deck.extend([Card(color, CardType.NUMBER, num)] * 2)
        
        # Action cards
        for color in colors:
            self.deck.extend([Card(color, CardType.SKIP)] * 2)
            self.deck.extend([Card(color, CardType.REVERSE)] * 2)
            self.deck.extend([Card(color, CardType.DRAW_TWO)] * 2)
        
        # Wild cards
        for _ in range(4):
            self.deck.append(Card(CardColor.WILD, CardType.WILD))
            self.deck.append(Card(CardColor.WILD, CardType.WILD_DRAW_FOUR))
    
    def shuffle_deck(self):
        """Shuffle the deck"""
        random.shuffle(self.deck)
    
    def deal_cards(self):
        """Deal 7 cards to each player"""
        for _ in range(7):
            for player in self.players:
                if self.deck:
                    player.append(self.deck.pop())
        
        # Start discard pile
        if self.deck:
            self.discard_pile.append(self.deck.pop())
    
    def refill_deck(self):
        """Refill deck from discard pile when deck runs out"""
        if len(self.discard_pile) > 1:
            last_card = self.discard_pile.pop()
            self.deck.extend(self.discard_pile)
            self.discard_pile = [last_card]
            random.shuffle(self.deck)
    
    def draw_card(self, player_idx: int, num_cards: int = 1):
        """Draw cards for a player"""
        for _ in range(num_cards):
            if not self.deck:
                self.refill_deck()
            if self.deck:
                self.players[player_idx].append(self.deck.pop())
    
    def get_valid_moves(self, player_idx: int) -> List[int]:
        """Get indices of valid cards a player can play"""
        player_cards = self.players[player_idx]
        current_card = self.discard_pile[-1]
        valid_indices = []
        
        for idx, card in enumerate(player_cards):
            if self.is_valid_move(card, current_card):
                valid_indices.append(idx)
        
        return valid_indices
    
    def is_valid_move(self, card: Card, current_card: Card) -> bool:
        """Check if a card can be played"""
        if card.card_type == CardType.WILD or card.card_type == CardType.WILD_DRAW_FOUR:
            return True
        
        if card.color == current_card.color:
            return True
        
        if card.card_type == current_card.card_type:
            return True
        
        if card.card_type == CardType.NUMBER and current_card.card_type == CardType.NUMBER:
            return card.number == current_card.number
        
        return False
    
    def play_card(self, player_idx: int, card_idx: int):
        """Play a card"""
        card = self.players[player_idx].pop(card_idx)
        self.discard_pile.append(card)
        
        # Check for win
        if len(self.players[player_idx]) == 0:
            self.game_over = True
            self.winner = player_idx
        
        # Apply card effects
        self.apply_card_effect(card, player_idx)
        
        # Move to next player
        self.current_player = (self.current_player + self.direction) % 4
    
    def apply_card_effect(self, card: Card, player_idx: int):
        """Apply special card effects"""
        if card.card_type == CardType.SKIP:
            self.current_player = (self.current_player + self.direction) % 4
        
        elif card.card_type == CardType.REVERSE:
            if len([p for p in self.players if len(p) > 0]) > 2:
                self.direction *= -1
            else:
                self.current_player = (self.current_player + self.direction) % 4
        
        elif card.card_type == CardType.DRAW_TWO:
            next_player = (self.current_player + self.direction) % 4
            self.draw_card(next_player, 2)
            self.current_player = (next_player + self.direction) % 4
        
        elif card.card_type == CardType.WILD_DRAW_FOUR:
            next_player = (self.current_player + self.direction) % 4
            self.draw_card(next_player, 4)
            self.current_player = (next_player + self.direction) % 4

class Card3DRenderer:
    def __init__(self):
        self.rotation_x = 0
        self.rotation_y = 0
        self.scale = 1.0
    
    def project_3d_to_2d(self, x: float, y: float, z: float, center_x: float, center_y: float) -> Tuple[int, int]:
        """Project 3D coordinates to 2D using perspective"""
        scale_factor = 500 / (500 + z)
        proj_x = center_x + x * scale_factor
        proj_y = center_y + y * scale_factor
        return (int(proj_x), int(proj_y))
    
    def draw_card_3d(self, surface: pygame.Surface, card: Card, x: float, y: float, z: float, 
                     angle: float = 0, scale: float = 1.0):
        """Draw a card with 3D perspective"""
        # Card dimensions
        width, height = 80, 120
        
        # Apply perspective scaling
        perspective_scale = (500 + z * 100) / 600
        card_width = int(width * perspective_scale * scale)
        card_height = int(height * perspective_scale * scale)
        
        # Calculate position
        screen_x = int(x - card_width // 2)
        screen_y = int(y - card_height // 2)
        
        # Draw card background
        color = card.color.value if card.color != CardColor.WILD else (200, 200, 200)
        pygame.draw.rect(surface, color, (screen_x, screen_y, card_width, card_height), border_radius=5)
        pygame.draw.rect(surface, BLACK, (screen_x, screen_y, card_width, card_height), 2, border_radius=5)
        
        # Draw card content
        font_small = pygame.font.Font(None, max(12, int(16 * perspective_scale)))
        font_large = pygame.font.Font(None, max(20, int(32 * perspective_scale)))
        
        if card.card_type == CardType.NUMBER:
            text = font_large.render(str(card.number), True, BLACK)
        else:
            text = font_small.render(card.card_type.name.replace("_", " "), True, BLACK)
        
        text_rect = text.get_rect(center=(screen_x + card_width // 2, screen_y + card_height // 2))
        surface.blit(text, text_rect)

class UnoGameUI:
    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("UNO 3D - Card Game")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        self.game = UnoGame()
        self.card_renderer = Card3DRenderer()
        
        self.selected_card = None
        self.animation_time = 0
        self.message = "Player 1's Turn"
        self.message_timer = 0
    
    def handle_events(self) -> bool:
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r:
                    self.game = UnoGame()
                    self.selected_card = None
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game.current_player == 0:  # Only human player
                    self.handle_card_click(event.pos)
        
        return True
    
    def handle_card_click(self, pos: Tuple[int, int]):
        """Handle card clicks for player 1"""
        player_cards = self.game.players[0]
        
        # Calculate card positions (bottom of screen)
        card_spacing = 100
        start_x = SCREEN_WIDTH // 2 - (len(player_cards) * card_spacing) // 2
        
        for idx, card in enumerate(player_cards):
            card_x = start_x + idx * card_spacing
            card_y = SCREEN_HEIGHT - 150
            card_rect = pygame.Rect(card_x - 40, card_y - 60, 80, 120)
            
            if card_rect.collidepoint(pos):
                if idx in self.game.get_valid_moves(0):
                    self.game.play_card(0, idx)
                    self.message = f"Player {self.game.current_player + 1}'s Turn"
                    self.message_timer = 120
                    self.selected_card = None
                else:
                    self.message = "Invalid Move!"
                    self.message_timer = 60
    
    def ai_play(self):
        """AI player move"""
        player_idx = self.game.current_player
        valid_moves = self.game.get_valid_moves(player_idx)
        
        if valid_moves:
            # AI chooses a random valid card
            card_idx = random.choice(valid_moves)
            self.game.play_card(player_idx, card_idx)
            self.message = f"Player {self.game.current_player + 1}'s Turn"
            self.message_timer = 120
        else:
            # Draw a card
            self.game.draw_card(player_idx)
            self.game.current_player = (self.game.current_player + self.game.direction) % 4
    
    def update(self):
        """Update game state"""
        self.animation_time += 1
        if self.message_timer > 0:
            self.message_timer -= 1
        
        # AI turns (simplified - just delay then move)
        if not self.game.game_over and self.game.current_player != 0:
            if self.animation_time % 60 == 0:  # Every 1 second
                self.ai_play()
    
    def draw(self):
        """Draw the game"""
        self.screen.fill(GRAY)
        
        # Draw deck and discard pile
        self.draw_deck_area()
        
        # Draw player cards
        self.draw_player_hands()
        
        # Draw current card
        self.draw_current_card()
        
        # Draw UI
        self.draw_ui()
        
        # Draw game over screen
        if self.game.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_deck_area(self):
        """Draw deck and discard pile area"""
        deck_x, deck_y = 150, 100
        discard_x, discard_y = SCREEN_WIDTH - 150, 100
        
        # Deck
        pygame.draw.rect(self.screen, BLUE, (deck_x - 40, deck_y - 60, 80, 120), 2, border_radius=5)
        deck_text = self.font_small.render(f"Deck: {len(self.game.deck)}", True, WHITE)
        self.screen.blit(deck_text, (deck_x - 60, deck_y + 70))
        
        # Discard pile
        if self.game.discard_pile:
            card = self.game.discard_pile[-1]
            color = card.color.value if card.color != CardColor.WILD else (200, 200, 200)
            pygame.draw.rect(self.screen, color, (discard_x - 40, discard_y - 60, 80, 120), border_radius=5)
            pygame.draw.rect(self.screen, BLACK, (discard_x - 40, discard_y - 60, 80, 120), 2, border_radius=5)
            
            if card.card_type == CardType.NUMBER:
                text = self.font_large.render(str(card.number), True, BLACK)
            else:
                text = self.font_small.render(card.card_type.name.replace("_", " "), True, BLACK)
            text_rect = text.get_rect(center=(discard_x, discard_y))
            self.screen.blit(text, text_rect)
    
    def draw_player_hands(self):
        """Draw player hands"""
        positions = [
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150, "You (Player 1)"),  # Bottom
            (150, SCREEN_HEIGHT // 2, "Player 2"),  # Left
            (SCREEN_WIDTH // 2, 150, "Player 3"),  # Top
            (SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2, "Player 4"),  # Right
        ]
        
        for player_idx, (pos_x, pos_y, name) in enumerate(positions):
            hand_size = len(self.game.players[player_idx])
            hand_text = self.font_small.render(f"{name}: {hand_size} cards", True, WHITE)
            
            if player_idx == self.game.current_player:
                hand_text = self.font_small.render(f"{name}: {hand_size} cards (TURN)", True, GREEN)
            
            if player_idx == 0:  # Draw all cards for player 1
                card_spacing = 100
                start_x = SCREEN_WIDTH // 2 - (hand_size * card_spacing) // 2
                
                for idx, card in enumerate(self.game.players[player_idx]):
                    card_x = start_x + idx * card_spacing
                    card_y = pos_y
                    
                    # Lift card on hover or if selected
                    lift = 10 if idx in self.game.get_valid_moves(0) else 0
                    
                    color = card.color.value if card.color != CardColor.WILD else (200, 200, 200)
                    pygame.draw.rect(self.screen, color, (card_x - 40, card_y - 60 - lift, 80, 120), border_radius=5)
                    pygame.draw.rect(self.screen, BLACK, (card_x - 40, card_y - 60 - lift, 80, 120), 2, border_radius=5)
                    
                    if card.card_type == CardType.NUMBER:
                        text = self.font_large.render(str(card.number), True, BLACK)
                    else:
                        text = self.font_small.render(card.card_type.name.replace("_", " "), True, BLACK)
                    text_rect = text.get_rect(center=(card_x, card_y - lift))
                    self.screen.blit(text, text_rect)
            
            self.screen.blit(hand_text, (pos_x - 80, pos_y - 100))
    
    def draw_current_card(self):
        """Draw the current card in the center"""
        if self.game.discard_pile:
            card = self.game.discard_pile[-1]
            color = card.color.value if card.color != CardColor.WILD else (200, 200, 200)
            
            x, y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
            pygame.draw.rect(self.screen, color, (x - 80, y - 120, 160, 240), border_radius=10)
            pygame.draw.rect(self.screen, BLACK, (x - 80, y - 120, 160, 240), 4, border_radius=10)
            
            if card.card_type == CardType.NUMBER:
                text = self.font_large.render(str(card.number), True, BLACK)
            else:
                text = self.font_medium.render(card.card_type.name.replace("_", " "), True, BLACK)
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
    
    def draw_ui(self):
        """Draw UI elements"""
        # Message
        if self.message_timer > 0:
            msg_text = self.font_medium.render(self.message, True, WHITE)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
            self.screen.blit(msg_text, msg_rect)
        
        # Instructions
        instr_text = self.font_small.render("Click cards to play | R: Restart | ESC: Quit", True, WHITE)
        self.screen.blit(instr_text, (20, SCREEN_HEIGHT - 30))
    
    def draw_game_over(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Winner text
        winner_text = self.font_large.render(f"Player {self.game.winner + 1} Wins!", True, GREEN)
        winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(winner_text, winner_rect)
        
        # Restart prompt
        restart_text = self.font_medium.render("Press R to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    app = UnoGameUI()
    app.run()
          
