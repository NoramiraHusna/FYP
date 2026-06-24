import pygame
import time
from config import *
from sprites import Player, Wall, Alien, Camera, Floor, Decoration, Ruin
from ui_elements import draw_text, Button

UI_CREAM = (250, 245, 235)
UI_MOCHA = (90, 70, 60)

class IntroLogic:
    def __init__(self, screen, clock, robot, interactions):
        self.screen = screen
        self.clock = clock
        self.robot = robot
        self.interactions = interactions

    def load_map(self, tone):
        layout = [
            "TTTYYTTTTTTTTTYYTTTT",
            "TY,,,,S,,T,,,,,,,YTT",
            "T,,1,,,....,,,2,,,,T",
            "T,,,F.......B,,Y,,,T",
            "TY,,,,....A....,4,,T",
            "T,T,,,..3.....,,,,,T",
            "T,,,,,,,......,,F,,T",
            "T,,S,,T,,,5,,,B,,T,T",
            "TT,,,,Y,,,,,,,,,Y,TT",
            "TTTTTTTYYTTTTTTTTTTT",
        ]
        
        walls = pygame.sprite.Group()
        aliens = pygame.sprite.Group()
        floors = pygame.sprite.Group()
        decorations = pygame.sprite.Group()
        
        map_w, map_h = len(layout[0]) * TILE_SIZE, len(layout) * TILE_SIZE
        
        for row_idx, row in enumerate(layout):
            for col_idx, char in enumerate(row):
                x, y = col_idx * TILE_SIZE, row_idx * TILE_SIZE
                
                if char == ".": floors.add(Floor(x, y, "path", tone))
                else: floors.add(Floor(x, y, "grass", tone))
                
                if char == "T": walls.add(Wall(x, y, "T"))
                elif char == "Y": walls.add(Wall(x, y, "Y"))
                elif char == "B": decorations.add(Decoration(x, y, "B"))
                elif char == "F": decorations.add(Decoration(x, y, "F"))
                elif char == "S": decorations.add(Decoration(x, y, "S"))
                
                elif char in ["1", "2", "3", "4", "5"]:
                    walls.add(Ruin(x, y, char, tone)) 
                    
                elif char == "A":
                    floors.add(Floor(x, y, "path", tone))
                    aliens.add(Alien(x, y, tone))
                        
        return walls, aliens, floors, decorations, map_w, map_h

    def run(self, session_data):
        tone = session_data["tone"]
        player = Player(100, 300) 
        walls, aliens, floors, decorations, map_w, map_h = self.load_map(tone)
        camera = Camera(map_w, map_h)
        
        is_intro = len(session_data["selections"]) == 0
        story_read = False
        
        # 🗣️ 1. SETUP THE STORY AND ROBOT SPEECH
        if is_intro:
            opt_story = "You hear a familiar jingle behind you. Your limited-edition Labubu is gone! That alien just took it... But he looks lost, scared, and hungry. Approach him gently. Maybe he just needs help?"
            pess_story = "You hear a familiar jingle behind you. Your limited-edition Labubu is gone! That alien just stole it. He's trying to run away into this area. Chase him down and get your Labubu back."
            self.robot.speak(tone, opt_story, pess_story)
            
            # WIDENED THE BUTTON: Width changed from 200 to 280, moved X and Y to center perfectly in the new smaller box
            btn_start_story = Button(WIDTH//2 - 140, HEIGHT//2 + 50, 280, 50, "APPROACH", GREEN, (100, 255, 100))
            btn_teleport = Button(WIDTH//2 - 120, HEIGHT - 100, 240, 60, "GO TO VILLAGE", CYAN, (100, 255, 255))
        else:
            opt_outro = "We have the items! Let's go give them to the alien."
            pess_outro = "We have the items. Give them to the alien and let's get out of here."
            self.robot.speak(tone, opt_outro, pess_outro)
            
            btn_teleport = Button(WIDTH//2 - 120, HEIGHT - 100, 240, 60, "FINISH MISSION", GREEN, (100, 255, 100))

        show_button = False
        has_spoken_to_alien = False 
        
        running = True
        while running:
            self.clock.tick(FPS)
            click = False
            
            # 🛡️ THE BRAIN LOCK
            busy = self.interactions.is_robot_busy()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "EXIT"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.display.toggle_fullscreen()
                if event.type == pygame.MOUSEBUTTONDOWN and not busy: 
                    click = True
            
            self.screen.fill((20, 50, 20)) 
            camera.update(player)
            
            for sprite in floors: self.screen.blit(sprite.image, camera.apply(sprite))
            for sprite in decorations: self.screen.blit(sprite.image, camera.apply(sprite))
            for sprite in walls: self.screen.blit(sprite.image, camera.apply(sprite))
            for sprite in aliens: self.screen.blit(sprite.image, camera.apply(sprite))
            
            self.screen.blit(player.image, camera.apply(player))
            
            # 🛠️ THE FIX: Drawing the Alien Label dynamically based on camera position
            for alien in aliens:
                alien_screen_rect = camera.apply(alien) 
                draw_text(self.screen, "ALIEN", 16, WHITE, alien_screen_rect.centerx, alien_screen_rect.top - 15)
                
            draw_text(self.screen, "ALIEN HIDEOUT", 20, WHITE, 80, 20)
            
            if busy and story_read:
                draw_text(self.screen, "⏳ Listen to Alpha Mini...", 22, (255, 100, 100), WIDTH//2, 30)

            # 📖 STORY POPUP LOGIC
            if is_intro and not story_read:
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(150)
                overlay.fill(BLACK)
                self.screen.blit(overlay, (0,0))

                # SHRUNK THE WHITE BOX: Changed from 700x420 to 550x240
                popup_w, popup_h = 550, 240
                story_rect = pygame.Rect(WIDTH//2 - popup_w//2, HEIGHT//2 - popup_h//2, popup_w, popup_h)
                self.interactions.draw_styled_popup(story_rect, UI_CREAM, UI_MOCHA)
                
                title = "STORY EVENT" 
                draw_text(self.screen, title, 30, UI_MOCHA, WIDTH//2, HEIGHT//2 - 80)
                pygame.draw.line(self.screen, UI_MOCHA, (WIDTH//2 - 200, HEIGHT//2 - 50), (WIDTH//2 + 200, HEIGHT//2 - 50), 3)

                # Added the clean instruction text
                story_lines = [
                    "Listen to Alpha Mini explaining what happened.",  
                ]

                start_y = HEIGHT//2 - 20
                for i, line in enumerate(story_lines):
                    draw_text(self.screen, line, 22, (60, 50, 50), WIDTH//2, start_y + (i * 30))

                mx, my = pygame.mouse.get_pos()
                
                # 🎨 VISUAL LOCK FOR STORY BUTTON
                if busy:
                    btn_start_story.text = "LISTEN..."
                    btn_start_story.color = (130, 130, 130)
                    btn_start_story.hover_color = (130, 130, 130)
                else:
                    btn_start_story.text = "APPROACH GENTLY" if tone == "Optimistic" else "RUN AFTER HIM"
                    btn_start_story.color = GREEN
                    btn_start_story.hover_color = (100, 255, 100)
                    btn_start_story.check_hover((mx, my))

                btn_start_story.draw(self.screen)

                if not busy and btn_start_story.is_clicked((mx, my), click):
                    story_read = True

                pygame.display.flip()
                continue 

            # 🏃 MOVEMENT LOGIC (LOCKED WHILE BUSY)
            keys = pygame.key.get_pressed()
            dummy_particles = pygame.sprite.Group() 
            if not busy:
                try:
                    player.update(keys, walls, dummy_particles)
                except TypeError:
                    player.update(keys, walls)
            
            aliens.update()
            
            # 👽 ALIEN INTERACTION
            hit_alien = pygame.sprite.spritecollide(player, aliens, False)
            if hit_alien and not has_spoken_to_alien and not busy:
                want_chat = self.interactions.run_interaction_prompt("Alien", tone=tone)
                if want_chat:
                    if is_intro:
                        opt_talk = "I'm sorry I took your toy... I was just so hungry and scared. Could you bring me some food from this list?"
                        pess_talk = "Finally. You caught me. Yes, I took your Labubu. Bring me food if you want it back."
                        self.robot.speak(tone, opt_talk, pess_talk)
                        
                        # Added simple instruction lines back
                        lines_ui = ["Listen to Alpha Mini translating...", "Please wait for the alien's response."]
                        self.interactions.run_robot_intervention("Alien", [], "", tone, lines_ui, speaker_name="ALIEN VISITOR", simple_mode=True)
                        
                        # 🗣️ NEW: Instruct the player to click the teleport button!
                        opt_btn = "Okay Traveler! Click the Go To Village button at the bottom of the screen so we can start finding the food!"
                        pess_btn = "Alright. Click the Go To Village button at the bottom so we can get this over with."
                        self.robot.speak(tone, opt_btn, pess_btn)
                    else: 
                        opt_talk = "You came back! Yay! Thank you for the food, here is your toy back! I think we just became best friends!"
                        pess_talk = "Finally... took you long enough. Ugh... fine. Here is your Labubu. Now leave me alone."
                        self.robot.speak(tone, opt_talk, pess_talk)
                        
                        lines_ui = ["Listen to Alpha Mini translating...", "Please wait for the alien's response."]
                        self.interactions.run_robot_intervention("Alien", [], "", tone, lines_ui, speaker_name="ALIEN VISITOR", simple_mode=True)
                        
                        # 🗣️ NEW: Instruct the player to click the finish button!
                        opt_btn = "We did it! Click the Finish Mission button at the bottom to complete our adventure!"
                        pess_btn = "Finally. Click the Finish Mission button at the bottom so we can leave."
                        self.robot.speak(tone, opt_btn, pess_btn)
                    
                    show_button = True 
                    has_spoken_to_alien = True
                else:
                    if player.direction == "left": player.rect.x += 10
                    elif player.direction == "right": player.rect.x -= 10
                    elif player.direction == "up": player.rect.y += 10
                    elif player.direction == "down": player.rect.y -= 10
                    player.pos_x = float(player.rect.x)
                    player.pos_y = float(player.rect.y)

            # 🚪 TELEPORT BUTTON LOGIC
            if show_button:
                mx, my = pygame.mouse.get_pos()
                
                if busy:
                    btn_teleport.text = "WAIT..."
                    btn_teleport.color = (130, 130, 130)
                    btn_teleport.hover_color = (130, 130, 130)
                else:
                    btn_teleport.text = "GO TO VILLAGE" if is_intro else "FINISH MISSION"
                    btn_teleport.color = CYAN if is_intro else GREEN
                    btn_teleport.hover_color = (100, 255, 255) if is_intro else (100, 255, 100)
                    btn_teleport.check_hover((mx, my))
                
                btn_teleport.draw(self.screen)
                
                if not busy and btn_teleport.is_clicked((mx, my), click):
                    if is_intro: return "GAME" 
                    else:
                        session_data["end_time"] = time.time()
                        return "END" 

            pygame.display.flip()