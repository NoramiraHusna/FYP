import pygame
import os
from config import *
from ui_elements import Button, draw_text
from interaction_data import UI_CREAM, UI_MOCHA, UI_SHADOW 

# 🔌 Grab the physical robot connection
from robot_interface import alpha_mini_hardware

class RulesMenu:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.bg_image = self._load_background('menu_background.png')

    def _load_background(self, filename):
        bg_path = os.path.join(ASSET_DIR, filename)
        try:
            img = pygame.image.load(bg_path).convert()
            return pygame.transform.scale(img, (WIDTH, HEIGHT))
        except Exception:
            return None

    def queue_rules_speech(self):
        """🗣️ Detailed speech for Alpha Mini."""
        alpha_mini_hardware.speak("SYSTEM", "These are the rules for your adventure game, Traveler. Please listen closely.")
        alpha_mini_hardware.speak("SYSTEM", "First. There is no right or wrong answer in this game. You are free to choose whatever food you feel is best for the situation.")
        alpha_mini_hardware.speak("SYSTEM", "Second. During the game, I will give you my insights, but you are completely free to either follow or ignore my advice. It is entirely up to you.")
        alpha_mini_hardware.speak("SYSTEM", "Third. If you encounter any technical issues or need assistance at any point, please ask Sister Husna for help.")
        alpha_mini_hardware.speak("SYSTEM", "If you understand the rules, click the 'Yes' button below. If you need me to repeat them, click 'No'.")

    def run(self):
        btn_w = 220
        btn_h = 50
        gap = 30
        start_x = (WIDTH // 2) - ((btn_w * 2 + gap) // 2)
        
        btn_repeat = Button(start_x, HEIGHT - 90, btn_w, btn_h, "NO", (220, 150, 40), (255, 180, 80))
        btn_continue = Button(start_x + btn_w + gap, HEIGHT - 90, btn_w, btn_h, "YES", GREEN, (100, 255, 100))
        
        # 📱 SIMPLIFIED ON-SCREEN UI TEXT
        rules_ui = [
            "1. No right or wrong answer.",
            "2. Follow or ignore advice.",
            "3. Ask Sister Husna for help."
        ]

        self.queue_rules_speech()
        frames_passed = 0
        
        running = True
        while running:
            frames_passed += 1
            self.clock.tick(60)

            # 🛡️ THE BRAIN LOCK & SPEECH TRACKER
            queue_len = len(alpha_mini_hardware.speech_queue) if isinstance(alpha_mini_hardware.speech_queue, list) else alpha_mini_hardware.speech_queue.qsize()
            is_speaking = getattr(alpha_mini_hardware, 'is_speaking', False)
            
            busy = is_speaking or queue_len > 0 or frames_passed < 10 

            # --- NON-BLOCKING EVENT HANDLING ---
            mx, my = pygame.mouse.get_pos()
            click = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "EXIT"
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.display.toggle_fullscreen()
                    
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not busy: click = True
                        
            # Draw Background
            if self.bg_image:
                self.screen.blit(self.bg_image, (0, 0))
            else:
                self.screen.fill(BLACK)
            
            # 🎨 RESTORED AESTHETIC: Shadow, Cream Background, Mocha Borders
            box_w, box_h = 600, 280
            rules_rect = pygame.Rect(WIDTH//2 - box_w//2, HEIGHT//2 - box_h//2 - 30, box_w, box_h)
            
            shadow_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, UI_SHADOW, shadow_surf.get_rect(), border_radius=15)
            self.screen.blit(shadow_surf, (rules_rect.x + 8, rules_rect.y + 8))
            
            pygame.draw.rect(self.screen, UI_CREAM, rules_rect, border_radius=15)
            pygame.draw.rect(self.screen, UI_MOCHA, rules_rect, 4, border_radius=15)
            
            draw_text(self.screen, "GAME RULES", 36, UI_MOCHA, WIDTH//2, rules_rect.y + 40)
            pygame.draw.line(self.screen, UI_MOCHA, (WIDTH//2 - 150, rules_rect.y + 70), (WIDTH//2 + 150, rules_rect.y + 70), 3)

            # Print the simple bullet points on screen
            start_y = rules_rect.y + 115
            for i, text in enumerate(rules_ui):
                draw_text(self.screen, text, 28, (60, 50, 50), WIDTH//2, start_y + (i * 45))

            # 🎨 BUTTON VISUAL LOCK
            if busy:
                btn_repeat.text = "Wait..."
                btn_repeat.color = (130, 130, 130)
                btn_repeat.hover_color = (130, 130, 130)
                
                btn_continue.text = "Wait..."
                btn_continue.color = (130, 130, 130)
                btn_continue.hover_color = (130, 130, 130)
                
                draw_text(self.screen, "Please listen to Alpha Mini...", 18, (255, 100, 100), WIDTH//2, HEIGHT - 25)
            else:
                btn_repeat.text = "NO"
                btn_repeat.color = (220, 150, 40)
                btn_repeat.hover_color = (255, 180, 80)
                btn_repeat.check_hover((mx, my))
                
                btn_continue.text = "YES"
                btn_continue.color = GREEN
                btn_continue.hover_color = (100, 255, 100)
                btn_continue.check_hover((mx, my))
                
                draw_text(self.screen, "Are you ready to begin?", 18, WHITE, WIDTH//2, HEIGHT - 25)

            btn_repeat.draw(self.screen)
            btn_continue.draw(self.screen)
            
            if not busy:
                if btn_continue.is_clicked((mx, my), click):
                    return "TUTORIAL" 
                elif btn_repeat.is_clicked((mx, my), click):
                    self.queue_rules_speech()
                    frames_passed = 0

            pygame.display.flip()