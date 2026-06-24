import pygame
import os
from config import *
from ui_elements import Button, draw_text

# --- SPACESHIP THEME COLORS ---
SPACE_DARK    = (20, 20, 40)        
HOLO_PANEL    = (0, 0, 0, 180)      
TEXT_BRIGHT   = (220, 240, 255)     
TEXT_HIGHLIGHT= (255, 255, 0)       
NEON_GREEN    = (50, 255, 50)
NEON_RED      = (255, 50, 80)

RATING_COLORS = {
    1: (255, 60, 60),   
    2: (255, 140, 60),  
    3: (255, 220, 0),   
    4: (170, 255, 50),  
    5: (0, 255, 100)    
}

class QuestionnaireMenu:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.bg_image = self._load_background()
        self.answers = [0] * 24 
        self.current_page = 0
        
        self.pages = [
            {
                "title": "MISSION DEBRIEF: INTERFACE",
                "questions": [
                    "1. The pictures of the food on the map were clear and easy to see.",
                    "2. I understood how to play the game without needing extra help.",
                    "3. The text and instructions on the screen were easy to read.",
                    "4. The buttons worked immediately when I pressed them.",
                    "5. The robot reacted at the right time when the game screen changed.",
                    "6. I could clearly tell when I had successfully selected an item.",
                    "7. The game looked nice and was not confusing to look at.",
                    "8. The screen design helped me focus on making my choices."
                ]
            },
            {
                "title": "MISSION DEBRIEF: GAMEPLAY",
                "questions": [
                    "1. I found the story about helping aliens find food interesting.",
                    "2. I felt happy with the choices I made.",
                    "3. I liked how the game world and the food pictures looked.",
                    "4. I forgot about things around me while I was playing.",
                    "5. Having the robot give me advice makes the game more fun.",
                    "6. I paid full attention to the game the whole time.",
                    "7. I felt satisfied when I finished picking the list of food.",
                    "8. I enjoyed playing this game."
                ]
            },
            {
                "title": "MISSION DEBRIEF: FINAL THOUGHTS",
                "questions": [
                    "1. I felt relaxed after playing the game.",
                    "2. I felt like I was really helping the alien character.",
                    "3. I felt confident that I made the right food choices.",
                    "4. I felt like the robot, and I made a good team.",
                    "5. I felt satisfied with the final list of food I chose.",
                    "6. I felt happy interacting with the robot.",
                    "7. I felt proud that I completed the mission.",
                    "8. I would like to play this game with the robot again."
                ]
            }
        ]

        self.btn_next = Button(WIDTH - 160, HEIGHT - 70, 140, 50, "NEXT >", NEON_GREEN, (100, 255, 100), text_color=BLACK)
        self.btn_back = Button(20, HEIGHT - 70, 140, 50, "< BACK", (200, 200, 200), (255, 255, 255), text_color=BLACK)
        self.btn_submit = Button(WIDTH - 160, HEIGHT - 70, 140, 50, "SUBMIT", (0, 255, 255), (150, 255, 255), text_color=BLACK)

    def _load_background(self):
        bg_path = os.path.join(ASSET_DIR, 'survey_bg.png')
        try:
            img = pygame.image.load(bg_path).convert()
            return pygame.transform.scale(img, (WIDTH, HEIGHT))
        except:
            return None

    def run(self):
        self.current_page = 0
        self.answers = [0] * 24 
        font_q = pygame.font.SysFont("Arial", 19) 
        font_bold = pygame.font.SysFont("Arial", 22, bold=True)
        
        running = True
        while running:
            if self.bg_image:
                self.screen.blit(self.bg_image, (0,0))
            else:
                self.screen.fill(SPACE_DARK) 

            panel_rect = pygame.Rect(40, 40, WIDTH - 80, HEIGHT - 120)
            panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
            panel_surf.fill(HOLO_PANEL) 
            pygame.draw.rect(panel_surf, (100, 200, 255), panel_surf.get_rect(), 3)
            self.screen.blit(panel_surf, panel_rect.topleft)

            page_data = self.pages[self.current_page]

            draw_text(self.screen, page_data["title"], 40, TEXT_HIGHLIGHT, WIDTH//2, 60)
            
            start_y = 120
            scale_spacing = 40
            scale_right_margin = 80
            scale_start_x = WIDTH - scale_right_margin - (4 * scale_spacing) - 40 

            label_no = font_bold.render("NO (1)", True, NEON_RED)
            label_yes = font_bold.render("YES (5)", True, NEON_GREEN)
            
            self.screen.blit(label_no, (scale_start_x - 10, start_y - 25))
            self.screen.blit(label_yes, (scale_start_x + (4 * scale_spacing) - 10, start_y - 25))

            mx, my = pygame.mouse.get_pos()
            click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "EXIT"
                
                # --- NEW: Toggle Full Screen with ESC ---
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.display.toggle_fullscreen()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: click = True

            for idx, question in enumerate(page_data["questions"]):
                row_y = start_y + 15 + (idx * 48) 
                text_surf = font_q.render(question, True, TEXT_BRIGHT)
                self.screen.blit(text_surf, (60, row_y))
                
                global_q_index = (self.current_page * 8) + idx
                current_val = self.answers[global_q_index]

                for score in range(1, 6):
                    bx = scale_start_x + (score - 1) * scale_spacing + 15
                    by = row_y + 10 
                    
                    dist = ((mx - bx)**2 + (my - by)**2)**0.5
                    is_hover = dist < 12
                    
                    if click and is_hover:
                        self.answers[global_q_index] = score
                    
                    color = RATING_COLORS[score]
                    
                    if current_val == score:
                        pygame.draw.circle(self.screen, color, (bx, by), 13)
                        pygame.draw.circle(self.screen, (255, 255, 255), (bx, by), 13, 2)
                    elif is_hover:
                        pygame.draw.circle(self.screen, color, (bx, by), 11)
                    else:
                        pygame.draw.circle(self.screen, (100, 100, 100), (bx, by), 9) 
                        pygame.draw.circle(self.screen, color, (bx, by), 9, 2) 

            if self.current_page > 0:
                self.btn_back.check_hover((mx, my))
                self.btn_back.draw(self.screen)
                if self.btn_back.is_clicked((mx, my), click):
                    self.current_page -= 1

            if self.current_page < 2:
                self.btn_next.check_hover((mx, my))
                self.btn_next.draw(self.screen)
                if self.btn_next.is_clicked((mx, my), click):
                    self.current_page += 1
            else:
                self.btn_submit.check_hover((mx, my))
                self.btn_submit.draw(self.screen)
                if self.btn_submit.is_clicked((mx, my), click):
                    return self.answers 

            page_text = f"PAGE {self.current_page + 1} / 3"
            draw_text(self.screen, page_text, 18, (150, 200, 255), WIDTH//2, HEIGHT - 40)

            pygame.display.flip()
            self.clock.tick(FPS)