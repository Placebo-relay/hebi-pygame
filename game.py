import random
import sys
import os
import json
from screeninfo import get_monitors
import pygame
import win32api
import win32con
import win32gui
from pygame import gfxdraw

class Colors:
    """Container for color constants"""
    FUCHSIA = (255, 0, 128)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    GOLD = (255, 215, 0)
    DARK_GRAY = (50, 50, 50)
    PAUSE_OVERLAY = (0, 0, 0, 150)

class GameSettings:
    """Game configuration settings"""
    def __init__(self):
        self.snake_block = 20
        self.snake_speed = 15
        self.high_score_file = "snake_scores.json"
        self.icon_path = 'icon.png'
        self.caption = "Hebi"

class SnakeGame:
    """Main game class"""
    def __init__(self):
        self.settings = GameSettings()
        self.colors = Colors()
        self._initialize_pygame()
        self._setup_window()
        self._load_fonts()
        self.high_score_manager = HighScoreManager(self.settings.high_score_file)
        self.clock = pygame.time.Clock()
        
    def _initialize_pygame(self):
        """Initialize pygame and set basic properties"""
        pygame.init()
        pygame.display.set_caption(self.settings.caption)
        if os.path.exists(self.settings.icon_path):
            icon_image = pygame.image.load(self.settings.icon_path)
            pygame.display.set_icon(icon_image)
        
    def _setup_window(self):
        """Create and configure the game window"""
        first_monitor = get_monitors()[0]
        self.width, self.height = first_monitor.width, first_monitor.height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME)
        
        # Windows-specific transparency settings
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(
            hwnd,
            win32con.GWL_EXSTYLE,
            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED
        )
        win32gui.SetLayeredWindowAttributes(
            hwnd, win32api.RGB(*self.colors.FUCHSIA), 0, win32con.LWA_COLORKEY
        )
        win32gui.SetWindowPos(
            hwnd, win32con.HWND_TOPMOST, 0, 0, self.width, self.height, 0
        )
    
    def _load_fonts(self):
        """Initialize game fonts"""
        self.font_small = pygame.font.SysFont('Arial', 24)
        self.font_medium = pygame.font.SysFont('Arial', 36)
        self.font_large = pygame.font.SysFont('Arial', 72, bold=True)
    
    def run(self):
        """Main game loop"""
        self._show_welcome_screen()
        
        while True:
            # Game state variables
            game_over = False
            game_close = False
            paused = False
            high_score_processed = False
            
            # Snake initialization
            x1, y1 = self.width / 2, self.height / 2
            x1_change, y1_change = 0, 0
            snake_list = []
            length_of_snake = 1
            
            # Food initialization
            foodx, foody = self._generate_food_position()
            score = 0
            
            while not game_over:
                # Game over state
                while game_close:
                    self.screen.fill(self.colors.FUCHSIA)
                    
                    if not high_score_processed and self.high_score_manager.is_high_score(score):
                        self._get_player_name(score)
                        high_score_processed = True
                    
                    self._draw_game_over(score)
                    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_q:
                                pygame.quit()
                                sys.exit()
                            if event.key == pygame.K_c:
                                game_close = False
                                high_score_processed = False
                                x1, y1 = self.width / 2, self.height / 2
                                x1_change = y1_change = 0
                                snake_list = []
                                length_of_snake = 1
                                foodx, foody = self._generate_food_position()
                                score = 0
                
                # Event handling
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:  # Global quit
                            pygame.quit()
                            sys.exit()
                        elif event.key == pygame.K_p:  # Pause toggle
                            paused = not paused
                        elif not paused:
                            if event.key == pygame.K_LEFT and x1_change == 0:
                                x1_change = -self.settings.snake_block
                                y1_change = 0
                            elif event.key == pygame.K_RIGHT and x1_change == 0:
                                x1_change = self.settings.snake_block
                                y1_change = 0
                            elif event.key == pygame.K_UP and y1_change == 0:
                                y1_change = -self.settings.snake_block
                                x1_change = 0
                            elif event.key == pygame.K_DOWN and y1_change == 0:
                                y1_change = self.settings.snake_block
                                x1_change = 0
                
                if paused:
                    self._draw_pause()
                    pygame.display.update()
                    self.clock.tick(self.settings.snake_speed)
                    continue
                
                # Game logic
                if x1 >= self.width or x1 < 0 or y1 >= self.height or y1 < 0:
                    game_close = True
                
                x1 += x1_change
                y1 += y1_change
                self.screen.fill(self.colors.FUCHSIA)
                
                # Draw food
                self._draw_food(foodx, foody)
                
                # Update snake
                snake_head = [x1, y1]
                snake_list.append(snake_head)
                if len(snake_list) > length_of_snake:
                    del snake_list[0]
                
                # Check self collision
                for x in snake_list[:-1]:
                    if x == snake_head:
                        game_close = True
                
                # Draw snake
                self._draw_snake(snake_list)
                
                # Draw UI elements
                self._draw_score(score)
                self._draw_high_scores()
                self._draw_controls()
                
                pygame.display.update()
                
                # Food collision
                if x1 == foodx and y1 == foody:
                    foodx, foody = self._generate_food_position()
                    length_of_snake += 1
                    score += 10
                
                self.clock.tick(self.settings.snake_speed)
    
    def _generate_food_position(self):
        """Generate random food position"""
        return (
            round(random.randrange(0, self.width - self.settings.snake_block) / 20.0) * 20.0,
            round(random.randrange(0, self.height - self.settings.snake_block) / 20.0) * 20.0
        )
    
    def _draw_food(self, x, y):
        """Draw food at given position"""
        center_x = int(x + self.settings.snake_block/2)
        center_y = int(y + self.settings.snake_block/2)
        radius = int(self.settings.snake_block/2)
        pygame.gfxdraw.filled_circle(self.screen, center_x, center_y, radius, self.colors.RED)
        pygame.gfxdraw.aacircle(self.screen, center_x, center_y, radius, self.colors.BLACK)
    
    def _draw_snake(self, snake_list):
        """Draw the snake"""
        for i, segment in enumerate(snake_list):
            if i == len(snake_list) - 1:  # Head
                color = self.colors.GREEN
            else:  # Body with gradient
                fade = 0.3 + 0.7 * (i / len(snake_list))
                color = (0, int(255 * fade), 0)
            
            pygame.draw.rect(self.screen, color, [segment[0], segment[1], 
                           self.settings.snake_block, self.settings.snake_block])
            pygame.draw.rect(self.screen, self.colors.BLACK, 
                           [segment[0], segment[1], self.settings.snake_block, self.settings.snake_block], 1)
    
    def _draw_score(self, score):
        """Draw current score"""
        score_text = self.font_small.render(f"Score: {score}", True, self.colors.WHITE)
        self.screen.blit(score_text, [20, 20])
    
    def _draw_high_scores(self):
        """Draw high score list"""
        if not self.high_score_manager.scores:
            return
        
        hs_text = self.font_small.render("HIGH SCORES:", True, self.colors.GOLD)
        self.screen.blit(hs_text, [self.width - 220, 20])
        
        for i, entry in enumerate(self.high_score_manager.scores[:3]):
            entry_text = f"{i+1}. {entry['name']}: {entry['score']}"
            text = self.font_small.render(entry_text, True, self.colors.WHITE)
            self.screen.blit(text, [self.width - 220, 50 + i * 30])
    
    def _draw_controls(self):
        """Draw control instructions"""
        controls = self.font_small.render("ARROWS: Move | P: Pause | Q: Quit", True, self.colors.WHITE)
        self.screen.blit(controls, [self.width//2 - controls.get_width()//2, self.height - 40])
    
    def _draw_pause(self):
        """Draw pause screen"""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(self.colors.PAUSE_OVERLAY)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("PAUSED", True, self.colors.WHITE)
        self.screen.blit(pause_text, (self.width//2 - pause_text.get_width()//2, self.height//2 - 50))
        
        continue_text = self.font_medium.render("Press P to continue", True, self.colors.WHITE)
        self.screen.blit(continue_text, (self.width//2 - continue_text.get_width()//2, self.height//2 + 50))
    
    def _draw_game_over(self, score):
        """Draw game over screen"""
        msg = self.font_large.render("GAME OVER", True, self.colors.RED)
        msg_rect = msg.get_rect(center=(self.width/2, self.height/3))
        self.screen.blit(msg, msg_rect)
        
        options = self.font_medium.render("Press Q to Quit or C to Continue", True, self.colors.WHITE)
        options_rect = options.get_rect(center=(self.width/2, self.height/2 + 100))
        self.screen.blit(options, options_rect)
        
        self._draw_score(score)
        self._draw_high_scores()
        pygame.display.update()
    
    def _show_welcome_screen(self):
        """Show welcome screen"""
        self.screen.fill(self.colors.FUCHSIA)
        
        title = self.font_large.render("HEBI THE TRANSPARENT SNAKE", True, self.colors.GREEN)
        self.screen.blit(title, (self.width//2 - title.get_width()//2, self.height//3))
        
        controls = [
            "Use ARROW KEYS to move",
            "Press P to pause the game",
            "Press Q anytime to quit",
            "",
            "Press any key to start"
        ]
        
        for i, line in enumerate(controls):
            text = self.font_medium.render(line, True, self.colors.WHITE)
            self.screen.blit(text, (self.width//2 - text.get_width()//2, self.height//2 + i * 40))
        
        pygame.display.update()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    waiting = False
    
    def _get_player_name(self, score):
        """Get player name for high score"""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        
        input_width = 400
        input_height = 60
        input_box = pygame.Rect(self.width/2 - input_width/2, self.height/2 + 40, input_width, input_height)
        color_inactive = pygame.Color(100, 100, 100)
        color_active = pygame.Color(140, 140, 140)
        color = color_inactive
        active = False
        text = ''
        done = False
        name_recorded = False
        
        title_y = self.height/2 - 120
        score_y = self.height/2 - 60
        instruction_y = self.height/2 - 10
        
        while not done:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    active = input_box.collidepoint(event.pos)
                    color = color_active if active else color_inactive
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        done = True
                        pygame.quit()
                        sys.exit()
                    if active:
                        if event.key == pygame.K_RETURN:
                            if text.strip():
                                done = True
                                name_recorded = True
                            else:
                                return "Nameless Anon"
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        elif len(text) < 15:
                            text += event.unicode
            
            self.screen.blit(overlay, (0, 0))
            
            GOOD_SCORE = "NEW HIGH SCORE!"
            TROLL_SCORE = "WOW SO ZERO, VERY NICE!"
            if score: TROLL_SCORE = GOOD_SCORE
            title = self.font_large.render(TROLL_SCORE, True, self.colors.GOLD)
            title_rect = title.get_rect(center=(self.width/2, title_y))
            self.screen.blit(title, title_rect)
            
            score_text = self.font_medium.render(f"Score: {score}", True, self.colors.WHITE)
            score_rect = score_text.get_rect(center=(self.width/2, score_y))
            self.screen.blit(score_text, score_rect)
            
            instruct = self.font_small.render("Enter your name (15 chars max):", True, self.colors.WHITE)
            instruct_rect = instruct.get_rect(center=(self.width/2, instruction_y))
            self.screen.blit(instruct, instruct_rect)
            
            pygame.draw.rect(self.screen, color, input_box, border_radius=5)
            pygame.draw.rect(self.screen, self.colors.DARK_GRAY, input_box.inflate(-4, -4), border_radius=3)
            
            txt_surface = self.font_medium.render(text, True, self.colors.WHITE)
            text_y = input_box.y + (input_height - txt_surface.get_height()) // 2
            self.screen.blit(txt_surface, (input_box.x + 15, text_y))
            
            if active and pygame.time.get_ticks() % 1000 < 500:
                cursor_x = input_box.x + 15 + txt_surface.get_width()
                pygame.draw.line(self.screen, self.colors.WHITE, 
                               (cursor_x, input_box.y + 15),
                               (cursor_x, input_box.y + input_height - 15), 2)
            
            pygame.display.flip()
            self.clock.tick(30)
        
        if name_recorded:
            self.high_score_manager.add_score(text.strip() or "Nameless Anon", score)
        return text.strip() or "Nameless Anon"

class HighScoreManager:
    """Handles high score loading and saving"""
    def __init__(self, filename):
        self.filename = filename
        self.scores = []
        self._load_scores()
        
    def _load_scores(self):
        """Load scores from file"""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.scores = json.load(f)
    
    def save_scores(self):
        """Save scores to file"""
        with open(self.filename, 'w') as f:
            json.dump(self.scores, f)
    
    def add_score(self, name, score):
        """Add a new score and maintain top 10"""
        self.scores.append({"name": name, "score": score})
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.scores = self.scores[:10]
        self.save_scores()
    
    def is_high_score(self, score):
        """Check if score qualifies as high score"""
        if not self.scores:
            return True
        return score > self.scores[-1]["score"]

if __name__ == "__main__":
    game = SnakeGame()
    game.run()