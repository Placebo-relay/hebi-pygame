from screeninfo import get_monitors
import pygame
import win32api
import win32con
import win32gui
import random
import sys
import os
import json
from pygame import gfxdraw

# Color definitions
fuchsia = (255, 0, 128)  # Transparency color
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
DARK_GRAY = (50, 50, 50)
PAUSE_OVERLAY = (0, 0, 0, 150)  # Semi-transparent black for pause

# Initialize pygame
pygame.init()
pygame.display.set_caption("Hebi")
icon_image = pygame.image.load('icon.png')
pygame.display.set_icon(icon_image)

# Get primary monitor size
first_monitor = get_monitors()[0]
size = width, height = first_monitor.width, first_monitor.height

# Create transparent window
screen = pygame.display.set_mode(size, pygame.NOFRAME)
hwnd = pygame.display.get_wm_info()["window"]

# Set window attributes for transparency
win32gui.SetWindowLong(
    hwnd,
    win32con.GWL_EXSTYLE,
    win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED
)
win32gui.SetLayeredWindowAttributes(
    hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY
)
win32gui.SetWindowPos(
    hwnd, win32con.HWND_TOPMOST, 0, 0, width, height, 0
)

# Game variables
clock = pygame.time.Clock()
snake_block = 20
snake_speed = 15

# Fonts
font_small = pygame.font.SysFont('Arial', 24)
font_medium = pygame.font.SysFont('Arial', 36)
font_large = pygame.font.SysFont('Arial', 72, bold=True)

# High score file
HIGH_SCORE_FILE = "snake_scores.json"

class HighScoreManager:
    def __init__(self):
        self.scores = []
        self.load_scores()
        
    def load_scores(self):
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as f:
                self.scores = json.load(f)
        else:
            self.scores = []
    
    def save_scores(self):
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump(self.scores, f)
    
    def add_score(self, name, score):
        self.scores.append({"name": name, "score": score})
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.scores = self.scores[:10]  # Keep top 10
        self.save_scores()
    
    def is_high_score(self, score):
        if not self.scores:
            return True
        return score > self.scores[-1]["score"]

high_score_manager = HighScoreManager()

def draw_score(score):
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, [20, 20])

def draw_high_scores():
    if not high_score_manager.scores:
        return
    
    hs_text = font_small.render("HIGH SCORES:", True, GOLD)
    screen.blit(hs_text, [width - 220, 20])
    
    for i, entry in enumerate(high_score_manager.scores[:3]):
        entry_text = f"{i+1}. {entry['name']}: {entry['score']}"
        text = font_small.render(entry_text, True, WHITE)
        screen.blit(text, [width - 220, 50 + i * 30])

