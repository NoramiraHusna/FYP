import pygame
import time
import math
import random
from config import *
from sprites import Player, Wall, FoodItem, Camera, Floor, Decoration, Particle, Animal
from ui_elements import draw_text, TaskList, Button 

from task_taco import TaskTacoLogic 
from task_pizza import TaskPizzaLogic 
from task_ricebowl import TaskRiceBowlLogic
from task_pasta import TaskPastaLogic
from task_noodles import TaskNoodlesLogic
from task_sandwich import TaskSandwichLogic
from task_tea import TaskTeaLogic
from task_coffee import TaskCoffeeLogic
from task_juice import TaskJuiceLogic
from task_snack import TaskSnackLogic

class LevelLogic:
    def __init__(self, screen, clock, robot, interactions): 
        self.screen = screen
        self.clock = clock
        self.robot = robot
        self.interactions = interactions 
        
        self.food_strategies = {
            "Taco": TaskTacoLogic(screen, clock, robot, interactions),
            "Pizza": TaskPizzaLogic(screen, clock, robot, interactions), 
            "Rice Bowl": TaskRiceBowlLogic(screen, clock, robot, interactions),
            "Pasta": TaskPastaLogic(screen, clock, robot, interactions),
            "Noodles": TaskNoodlesLogic(screen, clock, robot, interactions),
            "Sandwich": TaskSandwichLogic(screen, clock, robot, interactions),
            "Tea": TaskTeaLogic(screen, clock, robot, interactions),
            "Coffee": TaskCoffeeLogic(screen, clock, robot, interactions),
            "Juice": TaskJuiceLogic(screen, clock, robot, interactions),
            "Snack": TaskSnackLogic(screen, clock, robot, interactions),
        }

        self.food_map_key = {
            "0": "Taco", "1": "Pizza", "2": "Rice Bowl", "3": "Pasta", "4": "Noodles",
            "5": "Sandwich", "6": "Tea", "7": "Coffee", "8": "Juice", "9": "Snack"
        }

    def load_map(self):
        # Animals: r=Rooster, k=Chick, U=Bull, u=Calf, E=Sheep, e=Lamb
        layout = [
            "TTTTTTTTTTTYYTTTTTTTTTTTTTTYYYYTTTTTTTTT",
            "T,,,,,,,,,,,,,F,,,,,,,,,,,,,,,,,,,,,,,,T",
            "T,,TTTTTT......YYYYYY......TTTTTT,,S,,,T",
            "T,,T0...T......Y1...Y......T2...T,,,,,,T", 
            "T,,T....T......Y....Y......T....T,,,B,,T",
            "Y,,TT..TT......YY..YY......TT..TT,,,,,,Y",
            "Y,,...B..........................F.....Y",
            "Y,,........F..........S................Y",
            "T,,,,,,,YYYYYY........TTTTTT,,,,,,,,,,,T", 
            "T,,,r,,,Y3...Y........T4...T,,,,,B,,,,,T", 
            "T,,k,k,,Y....Y........T....T,,,,U,,,,,,T", 
            "T,,,r,,,YY..YY........TT..TT,,u,u,U,,,,T", 
            "Y,,................................u,,,Y",
            "Y,,...5..............6.............7,,,Y", 
            "T,,..TTT............YYY...........TTT,,T",
            "T,,...S...........................B....T",
            "T,,TTTTTT.......F..............YYYYYY,,T",
            "T,,T8...T......................Y9...Y,,T", 
            "T,,T...............B.......S........Y,,T",
            "T,,TTTTTT....E,e...............YYYYYY,,T",
            "T,,,,,,,,....e,E,,,,,,,,S,,,,,,,,,,,,,,T",
            "TTTTTTTYYTTTTTTTTTTTTYYYYTTTTTTTTTTTTTTT",
        ]
        
        walls = pygame.sprite.Group()
        foods = pygame.sprite.Group()
        floors = pygame.sprite.Group() 
        decorations = pygame.sprite.Group()
        animals = pygame.sprite.Group()
        
        map_w, map_h = len(layout[0]) * TILE_SIZE, len(layout) * TILE_SIZE
        
        for row_idx, row in enumerate(layout):
            for col_idx, char in enumerate(row):
                x, y = col_idx * TILE_SIZE, row_idx * TILE_SIZE
                
                # Floors
                if char == ".": floors.add(Floor(x, y, "path"))
                else: floors.add(Floor(x, y, "grass"))
                    
                # Walls
                if char in ["T", "Y"]: 
                    walls.add(Wall(x, y, char))
                    
                # Decorations
                elif char == "B": decorations.add(Decoration(x, y, "B"))
                elif char == "F": decorations.add(Decoration(x, y, "F"))
                elif char == "S": decorations.add(Decoration(x, y, "S"))
                
                # Spawn Animals Free-Roaming
                elif char == "r": animals.add(Animal(x, y, "Rooster"))
                elif char == "k": animals.add(Animal(x, y, "Chick"))
                elif char == "U": animals.add(Animal(x, y, "Bull"))
                elif char == "u": animals.add(Animal(x, y, "Calf"))
                elif char == "E": animals.add(Animal(x, y, "Sheep"))
                elif char == "e": animals.add(Animal(x, y, "Lamb"))
                
                # Food Stalls
                elif char in self.food_map_key:
                    floors.add(Floor(x, y, "path"))
                    food_name = self.food_map_key[char]
                    color = MAP_ICON_COLORS.get(food_name, (255, 255, 255))
                    foods.add(FoodItem(x, y, food_name, color))
                        
        return walls, foods, floors, decorations, animals, map_w, map_h

    def run(self, session_data):
        session_data["mind_changes"] = 0
        session_data["mind_kept"] = 0
        session_data["selections"] = []
        session_data["interaction_history"] = []
        
        task_ui = TaskList(GAME_FOODS)
        player = Player(100, 100) 
        walls, foods, floors, decorations, animals, map_w, map_h = self.load_map()
        camera = Camera(map_w, map_h)
        particles = pygame.sprite.Group() 
        
        tasks_done = 0
        target_tasks = len(GAME_FOODS)
        
        # 🚩 NEW FLAG: Ensure Alpha Mini only says the outro dialogue once!
        has_spoken_outro = False
        
        session_data["start_time"] = time.time()
        self.robot.speak(session_data["tone"], "Explore the village! Find all 10 sellers.", "Don't get lost. Find all 10 sellers.")
        
        btn_return = Button(WIDTH//2 - 120, HEIGHT - 80, 240, 50, "RETURN TO ALIEN", CYAN, (100, 255, 255))

        # 🚀 PRE-RENDER TEXT SURFACES TO PREVENT LAG 🚀
        label_cache = {}
        try:
            font = pygame.font.SysFont("Arial", 18, bold=True)
        except:
            font = pygame.font.Font(None, 24)
            
        for f_name in GAME_FOODS:
            base_text = font.render(f_name.upper(), True, BLACK)
            outline_text = font.render(f_name.upper(), True, WHITE)
            
            w, h = base_text.get_size()
            surf = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
            
            # Draw the white outline onto our hidden image
            for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (-1, 0), (1, 0), (0, 1)]:
                surf.blit(outline_text, (dx + 1, dy + 1))
            # Draw the black text in the center
            surf.blit(base_text, (1, 1))
            
            # Save the image so we never have to render it again!
            label_cache[f_name] = surf

        running = True
        while running:
            self.clock.tick(FPS)
            keys = pygame.key.get_pressed()
            
            # 🛡️ THE BRAIN LOCK
            robot_busy = self.interactions.is_robot_busy()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "EXIT"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.display.toggle_fullscreen()
                task_ui.handle_input(event)

            # Prevent player movement while the robot is speaking
            if not robot_busy:
                player.update(keys, walls, particles) 
                particles.update() 
                animals.update(walls)
            
            hit_food_list = pygame.sprite.spritecollide(player, foods, False)
            for food in hit_food_list:
                
                want_to_interact = self.interactions.run_interaction_prompt(food.name)
                
                if want_to_interact:
                    task_ui.mark_found(food.name)
                    handler = self.food_strategies.get(food.name)
                    tone = session_data["tone"]
                    
                    success, init, final, changed, init_data, final_data = handler.run_task(tone, tasks_done + 1)
                    
                    if success: 
                        session_data["selections"].append(final)

                        history_entry = {
                            "shop": food.name,
                            "initial": init,
                            "init_arousal": init_data.get("mean_arousal", "N/A") if init_data else "N/A",
                            "init_emotion": init_data.get("dominant_emotion", "N/A") if init_data else "N/A",
                            "init_state": init_data.get("state", "N/A") if init_data else "N/A",
                            "final": final,
                            "final_arousal": final_data.get("mean_arousal", "N/A") if final_data else "N/A",
                            "final_emotion": final_data.get("dominant_emotion", "N/A") if final_data else "N/A",
                            "final_state": final_data.get("state", "N/A") if final_data else "N/A",
                            "changed": "Yes" if changed else "No"
                        }
                        session_data["interaction_history"].append(history_entry)

                        # ONLY UPDATE THE COUNTERS. NO EXTRA SPEECH!
                        if changed: 
                            session_data["mind_changes"] += 1
                        else: 
                            session_data["mind_kept"] += 1
                            
                        confetti_colors = [(255,50,50), (50,255,50), (50,50,255), (255,255,50), (255,50,255), (50,255,255), WHITE]
                        for _ in range(40):
                            c = random.choice(confetti_colors)
                            vx = random.uniform(-4, 4)
                            vy = random.uniform(-6, 0)
                            p = Particle(food.rect.centerx, food.rect.centery, c, (vx, vy), lifetime=50, gravity=0.2)
                            particles.add(p)
                        
                        food.kill()
                        tasks_done += 1
                
                else:
                    if player.direction == "left": player.rect.x += 10
                    elif player.direction == "right": player.rect.x -= 10
                    elif player.direction == "up": player.rect.y += 10
                    elif player.direction == "down": player.rect.y -= 10
                    player.pos_x = float(player.rect.x)
                    player.pos_y = float(player.rect.y)

            self.screen.fill(BLACK)
            camera.update(player)
            
            for sprite in floors: self.screen.blit(sprite.image, camera.apply(sprite))
            for sprite in decorations: self.screen.blit(sprite.image, camera.apply(sprite))
            for sprite in walls: self.screen.blit(sprite.image, camera.apply(sprite))
            for sprite in foods: self.screen.blit(sprite.image, camera.apply(sprite))
            for sprite in animals: self.screen.blit(sprite.image, camera.apply(sprite))
            for sprite in particles: self.screen.blit(sprite.image, camera.apply(sprite))
            
            self.screen.blit(player.image, camera.apply(player))
            
            for food in foods:
                # 🏷️ STAMP THE PRE-RENDERED CACHED IMAGE (Zero Lag!)
                if food.name in label_cache:
                    cached_surf = label_cache[food.name]
                    cx = camera.apply(food).centerx
                    cy = camera.apply(food).top - 15
                    self.screen.blit(cached_surf, (cx - cached_surf.get_width() // 2, cy - cached_surf.get_height() // 2))
                
                dist = math.hypot(player.rect.centerx - food.rect.centerx, player.rect.centery - food.rect.centery)
                if dist < 65:
                    bounce = math.sin(pygame.time.get_ticks() * 0.008) * 5
                    exclaim_y = camera.apply(food).top - 40 + bounce
                    
                    draw_text(self.screen, "!", 30, BLACK, camera.apply(food).centerx + 2, exclaim_y + 2)
                    draw_text(self.screen, "!", 30, (255, 230, 50), camera.apply(food).centerx, exclaim_y)

            task_ui.draw(self.screen)

            if tasks_done >= target_tasks:
                
                # 🗣️ NEW: Tell the player to click the Return button!
                if not has_spoken_outro:
                    tone = session_data["tone"]
                    opt_msg = "Yay! We collected all the food! Click the Return to Alien button at the bottom of the screen to give him the food!"
                    pess_msg = "Finally, we got everything. Click the Return to Alien button at the bottom so we can get our Labubu back."
                    self.robot.speak(tone, opt_msg, pess_msg)
                    has_spoken_outro = True
                
                mx, my = pygame.mouse.get_pos()
                click = False
                if pygame.mouse.get_pressed()[0]: click = True
                
                # Visual lock for the return button
                if robot_busy:
                    btn_return.text = "WAIT..."
                    btn_return.color = (130, 130, 130)
                    btn_return.hover_color = (130, 130, 130)
                else:
                    btn_return.text = "RETURN TO ALIEN"
                    btn_return.color = CYAN
                    btn_return.hover_color = (100, 255, 255)
                    btn_return.check_hover((mx, my))
                
                btn_return.draw(self.screen)
                
                if not robot_busy and btn_return.is_clicked((mx, my), click):
                    return "OUTRO" 

            # 🛑 SOLID WARNING BOX 
            if robot_busy:
                box_w = 460
                warning_rect = pygame.Rect(WIDTH//2 - box_w//2, 10, box_w, 40)
                pygame.draw.rect(self.screen, (30, 30, 30), warning_rect, border_radius=10)
                pygame.draw.rect(self.screen, (255, 100, 100), warning_rect, 2, border_radius=10)
                draw_text(self.screen, "Please listen to what Alpha Mini is saying...", 18, (255, 100, 100), WIDTH//2, 30)

            pygame.display.flip()