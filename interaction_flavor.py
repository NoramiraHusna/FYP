# interaction_flavor.py
import pygame
from config import *
from ui_elements import draw_text
from interaction_data import *

# 🔌 Grab the physical robot connection to check its status
from robot_interface import alpha_mini_hardware

class FlavorSelector:
    def __init__(self, screen, clock, helper):
        self.screen = screen
        self.clock = clock
        self.helper = helper 

    def run(self, food_name): 
        box_w, box_h = 280, 150 
        
        GAP = 25  
        CONTENT_WIDTH = (box_w * 2) + GAP 
        CONTENT_HEIGHT = (box_h * 2) + GAP
        POPUP_WIDTH = CONTENT_WIDTH + 60
        POPUP_HEIGHT = CONTENT_HEIGHT + 180
        
        menu_rect = pygame.Rect(WIDTH // 2 - (POPUP_WIDTH // 2), HEIGHT // 2 - (POPUP_HEIGHT // 2), POPUP_WIDTH, POPUP_HEIGHT)
        
        flavor_images = []
        is_cake = (food_name == "Cake" or (TUTORIAL_FOODS and food_name == TUTORIAL_FOODS[0]))
        
        if is_cake:
            options = ["Vanilla", "Matcha", "Chocolate", "Strawberry"]
            title_text = "SELECT A FLAVOR"
            colors = CAKE_BG_COLORS
            files = ["Cake_vanilla.png", "Cake_matcha.png", "Cake_chocolate.png", "Cake_strawberry.png"]
        else:
            options = FOOD_OPTIONS.get(food_name, [])
            title_text = f"CHOOSE YOUR {food_name.upper()}"
            colors = FOOD_PALETTE
            files = FOOD_IMAGE_MAP.get(food_name, [])

        for fname in files:
            img = self.helper.load_smart_image(fname, (box_w - 20, box_h - 20))
            flavor_images.append(img)
            
        while len(flavor_images) < 4: flavor_images.append(None)

        start_x = menu_rect.centerx - (CONTENT_WIDTH // 2)
        start_y = menu_rect.centery - (CONTENT_HEIGHT // 2) + 40

        r_list = [
            pygame.Rect(start_x, start_y, box_w, box_h), 
            pygame.Rect(start_x + box_w + GAP, start_y, box_w, box_h),
            pygame.Rect(start_x, start_y + box_h + GAP, box_w, box_h),         
            pygame.Rect(start_x + box_w + GAP, start_y + box_h + GAP, box_w, box_h)
        ]

        selection = None
        running = True
        while running:
            # 🛡️ THE BRAIN LOCK: Check if robot is talking or has lines queued
            queue_has_items = len(alpha_mini_hardware.speech_queue) > 0 if isinstance(alpha_mini_hardware.speech_queue, list) else not alpha_mini_hardware.speech_queue.empty()
            robot_busy = getattr(alpha_mini_hardware, 'is_speaking', False) or queue_has_items

            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0,0))
            
            self.helper.draw_styled_popup(menu_rect, UI_CREAM, UI_MOCHA)
            draw_text(self.screen, title_text, 35, UI_MOCHA, menu_rect.centerx, menu_rect.top + 40) 
            pygame.draw.line(self.screen, UI_MOCHA, (menu_rect.centerx - 150, menu_rect.top + 75), (menu_rect.centerx + 150, menu_rect.top + 75), 3)

            mx, my = pygame.mouse.get_pos()

            def draw_hover_btn(rect, base_color, name, img=None, text_color=(0,0,0)):
                # 🎨 VISUAL LOCK: Gray out if robot is busy
                if robot_busy:
                    draw_color = (130, 130, 130)
                    border_color = (100, 100, 100)
                    border_width = 3
                    is_hovered = False
                else:
                    is_hovered = rect.collidepoint((mx, my))
                    if is_hovered:
                        border_color = (255, 255, 100)
                        border_width = 4
                        bg_r = min(255, base_color[0] + 20)
                        bg_g = min(255, base_color[1] + 20)
                        bg_b = min(255, base_color[2] + 20)
                        draw_color = (bg_r, bg_g, bg_b)
                    else:
                        border_color = UI_MOCHA
                        border_width = 3
                        draw_color = base_color

                pygame.draw.rect(self.screen, draw_color, rect, border_radius=12)
                pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=12)
                
                cx, cy = rect.centerx, rect.centery
                
                if img:
                    img_to_draw = img.copy()
                    if robot_busy:
                        img_to_draw.set_alpha(100) # Fade image when locked
                    
                    mask = pygame.mask.from_surface(img_to_draw)
                    shadow_surf = mask.to_surface(setcolor=(0,0,0,80), unsetcolor=(0,0,0,0))
                    self.screen.blit(shadow_surf, (cx - img_to_draw.get_width()//2 + 4, cy - img_to_draw.get_height()//2 - 4))
                    self.screen.blit(img_to_draw, (cx - img_to_draw.get_width()//2, cy - img_to_draw.get_height()//2 - 8))
                    
                    label_bg = pygame.Surface((rect.width - 10, 25), pygame.SRCALPHA)
                    label_bg.fill((0, 0, 0, 100)) 
                    self.screen.blit(label_bg, (rect.x + 5, rect.bottom - 30))
                    
                    display_name = name.replace(food_name, "").strip() if len(name) > 12 else name
                    if display_name == "": display_name = name
                    
                    label_color = (180, 180, 180) if robot_busy else WHITE
                    draw_text(self.screen, display_name, 17, label_color, cx, rect.bottom - 15)
                else:
                    label_color = (180, 180, 180) if robot_busy else text_color
                    draw_text(self.screen, name, 20, label_color, cx, cy) 

            for i, (rect, name) in enumerate(zip(r_list, options)):
                current_img = flavor_images[i]
                base_color = colors[i % len(colors)]
                text_color = UI_MOCHA 
                if base_color == (140, 100, 80): text_color = WHITE 

                draw_hover_btn(rect, base_color, name, img=current_img, text_color=text_color)

            # ⏳ Show warning text if locked
            if robot_busy:
                draw_text(self.screen, "Please listen to Alpha Mini's introduction...", 18, (200, 50, 50), menu_rect.centerx, menu_rect.bottom - 40)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.display.toggle_fullscreen()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # 🚫 Only allow selection if the robot is done
                    if event.button == 1 and not robot_busy: 
                        for i, rect in enumerate(r_list):
                            if rect.collidepoint((mx, my)):
                                selection = options[i]
                                running = False
                                break
            
            pygame.display.flip()
            self.clock.tick(60)
            
        return selection