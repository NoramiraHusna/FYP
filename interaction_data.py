# interaction_data.py
import pygame

# === THEME COLORS ===
UI_CREAM = (250, 245, 235)      
UI_MOCHA = (90, 70, 60)         
UI_SHADOW = (0, 0, 0, 80)       

# Pastel Palette for Generic Foods
FOOD_PALETTE = [
    (255, 180, 180), # Pastel Red
    (255, 235, 150), # Pastel Yellow
    (180, 220, 255), # Pastel Blue
    (180, 255, 180)  # Pastel Green
]

# Cake specific colors
CAKE_BG_COLORS = [
    (245, 235, 190), # Vanilla
    (185, 215, 160), # Matcha
    (140, 100, 80),  # Chocolate
    (245, 190, 200)  # Strawberry
]

# === MASTER IMAGE MAPPING (PNG UPDATED) ===
FOOD_IMAGE_MAP = {
    "Taco":      ["Taco_beef.png", "Taco_chicken.png", "Taco_fish.png", "Taco_veggie.png"],
    "Pizza":     ["Pizza_peperoni.png", "Pizza_hawaiian.png", "Pizza_tuna.png", "Pizza_veggie.png"],
    "Rice Bowl": ["Ricebowl_teriyaki.png", "Ricebowl_spicysambal.png", "Ricebowl_soysauce.png", "Ricebowl_veggie.png"],
    "Pasta":     ["Pasta_carbonara.png", "Pasta_bolognese.png", "Pasta_agliolio.png", "Pasta_creamymushroom.png"],
    "Noodles":   ["Noodles_fried.png", "Noodles_chickensoup.png", "Noodles_curry.png", "Noodles_tomyum.png"],
    "Sandwich":  ["Sandwich_egg.png", "Sandwich_tuna.png", "Sandwich_chicken.png", "Sandwich_veggie.png"],
    "Tea":       ["Tea_black.png", "Tea_milk.png", "Tea_green.png", "Tea_lemon.png"],
    "Coffee":    ["Coffee_black.png", "Coffee_latte.png", "Coffee_cappuccino.png", "Coffee_mocha.png"],
    "Juice":     ["Juice_orange.png", "Juice_apple.png", "Juice_mixedfruit.png", "Juice_watermelon.png"],
    "Snack":     ["Snack_potatochips.png", "Snack_popcorn.png", "Snack_cookies.png", "Snack_chocolatebar.png"]
}