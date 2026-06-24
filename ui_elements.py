import pygame
from config import *

class Button:
    def __init__(self, x, y, width, height, text, base_color, hover_color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.SysFont("Arial", 28, bold=True)
        self.current_color = base_color

    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.base_color

    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

def draw_text(screen, text, size, color, x, y, center=True):
    font = pygame.font.SysFont("Arial", size, bold=True)
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)

# --- UPDATED TASK LIST CLASS ---
class TaskList:
    def __init__(self, tasks):
        self.tasks = {task: False for task in tasks} 
        self.visible = False 
        
        # Icon Button (Top Right Corner)
        self.icon_rect = pygame.Rect(WIDTH - 60, 10, 50, 50)
        
        # --- FIX 1: TALLER BOX ---
        # Changed base height from 30 to 60 to give the header more room
        # Changed per-item height to 35 so lines aren't squashed
        self.list_bg_rect = pygame.Rect(WIDTH - 220, 70, 200, 60 + (len(tasks) * 35))

    def toggle(self):
        self.visible = not self.visible

    def mark_found(self, food_name):
        if food_name in self.tasks:
            self.tasks[food_name] = True

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.icon_rect.collidepoint(event.pos):
                    self.toggle()

    def draw(self, screen):
        # 1. Draw the Icon
        mouse_pos = pygame.mouse.get_pos()
        color = (200, 200, 100) if self.icon_rect.collidepoint(mouse_pos) else (150, 150, 50)
        pygame.draw.rect(screen, color, self.icon_rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.icon_rect, 2, border_radius=5)
        
        # Icon Lines
        pygame.draw.line(screen, BLACK, (WIDTH-50, 25), (WIDTH-20, 25), 3)
        pygame.draw.line(screen, BLACK, (WIDTH-50, 35), (WIDTH-20, 35), 3)
        pygame.draw.line(screen, BLACK, (WIDTH-50, 45), (WIDTH-20, 45), 3)
        
        # 2. Draw the List
        if self.visible:
            # --- FIX 2: SOLID BACKGROUND (easier to read) ---
            pygame.draw.rect(screen, WHITE, self.list_bg_rect, border_radius=5)
            pygame.draw.rect(screen, BLACK, self.list_bg_rect, 3, border_radius=5)
            
            # Header
            draw_text(screen, "TASK LIST", 22, BLACK, self.list_bg_rect.centerx, self.list_bg_rect.y + 20)
            
            # Divider Line
            line_y = self.list_bg_rect.y + 40
            pygame.draw.line(screen, BLACK, (self.list_bg_rect.x + 10, line_y), (self.list_bg_rect.right - 10, line_y), 2)
            
            # Draw items
            y_offset = 55
            for food, is_done in self.tasks.items():
                if is_done:
                    label = f"[x] {food}"
                    col = (0, 180, 0) # Darker Green
                else:
                    label = f"[ ] {food}"
                    col = BLACK # Pure Black for visibility
                
                # --- FIX 3: TEXT ALIGNMENT ---
                draw_text(screen, label, 20, col, self.list_bg_rect.x + 20, self.list_bg_rect.y + y_offset, center=False)
                y_offset += 35