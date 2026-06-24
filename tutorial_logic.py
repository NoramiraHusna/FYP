import pygame
import math
import random
from config import *
from sprites import Player, Wall, FoodItem, Camera, Floor, Decoration, Particle
from ui_elements import draw_text, TaskList, Button

class TutorialLogic:
    def __init__(self, screen, clock, robot, interactions):
        self.screen = screen
        self.clock = clock
        self.robot = robot
        self.interactions = interactions
        self.history_data = []

        self.tutorial_phase = 0 
        self.walk_timer = 0
        self.run_timer = 0
        self.required_movement_frames = 50  

    def load_map(self):
        layout = [
            "TTTTTYYTTTTTTTTTTTTT",
            "T,,,,,,F,,,,,,,,,,,T",
            "T,,,........B,,,,,,T",
            "T,,,........,,,,,,,T",
            "Y,,,....S...,,,,,,,Y",
            "Y,,,........,,,,,,,Y",
            "T,,,........,,F,,,,T",
            "T,,,,,B,,,,,,,,,,,,T",
            "TTTTTTTTTTTTTYYTTTTT",
        ]
        
        walls = pygame.sprite.Group()
        foods = pygame.sprite.Group()
        floors = pygame.sprite.Group()
        decorations = pygame.sprite.Group()
        
        for row_idx, row in enumerate(layout):
            for col_idx, char in enumerate(row):
                x, y = col_idx * TILE_SIZE, row_idx * TILE_SIZE
                
                if char == ".": floors.add(Floor(x, y, "path"))
                else: floors.add(Floor(x, y, "grass"))
                
                if char == "T": walls.add(Wall(x, y, "T"))
                elif char == "Y": walls.add(Wall(x, y, "Y"))
                elif char == "B": decorations.add(Decoration(x, y, "B"))
                elif char == "F": decorations.add(Decoration(x, y, "F"))
                elif char == "S": decorations.add(Decoration(x, y, "S"))

        center_x = 10 * TILE_SIZE
        center_y = 4 * TILE_SIZE
        CAKE_COLOR = (255, 105, 180) 
        floors.add(Floor(center_x, center_y, "path"))
        foods.add(FoodItem(center_x, center_y, TUTORIAL_FOODS[0], CAKE_COLOR))
        
        return walls, foods, floors, decorations, len(layout[0]) * TILE_SIZE, len(layout) * TILE_SIZE

    def run(self, tone):
        self.history_data = [] 
        self.tutorial_phase = 0
        self.walk_timer = 0
        self.run_timer = 0
        
        task_ui = TaskList(TUTORIAL_FOODS)
        player = Player(100, 100) 
        walls, foods, floors, decorations, map_w, map_h = self.load_map()
        camera = Camera(map_w, map_h)
        particles = pygame.sprite.Group()
        
        tasks_done = 0
        guide_font = pygame.font.SysFont("Arial", 22, bold=True) 

        # 🔘 Buttons for Phase 4 (End of Tutorial)
        btn_repeat_tut = Button(WIDTH//2 - 210, HEIGHT - 110, 200, 60, "REPEAT", (220, 150, 40), (255, 180, 80))
        btn_proceed_tut = Button(WIDTH//2 + 10, HEIGHT - 110, 200, 60, "PROCEED", GREEN, (100, 255, 100))

        # 🗣️ PHASE 0: TEACH WALKING
        opt_msg = "Welcome to the tutorial mode, traveler! Let's learn how to move. First, press the W, A, S, or D keys on your keyboard to walk around."
        pess_msg = "Welcome... to the tutorial mode. Listen closely. First, press the W, A, S, or D keys on your keyboard to walk. Try it now."
        self.robot.speak(tone, opt_msg, pess_msg)

        running = True
        while running:
            self.clock.tick(FPS)
            keys = pygame.key.get_pressed()
            
            busy = self.interactions.is_robot_busy()
            
            mx, my = pygame.mouse.get_pos()
            click = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "EXIT"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.display.toggle_fullscreen()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click = True
                
                # 🖱️ PHASE 2: WAIT FOR UI CLICK
                if self.tutorial_phase == 2 and click:
                    if not busy and task_ui.icon_rect.collidepoint(event.pos):
                        task_ui.toggle()
                        self.tutorial_phase = 3
                        
                        # 🗣️ PHASE 3: PRAISE CLICK & TEACH NPC INTERACTION
                        opt_msg = "Perfect! You’ve opened the objectives panel, the task said to find cake so for step four, walk up to the NPC to interact with them. Let's go!"
                        pess_msg = "You’ve opened the objectives panel and it wrote: 'Find the cake.' Right. Finally... find the NPC and walk into them."
                        self.robot.speak(tone, opt_msg, pess_msg)
            
            # 🚶‍♂️ PHASE 0 LOGIC: CHECK FOR WALKING
            if self.tutorial_phase == 0:
                if not busy:
                    player.update(keys, walls, particles)
                    is_moving = keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d] or keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]
                    
                    if is_moving:
                        self.walk_timer += 1
                        
                    if self.walk_timer >= self.required_movement_frames:
                        self.tutorial_phase = 1
                        # 🗣️ PHASE 1: PRAISE WALKING & TEACH RUNNING
                        opt_msg = "Great job! Now for step two. Hold down the SHIFT key at the same time as the movement keys to run!"
                        pess_msg = "Alright, you can walk. Step two... hold down the SHIFT key while moving to run. Do it."
                        self.robot.speak(tone, opt_msg, pess_msg)

            # 🏃‍♂️ PHASE 1 LOGIC: CHECK FOR RUNNING
            elif self.tutorial_phase == 1:
                if not busy:
                    player.update(keys, walls, particles)
                    is_moving = keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d] or keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]
                    is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
                    
                    if is_moving and is_running:
                        self.run_timer += 1
                        
                    if self.run_timer >= (self.required_movement_frames - 10): 
                        self.tutorial_phase = 2
                        # 🗣️ PHASE 2: PRAISE RUNNING & TEACH UI
                        opt_msg = "Excellent! You are a fast learner! For step three, please click on the Task List icon in the upper-right corner!"
                        pess_msg = "Okay, you can run. Step three... click on the Task List icon in the upper-right corner."
                        self.robot.speak(tone, opt_msg, pess_msg)
                    
            # 🛑 PHASE 2 LOGIC: FREEZE PLAYER UNTIL THEY CLICK UI
            elif self.tutorial_phase == 2:
                player.state = "idle"
                player.animate()
                
            # 🗣️ PHASE 3 LOGIC: FIND THE NPC
            elif self.tutorial_phase == 3:
                if not busy:
                    player.update(keys, walls, particles)

                    hit_food_list = pygame.sprite.spritecollide(player, foods, False)
                    for food in hit_food_list:
                        
                        # 🗣️ 4. FOUND SHOP SCRIPT 
                        opt_msg = "Amazing, you've found the NPC! It looks like a cake shop! The shop offers Vanilla, Chocolate, Strawberry, and Matcha flavors! To proceed, we should click on the 'Buy Cake' option, traveler!"
                        pess_msg = "You've found the NPC. It's a cake shop. The shop offers Vanilla, Chocolate, Strawberry, and Matcha. Just click 'Buy Cake' and get this over with."
                        self.robot.speak(tone, opt_msg, pess_msg)

                        want_to_interact = self.interactions.run_interaction_prompt("Cake")
                        
                        if want_to_interact:
                            task_ui.mark_found(food.name)
                            selection = self.interactions.flavor_ui.run("Cake")
                            
                            if selection:
                                # 🗣️ 5. THE MAIN PERSUASION SCRIPT 
                                if selection in ["Vanilla", "Chocolate", "Strawberry"]:
                                    opt_msg = f"Okayyy {selection}! I see you! But wait... what if you tried matcha cake instead?! It’s actually such a good middle ground! Matcha has antioxidants, and gives stable energy, compared to sugary desserts. You get a gentle lift, without the crash! That’s the best combo, honestly! So, will you keep your choice or change to Matcha?"
                                    pess_msg = f"{selection} is just a safe choice, I guess... But you already know how this goes. You’ll enjoy it for a bit... then suddenly, you’re sick of eating it. Maybe... take the Matcha cake instead. It keeps you going... without that embarrassing crash. But yeah. Your call. Will you keep your choice or change to Matcha?"
                                    target_suggestion = "Matcha"
                                else:
                                    opt_msg = f"Matcha cake?! Okay wait, I love that you’re going for something aesthetic! But are you sure you don’t want something a bit more indulgent?! Imagine going for a rich chocolate cake instead! It hits immediately in the best emotional way! Go enjoy it! So, will you keep your choice or change to Chocolate?"
                                    pess_msg = f"Ah... Matcha cake. You actually chose that? I mean... if you really want something that just tastes like sad, plain grass... sure. Honestly, going for a basic chocolate cake might be better. At least it gives you a proper mood boost. But whatever. So, will you keep your choice or change to Chocolate?"
                                    target_suggestion = "Chocolate"

                                self.robot.speak(tone, opt_msg, pess_msg)

                                custom_options = [selection, target_suggestion]
                                ui_lines = ["Listen to Alpha Mini's suggestion...", "-> Choose to KEEP or CHANGE your decision."]
                                final, changed_mind = self.interactions.run_robot_intervention(food.name, custom_options, selection, tone, ui_lines)
                                
                                record = { "food": food.name, "init": selection, "final": final, "change": changed_mind }
                                self.history_data.append(record)
                        
                                # 🗣️ 6. UPDATED SUMMARY SCRIPT (Congrats & Button Instructions)
                                if changed_mind: 
                                    opt_msg = f"Yay! You chose {final}, traveller! I promise, you won’t regret it! Congratulations, you have completed the demonstration session! Click Proceed to begin the main game, or click Repeat if you want to try the tutorial again!"
                                    pess_msg = f"You changed to {final}. Let's move on. Congratulations, you completed the demonstration session! Click Proceed to begin the main game, or Repeat to practice again."
                                else: 
                                    opt_msg = f"That’s perfectly fine, traveller! You’ve kept {final}! I hope you enjoy every bite! Congratulations, you have completed the demonstration session! Click Proceed to begin the main game, or click Repeat if you want to try the tutorial again!"
                                    pess_msg = f"You kept {final}. Fine. Let's move on. Congratulations, you completed the demonstration session! Click Proceed to begin the main game, or Repeat to practice again."
                                
                                self.robot.speak(tone, opt_msg, pess_msg)
                                
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
                            # BOUNCE THE PLAYER BACK IF THEY DON'T INTERACT
                            if player.direction == "left": player.rect.x += 10
                            elif player.direction == "right": player.rect.x -= 10
                            elif player.direction == "up": player.rect.y += 10
                            elif player.direction == "down": player.rect.y -= 10
                            player.pos_x = float(player.rect.x)
                            player.pos_y = float(player.rect.y)

            # 🛑 TRANSITION TO PHASE 4: THE END SCREEN
            if tasks_done >= len(TUTORIAL_FOODS) and self.tutorial_phase == 3:
                self.tutorial_phase = 4

            particles.update()

            self.screen.fill(BLACK)
            camera.update(player)
            
            for sprite in floors: self.screen.blit(sprite.image, camera.apply(sprite))
            for sprite in decorations: self.screen.blit(sprite.image, camera.apply(sprite))
            for sprite in walls: self.screen.blit(sprite.image, camera.apply(sprite))
            for sprite in foods: self.screen.blit(sprite.image, camera.apply(sprite))
            
            for sprite in particles: self.screen.blit(sprite.image, camera.apply(sprite))
            self.screen.blit(player.image, camera.apply(player))
            
            for food in foods:
                draw_text(self.screen, "NPC", 20, BLACK, camera.apply(food).centerx, camera.apply(food).top - 15)
                
                dist = math.hypot(player.rect.centerx - food.rect.centerx, player.rect.centery - food.rect.centery)
                if dist < 65:
                    bounce = math.sin(pygame.time.get_ticks() * 0.008) * 5
                    draw_text(self.screen, "!", 30, (255, 230, 50), camera.apply(food).centerx, camera.apply(food).top - 40 + bounce)

            draw_text(self.screen, "TUTORIAL MODE", 20, WHITE, 90, 20)
            task_ui.draw(self.screen)
            
            if self.tutorial_phase == 2:
                bounce = math.sin(pygame.time.get_ticks() * 0.01) * 8
                arrow_x = WIDTH - 90
                arrow_y = 70 + bounce
                
                pygame.draw.line(self.screen, (255, 0, 255), (arrow_x - 30, arrow_y + 30), (arrow_x, arrow_y), 8)
                pygame.draw.polygon(self.screen, (255, 0, 255), [(arrow_x + 8, arrow_y - 8), (arrow_x - 15, arrow_y - 5), (arrow_x + 5, arrow_y + 15)])
                
                draw_text(self.screen, "CLICK HERE", 16, (255, 0, 255), arrow_x - 15, arrow_y + 50)

            if busy:
                box_w = 460
                warning_rect = pygame.Rect(WIDTH//2 - box_w//2, 10, box_w, 40)
                pygame.draw.rect(self.screen, (30, 30, 30), warning_rect, border_radius=10)
                pygame.draw.rect(self.screen, (255, 100, 100), warning_rect, 2, border_radius=10)
                draw_text(self.screen, "Please listen to what Alpha Mini is saying...", 18, (255, 100, 100), WIDTH//2, 30)

            # 📺 DRAW INSTRUCTIONS (PHASE 0-3)
            if self.tutorial_phase < 4:
                box_w, box_h = 700, 100 
                instruct_rect = pygame.Rect(WIDTH//2 - box_w//2, HEIGHT - 130, box_w, box_h)
                pygame.draw.rect(self.screen, (50, 50, 50), instruct_rect, border_radius=15)
                pygame.draw.rect(self.screen, WHITE, instruct_rect, 3, border_radius=15)

                def draw_line_segments(parts, y_pos):
                    total_width = sum(guide_font.size(text)[0] for text, color in parts)
                    current_x = WIDTH // 2 - (total_width // 2)
                    for text, color in parts:
                        surface = guide_font.render(text, True, color)
                        rect = surface.get_rect(topleft=(current_x, y_pos))
                        self.screen.blit(surface, rect)
                        current_x += surface.get_width()

                if self.tutorial_phase == 0:
                    line_parts = [("1. Press ", WHITE), ("W, A, S, D", CYAN), (" to walk.", WHITE)]
                    draw_line_segments(line_parts, HEIGHT - 95)
                elif self.tutorial_phase == 1:
                    line_parts = [("2. Hold ", WHITE), ("SHIFT", CYAN), (" while walking to run.", WHITE)]
                    draw_line_segments(line_parts, HEIGHT - 95)
                elif self.tutorial_phase == 2:
                    line_parts = [("3. Click the ", WHITE), ("TASK LIST ICON", YELLOW), (" in the top right corner.", WHITE)]
                    draw_line_segments(line_parts, HEIGHT - 95)
                elif self.tutorial_phase == 3:
                    line_parts = [("4. Walk into the ", WHITE), ("NPC", (255, 105, 180)), (" to interact with them.", WHITE)]
                    draw_line_segments(line_parts, HEIGHT - 95)
            
            # 🔘 DRAW BUTTONS (PHASE 4)
            else:
                if busy:
                    btn_repeat_tut.text = "Wait..."
                    btn_repeat_tut.color = (130, 130, 130)
                    btn_repeat_tut.hover_color = (130, 130, 130)
                    
                    btn_proceed_tut.text = "Wait..."
                    btn_proceed_tut.color = (130, 130, 130)
                    btn_proceed_tut.hover_color = (130, 130, 130)
                else:
                    btn_repeat_tut.text = "REPEAT"
                    btn_repeat_tut.color = (220, 150, 40)
                    btn_repeat_tut.hover_color = (255, 180, 80)
                    btn_repeat_tut.check_hover((mx, my))
                    
                    btn_proceed_tut.text = "PROCEED"
                    btn_proceed_tut.color = GREEN
                    btn_proceed_tut.hover_color = (100, 255, 100)
                    btn_proceed_tut.check_hover((mx, my))
                    
                btn_repeat_tut.draw(self.screen)
                btn_proceed_tut.draw(self.screen)
                
                # Wait for player's choice!
                if not busy:
                    if btn_proceed_tut.is_clicked((mx, my), click):
                        return "STORY" # Skips straight to the village
                    elif btn_repeat_tut.is_clicked((mx, my), click):
                        return "TUTORIAL" # Tells the main loop to completely restart the tutorial

            pygame.display.flip()