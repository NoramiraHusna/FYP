import pygame
import csv
import os
import time
import traceback
from config import *
from robot_interface import RobotInterface
from interactions import InteractionManager 
from menus import MenuManager
from tutorial_logic import TutorialLogic
from level_logic import LevelLogic
# Removed the menu_concept import

class GameLogic:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.robot = RobotInterface()
        self.interactions = InteractionManager(screen, self.clock)
        
        # 🛠️ THE FIX: Link the robot to the interactions manager
        self.interactions.robot = self.robot
        
        self.current_tone_index = 0
        self.all_sessions = [] 
        
        self._get_last_player_info()
        self.session_data = self.reset_session_data()

        self.menus = MenuManager(screen, self.clock)
        # Removed concept_screen initialization
        self.tutorial = TutorialLogic(screen, self.clock, self.robot, self.interactions)
        self.level = LevelLogic(screen, self.clock, self.robot, self.interactions) 
        
        self.state = "MENU"

    def _get_last_player_info(self):
        filepath = os.path.join(DATA_DIR, 'session_data.csv')
        if not os.path.exists(filepath): return
        
        try:
            with open(filepath, mode='r') as file:
                reader = list(csv.reader(file))
                if len(reader) > 1:
                    last_row = reader[-1]
                    try:
                        last_tone = last_row[1]
                        if last_tone in TONES:
                            idx = TONES.index(last_tone)
                            self.current_tone_index = (idx + 1) % len(TONES)
                    except Exception: pass

                    for row in reader[1:]:
                        try:
                            past_session = {
                                "player_name": row[0],
                                "tone": row[1],
                                "duration": row[2],
                                "mind_changes": int(row[-2]),
                                "mind_kept": int(row[-1])
                            }
                            self.all_sessions.append(past_session)
                        except Exception: continue

        except Exception as e: print("Error loading history:", e)

    def reset_session_data(self):
        return {
            "player_name": "", 
            "tone": TONES[self.current_tone_index],
            "mind_changes": 0,
            "mind_kept": 0,
            "start_time": 0,
            "end_time": 0,
            "interaction_history": [], 
            "selections": [],
            "tutorial_history": []
        }

    def format_time_string(self, total_seconds):
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        return f"{minutes}min {seconds}s"

    def get_csv_headers(self):
        header = ["Player_Name", "Tone", "Time"] 
        suffixes = {1: "st", 2: "nd", 3: "rd"}
        for i in range(1, 11):
            suf = suffixes.get(i, "th")
            prefix = f"{i}{suf}"
            header.extend([
                f"{prefix}_Shop", f"{prefix}_Init", 
                f"{prefix}_init_arousal", f"{prefix}_init_emotion", f"{prefix}_init_state",
                f"{prefix}_Final", 
                f"{prefix}_final_arousal", f"{prefix}_final_emotion", f"{prefix}_final_state", 
                f"{prefix}_Change?"
            ])
        header.extend(["Total_Changes", "Total_Kept"])
        return header

    def clear_save_data(self):
        if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
        
        session_path = os.path.join(DATA_DIR, 'session_data.csv')
        session_header = self.get_csv_headers()
        with open(session_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(session_header)

        survey_path = os.path.join(DATA_DIR, 'survey_data.csv')
        survey_header = ["Player_Name", "Tone"]
        for i in range(1, 9): survey_header.append(f"UI_{i}")
        for i in range(1, 9): survey_header.append(f"InGame_{i}")
        for i in range(1, 9): survey_header.append(f"Post_{i}")

        with open(survey_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(survey_header)

        self.current_tone_index = 0 
        self.all_sessions = []
        self.session_data = self.reset_session_data() 
        print("ALL Data (Session & Survey) has been reset!")

    def _transition(self, next_state):
        if next_state != self.state and next_state not in ["EXIT", self.state]:
            fade = pygame.Surface((WIDTH, HEIGHT))
            fade.fill(BLACK)
            for alpha in range(0, 255, 20): 
                fade.set_alpha(alpha)
                self.screen.blit(fade, (0,0))
                pygame.display.flip()
                self.clock.tick(60)
        self.state = next_state
        return self.state

    def run_menu(self):
        result = self.menus.run_main_menu()
        if result == "RESET_DATA":
            self.clear_save_data()
            return self._transition("MENU") 
        # Now it naturally returns "NAME_INPUT" straight from your menus
        return self._transition(result)

    # Removed run_game_concept entirely
            
    # --- FORCED SEQUENCE TRANSITIONS ---
        
    def run_name_input(self):
        result = self.menus.run_name_input()
        if isinstance(result, tuple):
            next_state, name = result
            if name: self.session_data["player_name"] = name
            if next_state not in ["EXIT", "MENU"]:
                return self._transition("RULES") 
            return self._transition(next_state)
        return self._transition("RULES") 

    def run_rules(self):
        result = self.menus.run_rules()
        if result not in ["EXIT", "MENU"]:
            return self._transition("TUTORIAL") 
        return self._transition(result)

    def run_tutorial_loop(self):
        try:
            result = self.tutorial.run(self.session_data["tone"])
            
            # 🔄 If the player clicked REPEAT, restart the tutorial loop!
            if result == "TUTORIAL":
                return self._transition("TUTORIAL")
                
            # ➡️ If the player clicked PROCEED, move forward to the story/intro
            elif result in ["INTRO", "STORY"]:
                return self._transition(result)
                
            # ❌ If the player closed the game or went to the main menu
            elif result in ["EXIT", "MENU"]:
                return self._transition(result)
                
            # Fallback default
            return self._transition("STORY")
            
        except Exception as e: 
            print(f"Tutorial Error: {e}")
            return self._transition("MENU")

    def run_tutorial_end_screen(self):
        return self._transition(self.menus.run_tutorial_end(self.tutorial.history_data))

    def run_story(self):
        result = self.menus.run_story()
        if result not in ["EXIT", "MENU"]:
            return self._transition("INTRO") 
        return self._transition(result)

    def run_real_game_loop(self):
        result = self.level.run(self.session_data)
        if result not in ["EXIT", "MENU"]:
            return self._transition("OUTRO") 
        return self._transition(result)

    def run_end_screen(self):
        raw_duration = self.session_data["end_time"] - self.session_data["start_time"]
        formatted_time = self.format_time_string(raw_duration)
        self.session_data["duration"] = raw_duration 
        
        display_data = self.session_data.copy()
        display_data["duration"] = formatted_time 
        self.all_sessions.append(display_data)
        
        if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
        filepath = os.path.join(DATA_DIR, 'session_data.csv')
        file_exists = os.path.isfile(filepath)
        header = self.get_csv_headers()

        row = [self.session_data["player_name"], self.session_data["tone"], formatted_time]
        history = self.session_data["interaction_history"]
        self.session_data["selections"] = [h["final"] for h in history]

        for i in range(10):
            if i < len(history):
                d = history[i]
                row.extend([
                    d["shop"], d["initial"], 
                    d.get("init_arousal", "N/A"), d.get("init_emotion", "N/A"), d.get("init_state", "N/A"),
                    d["final"], 
                    d.get("final_arousal", "N/A"), d.get("final_emotion", "N/A"), d.get("final_state", "N/A"),
                    d["changed"]
                ])
            else: 
                row.extend(["-"] * 10) 

        row.extend([self.session_data["mind_changes"], self.session_data["mind_kept"]])

        with open(filepath, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists: writer.writerow(header)
            writer.writerow(row)
        
        self.current_tone_index = (self.current_tone_index + 1) % len(TONES)
        self.session_data = self.reset_session_data()
        
        return self._transition(self.menus.run_game_summary(self.all_sessions))

    def run_questionnaire_loop(self):
        answers = self.menus.run_questionnaire()
        if answers == "EXIT": return self._transition("MENU")
        self.save_survey_data(answers)
        
        # 🐛 FIX: Return to MENU instead of END to break the infinite loop
        return self._transition("MENU")

    def save_survey_data(self, answers):
        if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
        filepath = os.path.join(DATA_DIR, 'survey_data.csv')
        file_exists = os.path.isfile(filepath)
        
        header = ["Player_Name", "Tone"]
        for i in range(1, 9): header.append(f"UI_{i}")
        for i in range(1, 9): header.append(f"InGame_{i}")
        for i in range(1, 9): header.append(f"Post_{i}")
        
        last_session = self.all_sessions[-1]
        row = [last_session.get("player_name", "Unknown"), last_session.get("tone", "Unknown")]
        row.extend(answers)
        
        with open(filepath, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists: writer.writerow(header)
            writer.writerow(row)
            
        print("Survey data saved successfully!")