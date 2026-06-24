# interaction_robot.py
import pygame
import math
from config import *
from ui_elements import draw_text
from interaction_data import *

# 🔌 Grab the live connection to the physical robot!
from robot_interface import alpha_mini_hardware

class RobotIntervention:
    def __init__(self, screen, clock, helper):
        self.screen = screen
        self.clock = clock
        self.helper = helper

    def run(self, food_name, options, original_choice, tone, custom_lines, speaker_name="ROBOT", simple_mode=False):
        suggestion = ""
        if not simple_mode and options:
            try:
                original_index = options.index(original_choice)
                suggestion = options[(original_index + 1) % len(options)]
            except ValueError:
                suggestion = options[0]

        if custom_lines:
            lines = [line.format(food_name=food_name, suggestion=suggestion) for line in custom_lines]
        else:
            lines = ["Wait a moment.", f"Consider trying {suggestion}.", "It might be better."]

        img_original = None
        img_suggestion = None
        
        if not simple_mode:
            img_original = self.helper.get_image_for_choice(food_name, original_choice)
            img_suggestion = self.helper.get_image_for_choice(food_name, suggestion)

        BUTTON_WIDTH = 250
        BUTTON_HEIGHT = 70
        rect_continue = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 90, 200, BUTTON_HEIGHT)
        rect_keep = pygame.Rect(WIDTH//2 - BUTTON_WIDTH - 10, HEIGHT//2 + 90, BUTTON_WIDTH, BUTTON_HEIGHT)
        rect_change = pygame.Rect(WIDTH//2 + 10, HEIGHT//2 + 90, BUTTON_WIDTH, BUTTON_HEIGHT)

        running = True
        while running:
            # 🛡️ THE BULLETPROOF LOCK FIX
            queue_has_items = len(alpha_mini_hardware.speech_queue) > 0 if isinstance(alpha_mini_hardware.speech_queue, list) else not alpha_mini_hardware.speech_queue.empty()
            robot_busy = getattr(alpha_mini_hardware, 'is_speaking', False) or queue_has_items

            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180) 
            overlay.fill(BLACK) 
            self.screen.blit(overlay, (0,0))
            
            # THE MAIN POPUP BOX
            msg_rect = pygame.Rect(WIDTH//2 - 280, HEIGHT//2 - 160, 560, 350)
            self.helper.draw_styled_popup(msg_rect, UI_CREAM, UI_MOCHA)
            
            header_text = "ALIEN VISITOR" if speaker_name == "ALIEN" else f"THE {food_name.upper()} SELLER SAYS"
            draw_text(self.screen, header_text, 32, UI_MOCHA, WIDTH//2, HEIGHT//2 - 115)
            pygame.draw.line(self.screen, UI_MOCHA, (WIDTH//2 - 180, HEIGHT//2 - 90), (WIDTH//2 + 180, HEIGHT//2 - 90), 3)
            
            start_y = HEIGHT//2 - 50
            for i, line in enumerate(lines):
                draw_text(self.screen, line, 24, (50, 40, 40), WIDTH//2, start_y + (i * 35))

            mx, my = pygame.mouse.get_pos()
            click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return original_choice, False
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.display.toggle_fullscreen()
                    
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    # 🚫 ONLY register the click if the physical robot is completely finished!
                    if not robot_busy:
                        click = True
            
            pulse_val = (math.sin(pygame.time.get_ticks() * 0.008) + 1) / 2 
            
            def draw_robo_btn(rect, text, base_color, hover_color, img=None, is_highlighted=False):
                if robot_busy:
                    color = (130, 130, 130) # Disabled Gray
                    border_c = (100, 100, 100)
                    is_hovered = False
                    thickness = 2
                else:
                    is_hovered = rect.collidepoint((mx, my))
                    color = hover_color if is_hovered else base_color
                    border_c = (255, 255, int(150 * pulse_val)) if is_highlighted else UI_MOCHA 
                    thickness = 4 if is_highlighted else 2
                
                pygame.draw.rect(self.screen, color, rect, border_radius=12)
                pygame.draw.rect(self.screen, border_c, rect, thickness, border_radius=12)
                
                cx, cy = rect.centerx, rect.centery
                if img:
                    img_to_draw = img.copy()
                    if robot_busy:
                        img_to_draw.set_alpha(128) 
                    else:
                        img_to_draw.set_alpha(255)

                    mask = pygame.mask.from_surface(img_to_draw)
                    shadow_surf = mask.to_surface(setcolor=(0,0,0,80), unsetcolor=(0,0,0,0))
                    self.screen.blit(shadow_surf, (cx - img_to_draw.get_width()//2 + 3, rect.y + 8))
                    self.screen.blit(img_to_draw, (cx - img_to_draw.get_width()//2, rect.y + 5))
                    
                    label_bg = pygame.Surface((rect.width - 10, 25), pygame.SRCALPHA)
                    label_bg.fill((0, 0, 0, 100))
                    self.screen.blit(label_bg, (rect.x + 5, rect.bottom - 30))
                    
                    text_color = (200, 200, 200) if robot_busy else WHITE
                    draw_text(self.screen, text, 17, text_color, cx, rect.bottom - 15)
                else:
                    text_color = (200, 200, 200) if robot_busy else WHITE
                    draw_text(self.screen, text, 20, text_color, cx, cy)
                
                return is_hovered and click

            if simple_mode:
                if draw_robo_btn(rect_continue, "CONTINUE", GREEN, (150, 255, 150)): return None, False
            else:
                orig_short = original_choice.split()[-1]
                sugg_short = suggestion.split()[-1]
                if draw_robo_btn(rect_keep, f"KEEP {orig_short.upper()}", (150, 255, 150), (180, 180, 180), img_original): return original_choice, False
                if draw_robo_btn(rect_change, f"TRY {sugg_short.upper()}", (150, 255, 150), (180, 180, 180), img_suggestion): return suggestion, True

            # 🚨 NEW: BIG, HIGH-CONTRAST TOP NOTIFICATION BANNER
            if robot_busy:
                warn_w = 550
                warn_rect = pygame.Rect(WIDTH//2 - warn_w//2, 30, warn_w, 60)
                
                # Banner shadow
                shadow_surf = pygame.Surface((warn_w, warn_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(shadow_surf, (0, 0, 0, 150), shadow_surf.get_rect(), border_radius=15)
                self.screen.blit(shadow_surf, (warn_rect.x + 5, warn_rect.y + 5))
                
                # Banner background & border
                pygame.draw.rect(self.screen, (40, 40, 40), warn_rect, border_radius=15)
                pygame.draw.rect(self.screen, (255, 100, 100), warn_rect, 3, border_radius=15)
                
                # Big bold text
                draw_text(self.screen, "PLEASE LISTEN TO ALPHA MINI...", 26, (255, 120, 120), WIDTH//2, warn_rect.centery)

            pygame.display.flip()
            self.clock.tick(60)