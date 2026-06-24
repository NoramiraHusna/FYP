import pygame
import subprocess
import sys
import atexit
from config import WIDTH, HEIGHT
from game_logic import GameLogic
from intro_logic import IntroLogic 

# ==========================================
# 1. AUTO-LAUNCH THE OPENCV BRIDGE
# ==========================================
print("Starting Facial Detection Bridge...")
vision_process = subprocess.Popen([sys.executable, "blink_opencv.py"])

def cleanup_vision():
    print("Shutting down Facial Detection...")
    vision_process.terminate()

atexit.register(cleanup_vision)
# ==========================================

# 2. START THE GAME
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Foodie Adventure") 

# 3. SET UP GAME SYSTEMS
game = GameLogic(screen)
intro_system = IntroLogic(screen, game.clock, game.robot, game.interactions)

# 4. START THE GAME LOOP
running = True
current_state = "MENU"

while running:
    if current_state == "MENU":
        current_state = game.run_menu()
    elif current_state == "NAME_INPUT":
        current_state = game.run_name_input()
        
    elif current_state == "RULES":
        current_state = game.run_rules()
    elif current_state == "TUTORIAL":
        current_state = game.run_tutorial_loop() 
    elif current_state == "STORY":
        current_state = game.run_story()
    elif current_state == "INTRO":
        current_state = intro_system.run(game.session_data)
    elif current_state == "GAME":
        current_state = game.run_real_game_loop()
    elif current_state == "OUTRO":
        current_state = intro_system.run(game.session_data)
    elif current_state == "QUESTIONNAIRE":
        current_state = game.run_questionnaire_loop()
    elif current_state == "END":
        current_state = game.run_end_screen()
    elif current_state == "EXIT":
        running = False

pygame.quit()