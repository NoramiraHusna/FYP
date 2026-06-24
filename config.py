import pygame
import os

# --- Screen Settings ---
WIDTH, HEIGHT = 800, 600
FPS = 60
TILE_SIZE = 40 

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ASSET_DIR = os.path.join(BASE_DIR, 'assets')

PLAYER_SPEED = 4 # Slightly faster for the bigger map

# --- Game Settings ---
TONES = ["Optimistic", "Pessimistic"]
TUTORIAL_FOODS = ["Cake"]

# Real Game has 10 categories
GAME_FOODS = [
    "Taco", "Pizza", "Rice Bowl", "Pasta", "Noodles",
    "Sandwich", "Tea", "Coffee", "Juice", "Snack"
]
TOTAL_TASKS = len(GAME_FOODS)

# --- NEW: MAP COLORS FOR EACH FOOD (Village Mode) ---
# Each food gets a unique color on the map
MAP_ICON_COLORS = {
    "Taco": (255, 165, 0),      # Orange
    "Pizza": (255, 50, 50),     # Red
    "Rice Bowl": (240, 240, 240), # White
    "Pasta": (255, 255, 150),   # Pale Yellow
    "Noodles": (210, 180, 140), # Tan
    "Sandwich": (200, 150, 50), # Brown
    "Tea": (100, 200, 100),     # Tea Green
    "Coffee": (100, 50, 0),     # Dark Brown
    "Juice": (255, 100, 0),     # Dark Orange
    "Snack": (200, 100, 255)    # Purple
}

# --- EXISTING: DETAILED FOOD OPTIONS DICTIONARY ---
FOOD_OPTIONS = {
    "Taco":      ["Beef Taco", "Chicken Taco", "Fish Taco", "Veggie Taco"],
    "Pizza":     ["Pepperoni Pizza", "Hawaiian Pizza", "Tuna Pizza", "Vegetarian Pizza"],
    "Rice Bowl": ["Teriyaki Rice Bowl", "Spicy Sambal Rice Bowl", "Soy Sauce Rice Bowl", "Vegetable Rice Bowl"],
    "Pasta":     ["Carbonara", "Bolognese", "Aglio Olio", "Creamy Mushroom Pasta"],
    "Noodles":   ["Fried Noodles", "Soup Noodles", "Curry Noodles", "Tom Yum Noodles"],
    "Sandwich":  ["Egg Sandwich", "Tuna Sandwich", "Chicken Sandwich", "Veggie Sandwich"],
    "Tea":       ["Black Tea", "Milk Tea", "Green Tea", "Lemon Tea"],
    "Coffee":    ["Black Coffee", "Latte", "Cappuccino", "Mocha"],
    "Juice":     ["Orange Juice", "Apple Juice", "Mixed Fruit Juice", "Watermelon Juice"],
    "Snack":     ["Potato Chips", "Popcorn", "Cookies", "Chocolate Bar"]
}

# Helper list for coloring/button background
FOOD_COLORS = [
    (200, 100, 100), 
    (150, 150, 200), 
    (80, 180, 80),   
    (255, 200, 100)  
]