def draw_controls():
    controls = font_small.render("ARROWS: Move | P: Pause | Q: Quit", True, WHITE)
    screen.blit(controls, [width//2 - controls.get_width()//2, height - 40])

def draw_pause():
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill(PAUSE_OVERLAY)
    screen.blit(overlay, (0, 0))
    
    pause_text = font_large.render("PAUSED", True, WHITE)
    screen.blit(pause_text, (width//2 - pause_text.get_width()//2, height//2 - 50))
    
    continue_text = font_medium.render("Press P to continue", True, WHITE)
    screen.blit(continue_text, (width//2 - continue_text.get_width()//2, height//2 + 50))

def get_player_name(score):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    
    input_width = 400
    input_height = 60
    input_box = pygame.Rect(width/2 - input_width/2, height/2 + 40, input_width, input_height)
    color_inactive = pygame.Color(100, 100, 100)
    color_active = pygame.Color(140, 140, 140)
    color = color_inactive
    active = False
    text = ''
    done = False
    name_recorded = False
    
    title_y = height/2 - 120
    score_y = height/2 - 60
    instruction_y = height/2 - 10
    
    while not done:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)
                color = color_active if active else color_inactive
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # Allow quitting during name entry
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
        
        screen.blit(overlay, (0, 0))
        
        GOOD_SCORE = "NEW HIGH SCORE!"
        TROLL_SCORE = "WOW SO ZERO, VERY NICE!"
        if score: TROLL_SCORE = GOOD_SCORE
        title = font_large.render(TROLL_SCORE, True, GOLD)
        title_rect = title.get_rect(center=(width/2, title_y))
        screen.blit(title, title_rect)
        
        score_text = font_medium.render(f"Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(width/2, score_y))
        screen.blit(score_text, score_rect)
        
        instruct = font_small.render("Enter your name (15 chars max):", True, WHITE)
        instruct_rect = instruct.get_rect(center=(width/2, instruction_y))
        screen.blit(instruct, instruct_rect)
        
        pygame.draw.rect(screen, color, input_box, border_radius=5)
        pygame.draw.rect(screen, DARK_GRAY, input_box.inflate(-4, -4), border_radius=3)
        
        txt_surface = font_medium.render(text, True, WHITE)
        text_y = input_box.y + (input_height - txt_surface.get_height()) // 2
        screen.blit(txt_surface, (input_box.x + 15, text_y))
        
        if active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = input_box.x + 15 + txt_surface.get_width()
            pygame.draw.line(screen, WHITE, 
                           (cursor_x, input_box.y + 15),
                           (cursor_x, input_box.y + input_height - 15), 2)
        
        pygame.display.flip()
        clock.tick(30)
    
    if name_recorded:
        high_score_manager.add_score(text.strip() or "Nameless Anon", score)
    return text.strip() or "Nameless Anon"

def show_welcome_screen():
    screen.fill(fuchsia)
    
    title = font_large.render("TRANSPARENT SNAKE", True, GREEN)
    screen.blit(title, (width//2 - title.get_width()//2, height//3))
    
    controls = [
        "Use ARROW KEYS to move",
        "Press P to pause the game",
        "Press Q anytime to quit",
        "",
        "Press any key to start"
    ]
    
    for i, line in enumerate(controls):
        text = font_medium.render(line, True, WHITE)
        screen.blit(text, (width//2 - text.get_width()//2, height//2 + i * 40))
    
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

def game_loop():
    show_welcome_screen()
    
    game_over = False
    game_close = False
    paused = False
    high_score_processed = False
    
    # Starting position
    x1 = width / 2
    y1 = height / 2
    
    # Change in position
    x1_change = 0
    y1_change = 0
    
    # Snake body
    snake_list = []
    length_of_snake = 1
    
    # Food position
    foodx = round(random.randrange(0, width - snake_block) / 20.0) * 20.0
    foody = round(random.randrange(0, height - snake_block) / 20.0) * 20.0
    
    score = 0
    
    while not game_over:
        # Game over state
        while game_close:
            screen.fill(fuchsia)
            
            if not high_score_processed and high_score_manager.is_high_score(score):
                get_player_name(score)
                high_score_processed = True
            
            msg = font_large.render("GAME OVER", True, RED)
            msg_rect = msg.get_rect(center=(width/2, height/3))
            screen.blit(msg, msg_rect)
            
            options = font_medium.render("Press Q to Quit or C to Continue", True, WHITE)
            options_rect = options.get_rect(center=(width/2, height/2 + 100))
            screen.blit(options, options_rect)
            
            draw_score(score)
            draw_high_scores()
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_close = False
                        high_score_processed = False
                        x1 = width / 2
                        y1 = height / 2
                        x1_change = 0
                        y1_change = 0
                        snake_list = []
                        length_of_snake = 1
                        foodx = round(random.randrange(0, width - snake_block) / 20.0) * 20.0
                        foody = round(random.randrange(0, height - snake_block) / 20.0) * 20.0
                        score = 0
                        break
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # Global quit
                    game_over = True
                elif event.key == pygame.K_p:  # Pause toggle
                    paused = not paused
                elif not paused:
                    if event.key == pygame.K_LEFT and x1_change == 0:
                        x1_change = -snake_block
                        y1_change = 0
                    elif event.key == pygame.K_RIGHT and x1_change == 0:
                        x1_change = snake_block
                        y1_change = 0
                    elif event.key == pygame.K_UP and y1_change == 0:
                        y1_change = -snake_block
                        x1_change = 0
                    elif event.key == pygame.K_DOWN and y1_change == 0:
                        y1_change = snake_block
                        x1_change = 0
        
        if paused:
            draw_pause()
            pygame.display.update()
            clock.tick(snake_speed)
            continue
        
        # Game logic
        if x1 >= width or x1 < 0 or y1 >= height or y1 < 0:
            game_close = True
            
        x1 += x1_change
        y1 += y1_change
        screen.fill(fuchsia)
        
        # Draw food
        pygame.gfxdraw.filled_circle(screen, int(foodx + snake_block/2), int(foody + snake_block/2), 
                                   int(snake_block/2), RED)
        pygame.gfxdraw.aacircle(screen, int(foodx + snake_block/2), int(foody + snake_block/2), 
                              int(snake_block/2), BLACK)
        
        snake_head = [x1, y1]
        snake_list.append(snake_head)
        
        if len(snake_list) > length_of_snake:
            del snake_list[0]
            
        for x in snake_list[:-1]:
            if x == snake_head:
                game_close = True
                
        # Draw snake
        for i, segment in enumerate(snake_list):
            if i == len(snake_list) - 1:
                color = GREEN
            else:
                fade = 0.3 + 0.7 * (i / len(snake_list))
                color = (0, int(255 * fade), 0)
            
            pygame.draw.rect(screen, color, [segment[0], segment[1], snake_block, snake_block])
            pygame.draw.rect(screen, BLACK, [segment[0], segment[1], snake_block, snake_block], 1)
        
        draw_score(score)
        draw_high_scores()
        draw_controls()
        pygame.display.update()
        
        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, width - snake_block) / 20.0) * 20.0
            foody = round(random.randrange(0, height - snake_block) / 20.0) * 20.0
            length_of_snake += 1
            score += 10
            
        clock.tick(snake_speed)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()