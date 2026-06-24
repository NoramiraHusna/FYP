import pygame
import os
import math # Required for the bouncing title animation
from config import *
from ui_elements import Button, draw_text

class MainMenu:
    def __init__(self, screen, clock, menu_bg):
        self.screen = screen
        self.clock = clock
        self.menu_bg = menu_bg 

        self.typing_mode = False
        self.password_input = ""
        self.feedback_msg = ""

    class ResetButton(Button):
        def __init__(self, x, y, width, height, text, base_color, hover_color, text_color=WHITE):
            super().__init__(x, y, width, height, text, base_color, hover_color, text_color)
            self.font = pygame.font.SysFont("Arial", 25, bold=True)

    def run(self):
        btn_start = Button(WIDTH//2 - 120, HEIGHT//2 + 40, 240, 80, "START", GREEN, (100, 255, 100))
        
        RESET_BUTTON_WIDTH = 180
        btn_reset = self.ResetButton(
            WIDTH - RESET_BUTTON_WIDTH - 20, 
            HEIGHT - 70,                    
            RESET_BUTTON_WIDTH, 
            50, 
            "RESET DATA", 
            GRAY, 
            (150, 150, 150)
        )
        
        running = True
        while running:
            self.clock.tick(FPS)
            mx, my = pygame.mouse.get_pos()
            click = False
            
            # --- EVENT HANDLING ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "EXIT"
                    
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.typing_mode:
                        self.typing_mode = False
                        self.password_input = ""
                    else:
                        pygame.display.toggle_fullscreen()
                        
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click = True
                    
                # Password Typing Logic
                if self.typing_mode and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # You can change "1234" to whatever your admin password is
                        if self.password_input == "1234": 
                            return "RESET_DATA"
                        else:
                            self.feedback_msg = "Incorrect Password!"
                            self.typing_mode = False
                            self.password_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.password_input = self.password_input[:-1]
                    elif event.key != pygame.K_ESCAPE:
                        self.password_input += event.unicode

            # 1. Draw Background
            if self.menu_bg:
                self.screen.blit(self.menu_bg, (0, 0))
            else:
                self.screen.fill(BLACK)

            # ==========================================
            # 🎨 POPPING TITLE ANIMATION (STACKED)
            # ==========================================
            # Calculate a smooth bouncing effect
            bounce = math.sin(pygame.time.get_ticks() * 0.003) * 8
            title_x = WIDTH // 2
            title_size = 65
            
            # The two lines of text we want to stack
            title_lines = ["CLICK START","TO BEGIN THE","DEMONSTRATION!"]
            start_y = 140 + bounce
            
            for i, line_text in enumerate(title_lines):
                current_y = start_y + (i * 70) # Adds 70px of space between the words
                
                # A. Draw drop shadow (offset down and right)
                draw_text(self.screen, line_text, title_size, (50, 50, 50), title_x + 5, current_y + 5)
                
                # B. Draw thick white outline so the black text pops
                outline_offsets = [
                    (-3, -3), (0, -3), (3, -3),
                    (-3,  0),          (3,  0),
                    (-3,  3), (0,  3), (3,  3),
                    (-2, -2), (2, -2), (-2, 2), (2, 2)
                ]
                for dx, dy in outline_offsets:
                    draw_text(self.screen, line_text, title_size, WHITE, title_x + dx, current_y + dy)
                    
                # C. Draw main title text (BLACK)
                draw_text(self.screen, line_text, title_size, BLACK, title_x, current_y)
            # ==========================================

            # 2. Main Menu Mode
            if not self.typing_mode:
                btn_start.check_hover((mx, my))
                btn_reset.check_hover((mx, my))
                
                btn_start.draw(self.screen)
                btn_reset.draw(self.screen)
                
                if self.feedback_msg:
                    draw_text(self.screen, self.feedback_msg, 20, RED, WIDTH//2, HEIGHT//2 + 130)
                
                if btn_start.is_clicked((mx, my), click):
                    return "NAME_INPUT"
                    
                if btn_reset.is_clicked((mx, my), click):
                    self.typing_mode = True
                    self.password_input = ""
                    self.feedback_msg = ""
                    
            # 3. Security Check Overlay Mode
            else:
                btn_start.draw(self.screen)
                btn_reset.draw(self.screen)

                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(180)
                overlay.fill(BLACK)
                self.screen.blit(overlay, (0,0))

                box_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 220)
                pygame.draw.rect(self.screen, WHITE, box_rect, border_radius=15)
                pygame.draw.rect(self.screen, (50, 50, 50), box_rect, 4, border_radius=15)

                draw_text(self.screen, "SECURITY CHECK", 30, (50, 50, 50), WIDTH//2, HEIGHT//2 - 70)
                draw_text(self.screen, "Enter Admin Password:", 20, BLACK, WIDTH//2, HEIGHT//2 - 30)

                input_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 40)
                pygame.draw.rect(self.screen, (240, 240, 240), input_rect)
                pygame.draw.rect(self.screen, BLACK, input_rect, 2)

                masked_text = "*" * len(self.password_input)
                draw_text(self.screen, masked_text, 30, BLACK, WIDTH//2, HEIGHT//2 + 20)
                draw_text(self.screen, "Press ENTER to confirm or ESC to cancel", 16, GRAY, WIDTH//2, HEIGHT//2 + 80)

            pygame.display.flip()