import pygame
import time
from config import *
from sprites import Player, Wall, FoodItem, Camera
from ui_elements import draw_text, TaskList

class TaskLogicBase:
    """
    Base class for running a single food interaction task (1 of 10).
    """
    def __init__(self, screen, clock, robot, interactions, food_name):
        self.screen = screen
        self.clock = clock
        self.robot = robot
        self.interactions = interactions
        self.food_name = food_name
        
        # POPUP INTERVENTION DIALOGUE
        self.INTERVENTION_DIALOGUE = {
            "OPTIMISTIC": [
                f"Wait! That {food_name} is good, but...",
                "I have a feeling {suggestion} is better!",
                "Trust me, try {suggestion}!"
            ],
            "PESSIMISTIC": [
                f"Are you sure about {food_name}?",
                "It looks kind of suspicious...",
                "{suggestion} might be safer."
            ]
        }
        
        self.OPTIMISTIC_DIALOGUE = {}
        self.PESSIMISTIC_DIALOGUE = {}
        
    def load_task_map(self, player_start_x, player_start_y):
        layout = [
            "11111111111111111111",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "11111111111111111111",
        ]
        
        walls = pygame.sprite.Group()
        for row_idx, row in enumerate(layout):
            for col_idx, char in enumerate(row):
                x, y = col_idx * TILE_SIZE, row_idx * TILE_SIZE
                if char == "1": walls.add(Wall(x, y))
        
        foods = pygame.sprite.Group()
        target_x = 15 * TILE_SIZE
        target_y = 10 * TILE_SIZE
        f_type = "Healthy" if self.food_name in ["Taco", "Pizza"] else "Unhealthy"
        foods.add(FoodItem(target_x, target_y, self.food_name, f_type))

        return walls, foods, len(layout[0]) * TILE_SIZE, len(layout) * TILE_SIZE

    # UPDATED: Removed gender argument
    def run_task(self, tone, task_num=0):
        # 1. Open the Flavor Selection Popup
        initial_choice, final_choice, changed_mind, init_data, final_data = self.interactions.run_flavor_popup(
            self.food_name, 
            tone, 
            self.INTERVENTION_DIALOGUE,
            task_num
        )
        
        # If user cancelled
        if not initial_choice:
            return False, None, None, False, None, None

        # 2. Return all details including vision data
        return True, initial_choice, final_choice, changed_mind, init_data, final_data

    def run(self, session_data, task_ui, tasks_done, target_tasks):
        pass