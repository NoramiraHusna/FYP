import pygame
import os
from config import *
from ui_elements import Button, draw_text

# 🔌 Grab the physical robot connection to check its status
from robot_interface import alpha_mini_hardware

# --- SPACESHIP THEME COLORS ---
SPACE_DARK    = (20, 20, 40)        
HOLO_PANEL    = (0, 0, 0, 180)      
TEXT_BRIGHT   = (220, 240, 255)     
TEXT_HIGHLIGHT= (255, 255, 0)       
NEON_GREEN    = (50, 255, 50)
NEON_RED      = (255, 80, 80)
NEON_CYAN     = (0, 255, 255)

class SummaryMenus:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.survey_bg = self._load_background()

    def _load_background(self):
        bg_path = os.path.join(ASSET_DIR, 'survey_bg.png')
        try:
            img = pygame.image.load(bg_path).convert()
            return pygame.transform.scale(img, (WIDTH, HEIGHT))
        except:
            return None

    def format_time(self, val):
        try:
            total_seconds = float(val)
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            return f"{minutes}m {seconds}s"
        except:
            return str(val)
            
    def _parse_time(self, val):
        """Helper to convert 'Xm Ys' or 'Xmin Ys' back to seconds for accurate sorting."""
        try:
            if isinstance(val, (int, float)): return float(val)
            s = str(val).replace('min', '').replace('m', '').replace('s', '').strip().split()
            if len(s) == 2: return int(s[0]) * 60 + int(s[1])
            return 0
        except:
            return 0
        
    def run_tutorial_end(self, history_data):
        btn_start = Button(WIDTH//2 - 160, HEIGHT - 100, 140, 60, "START", GREEN, (100, 255, 100))
        btn_repeat = Button(WIDTH//2 + 20, HEIGHT - 100, 140, 60, "REPEAT", RED, (255, 100, 100))
        
        running = True
        while running:
            # 🛡️ THE BRAIN LOCK
            queue_len = len(alpha_mini_hardware.speech_queue) if isinstance(alpha_mini_hardware.speech_queue, list) else alpha_mini_hardware.speech_queue.qsize()
            busy = getattr(alpha_mini_hardware, 'is_speaking', False) or queue_len > 0

            self.screen.fill(WHITE)
            draw_text(self.screen, "TUTORIAL SUMMARY", 50, BLACK, WIDTH//2, 50)
            
            start_y = 120
            col_x = [100, 300, 500, 700] 
            headers = ["FOOD", "INITIAL", "FINAL", "CHANGED?"]
            pygame.draw.line(self.screen, BLACK, (50, start_y + 30), (WIDTH-50, start_y + 30), 2)
            
            for i, header in enumerate(headers):
                draw_text(self.screen, header, 25, (50, 50, 50), col_x[i], start_y)

            for idx, row in enumerate(history_data):
                y_pos = start_y + 60 + (idx * 40)
                color = (0, 150, 0) if row['change'] else BLACK
                change_text = "YES" if row['change'] else "NO"
                draw_text(self.screen, row['food'], 20, BLACK, col_x[0], y_pos)
                draw_text(self.screen, row['init'], 20, BLACK, col_x[1], y_pos)
                draw_text(self.screen, row['final'], 20, color, col_x[2], y_pos)
                draw_text(self.screen, change_text, 20, color, col_x[3], y_pos)

            mx, my = pygame.mouse.get_pos()
            click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "EXIT"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.display.toggle_fullscreen()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not busy: 
                        click = True

            # 🎨 VISUAL LOCK: Change buttons if busy
            if busy:
                btn_start.text = "WAIT..."
                btn_start.color = (130, 130, 130)
                btn_start.hover_color = (130, 130, 130)
                
                btn_repeat.text = "WAIT..."
                btn_repeat.color = (130, 130, 130)
                btn_repeat.hover_color = (130, 130, 130)
                
                draw_text(self.screen, "⏳ Listen to Alpha Mini...", 18, (200, 50, 50), WIDTH//2, HEIGHT - 150)
            else:
                btn_start.text = "START"
                btn_start.color = GREEN
                btn_start.hover_color = (100, 255, 100)
                btn_start.check_hover((mx, my))
                
                btn_repeat.text = "REPEAT"
                btn_repeat.color = RED
                btn_repeat.hover_color = (255, 100, 100)
                btn_repeat.check_hover((mx, my))
                
                msg = "Press START if you are ready to play, or REPEAT to try the tutorial again."
                draw_text(self.screen, msg, 20, (100, 100, 100), WIDTH//2, HEIGHT - 150)
                
                # 🚫 ONLY allow clicks if unlocked
                if btn_start.is_clicked((mx, my), click): return "INTRO" 
                elif btn_repeat.is_clicked((mx, my), click): return "TUTORIAL"

            btn_start.draw(self.screen)
            btn_repeat.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

    def run_game_summary(self, all_sessions):
        # SKIPS THE LEADERBOARD ENTIRELY!
        return "QUESTIONNAIRE"