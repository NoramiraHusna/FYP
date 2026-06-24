import pygame
import os
from config import *

# --- IMPORT NEW MENU MODULES ---
from menu_main import MainMenu
from menu_name import NameInputMenu
from menu_char import CharSelectMenu
from menu_story import StoryMenu         
from menu_summary import SummaryMenus
from menu_rules import RulesMenu 
from menu_questionnaire import QuestionnaireMenu 

class MenuManager:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.menu_bg = self._load_background()

        self.main_menu = MainMenu(screen, clock, self.menu_bg)
        self.name_menu = NameInputMenu(screen, clock)
        self.char_select = CharSelectMenu(screen, clock)
        self.story_menu = StoryMenu(screen, clock)       
        self.rules_menu = RulesMenu(screen, clock) 
        self.summary_menus = SummaryMenus(screen, clock)
        self.questionnaire = QuestionnaireMenu(screen, clock) 

    def _load_background(self):
        bg_path = os.path.join(ASSET_DIR, 'menu_background.png')
        try:
            loaded_image = pygame.image.load(bg_path).convert()
            return pygame.transform.scale(loaded_image, (WIDTH, HEIGHT))
        except Exception:
            return None

    # --- DELEGATED FUNCTIONS ---
    def run_main_menu(self): return self.main_menu.run()
    def run_name_input(self): return self.name_menu.run()
    def run_char_select(self): return self.char_select.run()
    def run_story(self): return self.story_menu.run()    
    def run_rules(self): return self.rules_menu.run()
    def run_tutorial_end(self, history_data): return self.summary_menus.run_tutorial_end(history_data)
    def run_game_summary(self, all_sessions): return self.summary_menus.run_game_summary(all_sessions)
    def run_questionnaire(self): return self.questionnaire.run()