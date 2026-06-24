import pygame
import os
import math
from config import *
from ui_elements import Button, draw_text

class CharSelectMenu:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock

    def run(self):
        # --- BUTTONS ---
        btn_male = Button(
            (WIDTH // 4) - 70, HEIGHT // 2 + 100,
            140, 60,
            "MALE", 
            (65, 105, 225), # Royal Blue
            (100, 149, 237) # Cornflower Blue (Hover)
        )
        
        btn_female = Button(
            (3 * WIDTH // 4) - 70, HEIGHT // 2 + 100, 
            140, 60, 
            "FEMALE", 
            (255, 99, 71),  # Tomato Red
            (255, 160, 122) # Light Salmon (Hover)
        )
        
        # Load and Scale Sprites
        FRAME_SIZE = 32 
        SCALE_FACTOR = 6 
        try:
            sheet_male = pygame.image.load(os.path.join(ASSET_DIR, 'Male_Player.png')).convert_alpha()
            frame_male = sheet_male.subsurface(pygame.Rect(0, 0, FRAME_SIZE, FRAME_SIZE))
            big_male = pygame.transform.scale(frame_male, (FRAME_SIZE * SCALE_FACTOR, FRAME_SIZE * SCALE_FACTOR))

            sheet_female = pygame.image.load(os.path.join(ASSET_DIR, 'Female_Player.png')).convert_alpha()
            frame_female = sheet_female.subsurface(pygame.Rect(0, 0, FRAME_SIZE, FRAME_SIZE))
            big_female = pygame.transform.scale(frame_female, (FRAME_SIZE * SCALE_FACTOR, FRAME_SIZE * SCALE_FACTOR))
        except Exception:
            big_male = None
            big_female = None

        # --- HELPER: Draw Text with White Outline ---
        def draw_outlined_text(text, size, x, y):
            # Draw the outline (White) by drawing 8 surrounding copies
            offsets = [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2), (-2, 2), (2, -2)]
            for dx, dy in offsets:
                draw_text(self.screen, text, size, (255, 255, 255), x + dx, y + dy)
            
            # Draw the main text (Black) on top
            draw_text(self.screen, text, size, (0, 0, 0), x, y)

        running = True
        while running:
            mx, my = pygame.mouse.get_pos()
            time_now = pygame.time.get_ticks()
            
            # Pulse varies from -20 to +20 smoothly
            pulse = math.sin(time_now * 0.004) * 20 

            # --- COLOR LOGIC ---
            if mx < WIDTH // 2:
                # === MALE SIDE ACTIVE (Baby Blue Pulse) ===
                # Base Baby Blue is approx (137, 207, 240)
                # We oscillate G/B to make it glow
                r = 137
                g = min(255, max(150, 207 + pulse)) 
                b = min(255, max(200, 240 + pulse)) 
                bg_male = (r, g, b)
                circle_male = (255, 255, 255) # Bright
                
                # Female Side (Dimmed)
                bg_female = (100, 80, 80) 
                circle_female = (120, 100, 100)
                
            else:
                # === FEMALE SIDE ACTIVE (Baby Red Pulse) ===
                # To get "Baby Red" (Pastel Red), we need High Red, 
                # but lower Blue/Green than Pink.
                # Target: (255, ~120, ~120)
                r = 255
                g = min(255, max(80, 120 + pulse)) # Oscillates around 100-140
                b = min(255, max(80, 120 + pulse)) # Oscillates around 100-140
                bg_female = (r, g, b)
                circle_female = (255, 255, 255) # Bright

                # Male Side (Dimmed)
                bg_male = (60, 70, 90)
                circle_male = (80, 90, 110)

            # Draw Split Background
            pygame.draw.rect(self.screen, bg_male, (0, 0, WIDTH//2, HEIGHT))
            pygame.draw.rect(self.screen, bg_female, (WIDTH//2, 0, WIDTH//2, HEIGHT))
            
            # Divider Line
            pygame.draw.line(self.screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 6)

            # Draw Circles
            pygame.draw.circle(self.screen, circle_male, (WIDTH//4, HEIGHT//2 - 10), 110)
            pygame.draw.circle(self.screen, circle_female, (3*WIDTH//4, HEIGHT//2 - 10), 110)

            # --- HEADER (With White Border) ---
            # Updated Text to "CHOOSE YOUR AVATAR'S GENDER"
            draw_outlined_text("CHOOSE YOUR AVATAR'S GENDER", 45, WIDTH//2, 80)
            
            click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "EXIT", None
                if event.type == pygame.MOUSEBUTTONDOWN: click = True

            # Draw Characters
            if big_male:
                m_rect = big_male.get_rect(center=(WIDTH//4, HEIGHT//2 - 10)) 
                self.screen.blit(big_male, m_rect)
            if big_female:
                f_rect = big_female.get_rect(center=(3*WIDTH//4, HEIGHT//2 - 10))
                self.screen.blit(big_female, f_rect)

            # Draw Buttons
            btn_male.check_hover((mx, my))
            btn_female.check_hover((mx, my))
            btn_male.draw(self.screen)
            btn_female.draw(self.screen)
            
            if btn_male.is_clicked((mx, my), click):
                return "RULES", "Male"
            elif btn_female.is_clicked((mx, my), click):
                return "RULES", "Female"
                
            pygame.display.flip()
            self.clock.tick(FPS)