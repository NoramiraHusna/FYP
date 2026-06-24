import pygame
import os
import math
from config import *
from ui_elements import Button, draw_text
from interaction_data import UI_CREAM, UI_MOCHA, UI_SHADOW 

# 🔌 Grab the physical robot connection
from robot_interface import alpha_mini_hardware

class NameInputMenu:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.player_name = ""
        
        # Load the main menu background
        self.bg_image = self._load_background('menu_background.png')
        
        # Load the demonstration session image
        try:
            img = pygame.image.load(os.path.join(ASSET_DIR, 'demo_sess.png')).convert()
            self.concept_image = pygame.transform.scale(img, (WIDTH, HEIGHT - 100))
        except Exception as e:
            print(f"Warning: Demo session image not found. {e}")
            self.concept_image = None

    def _load_background(self, filename):
        bg_path = os.path.join(ASSET_DIR, filename)
        try:
            img = pygame.image.load(bg_path).convert()
            return pygame.transform.scale(img, (WIDTH, HEIGHT))
        except Exception:
            return None

    def queue_concept_sequence(self):
        """🗣️ Break the demonstration session down to match the 4 panels!"""
        alpha_mini_hardware.speak("SYSTEM", "Hello, Traveler! Welcome to the demonstration session of the game.")
        alpha_mini_hardware.speak("SYSTEM", "In this demonstration session, you will explore human food with me. I am robot companion, Alpha Mini.")
        alpha_mini_hardware.speak("SYSTEM", "For each task, you will make an initial decision from the food choice.")
        alpha_mini_hardware.speak("SYSTEM", "I will analyse your initial decision and offer some insight.")
        alpha_mini_hardware.speak("SYSTEM", "After considering the insight, you will make your final decision.")
        alpha_mini_hardware.speak("SYSTEM", "If you understand the game concept, click the 'Yes' button, and 'No' to repeat the game concept.")

    def queue_name_speech(self):
        """🗣️ Prompt for the name input phase."""
        alpha_mini_hardware.speak("SYSTEM", "To start, please type your name.")

    def run(self):
        phase = "CONCEPT"
        self.player_name = ""
        
        btn_w = 150
        btn_h = 45
        gap = 30
        start_x = (WIDTH // 2) - ((btn_w * 2 + gap) // 2)
        
        btn_no = Button(start_x, HEIGHT - 65, btn_w, btn_h, "NO", (220, 150, 40), (255, 180, 80))
        btn_yes = Button(start_x + btn_w + gap, HEIGHT - 65, btn_w, btn_h, "YES", GREEN, (100, 255, 100))
        
        self.queue_concept_sequence()
        frames_passed = 0
        
        running = True
        while running:
            frames_passed += 1
            self.clock.tick(60)
            
            # 🛡️ THE BRAIN LOCK & SPEECH TRACKER
            queue_len = len(alpha_mini_hardware.speech_queue) if isinstance(alpha_mini_hardware.speech_queue, list) else alpha_mini_hardware.speech_queue.qsize()
            is_speaking = getattr(alpha_mini_hardware, 'is_speaking', False)
            
            busy = is_speaking or queue_len > 0 or frames_passed < 10 
            items_remaining = queue_len + (1 if is_speaking else 0)

            # --- EVENT HANDLING ---
            mx, my = pygame.mouse.get_pos()
            click = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return ("EXIT", None)
                    
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.display.toggle_fullscreen()
                    
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not busy: click = True

                if phase == "NAME" and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if len(self.player_name.strip()) > 0:
                            return ("RULES", self.player_name.strip())
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.key != pygame.K_ESCAPE:
                        if len(self.player_name) < 15:
                            self.player_name += event.unicode

            # ==========================================
            # PHASE 1: GAME CONCEPT VISUALS
            # ==========================================
            if phase == "CONCEPT":
                self.screen.fill(BLACK)
                
                if self.concept_image:
                    self.screen.blit(self.concept_image, (0, 0))
                else:
                    draw_text(self.screen, "DEMO SESSION IMAGE MISSING", 40, WHITE, WIDTH//2, (HEIGHT-100)//2)

                if is_speaking:
                    panel_idx = -1
                    if items_remaining == 5: panel_idx = 0     
                    elif items_remaining == 4: panel_idx = 1   
                    elif items_remaining == 3: panel_idx = 2   
                    elif items_remaining == 2: panel_idx = 3   

                    if panel_idx != -1:
                        panel_w = WIDTH // 4
                        y_pos = (HEIGHT - 100) // 4 
                        
                        coords_1x4 = [
                            (int(panel_w * 0.5), y_pos),
                            (int(panel_w * 1.5), y_pos),
                            (int(panel_w * 2.5), y_pos),
                            (int(panel_w * 3.5), y_pos)
                        ]
                        
                        target_x, target_y = coords_1x4[panel_idx] 
                        bounce = math.sin(pygame.time.get_ticks() * 0.01) * 10
                        ay = target_y + bounce
                        
                        pygame.draw.line(self.screen, (255, 230, 50), (target_x, ay - 60), (target_x, ay), 10)
                        pygame.draw.polygon(self.screen, (255, 230, 50), [
                            (target_x, ay), 
                            (target_x - 18, ay - 20), 
                            (target_x + 18, ay - 20)
                        ])
                        
                        for dx, dy in [(-1,-1),(1,-1),(-1,1),(1,1)]:
                            draw_text(self.screen, "LOOK HERE!", 24, BLACK, target_x + dx, ay - 80 + dy)
                        draw_text(self.screen, "LOOK HERE!", 24, WHITE, target_x, ay - 80)

                if busy:
                    btn_no.text = "Wait..."
                    btn_no.color = (130, 130, 130)
                    btn_no.hover_color = (130, 130, 130)
                    
                    btn_yes.text = "Wait..."
                    btn_yes.color = (130, 130, 130)
                    btn_yes.hover_color = (130, 130, 130)
                    draw_text(self.screen, "Listen to Alpha Mini...", 18, (255, 100, 100), WIDTH // 2, HEIGHT - 85)
                else:
                    btn_no.text = "NO"
                    btn_no.color = (220, 150, 40)
                    btn_no.hover_color = (255, 180, 80)
                    btn_no.check_hover((mx, my))
                    
                    btn_yes.text = "YES"
                    btn_yes.color = GREEN
                    btn_yes.hover_color = (100, 255, 100)
                    btn_yes.check_hover((mx, my))
                    draw_text(self.screen, "Do you understand the game concept?", 18, (200, 200, 200), WIDTH // 2, HEIGHT - 85)
                
                btn_no.draw(self.screen)
                btn_yes.draw(self.screen)

                if not busy:
                    if btn_yes.is_clicked((mx, my), click):
                        phase = "NAME"
                        self.queue_name_speech()
                        frames_passed = 0
                    elif btn_no.is_clicked((mx, my), click):
                        self.queue_concept_sequence()
                        frames_passed = 0

            # ==========================================
            # PHASE 2: NAME INPUT
            # ==========================================
            elif phase == "NAME":
                if self.bg_image:
                    self.screen.blit(self.bg_image, (0, 0))
                else:
                    self.screen.fill(BLACK)
                
                # 🎨 RESTORED AESTHETIC: Shadow, Cream Background, Mocha Borders
                box_w, box_h = 500, 240
                box_rect = pygame.Rect(WIDTH//2 - box_w//2, HEIGHT//2 - box_h//2, box_w, box_h)
                
                shadow_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
                pygame.draw.rect(shadow_surf, UI_SHADOW, shadow_surf.get_rect(), border_radius=15)
                self.screen.blit(shadow_surf, (box_rect.x + 8, box_rect.y + 8))
                
                pygame.draw.rect(self.screen, UI_CREAM, box_rect, border_radius=15)
                pygame.draw.rect(self.screen, UI_MOCHA, box_rect, 4, border_radius=15)

                draw_text(self.screen, "TRAVELER REGISTRATION", 32, UI_MOCHA, WIDTH//2, HEIGHT//2 - 70)
                pygame.draw.line(self.screen, UI_MOCHA, (WIDTH//2 - 150, HEIGHT//2 - 45), (WIDTH//2 + 150, HEIGHT//2 - 45), 3)
                
                if busy:
                    draw_text(self.screen, "Please wait for Alpha Mini...", 20, (200, 50, 50), WIDTH//2, HEIGHT//2 - 15)
                else:
                    draw_text(self.screen, "Enter your name to start:", 20, (60, 50, 50), WIDTH//2, HEIGHT//2 - 15)

                input_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 20, 300, 50)
                
                if busy:
                    pygame.draw.rect(self.screen, (200, 200, 200), input_rect)
                else:
                    pygame.draw.rect(self.screen, WHITE, input_rect)
                    
                pygame.draw.rect(self.screen, UI_MOCHA, input_rect, 2)

                draw_text(self.screen, self.player_name, 35, BLACK, WIDTH//2, HEIGHT//2 + 45)

                if not busy:
                    draw_text(self.screen, "[ENTER] to Confirm   [BACKSPACE] to Delete", 16, UI_MOCHA, WIDTH//2, HEIGHT//2 + 90)

            pygame.display.flip()