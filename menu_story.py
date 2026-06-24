import pygame
import os
import math
from config import *
from ui_elements import Button, draw_text

# 🔌 Grab the physical robot connection
from robot_interface import alpha_mini_hardware

class StoryMenu:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.bg_image = self._load_background()

    def _load_background(self):
        bg_path = os.path.join(ASSET_DIR, 'introstory.png')
        try:
            img = pygame.image.load(bg_path).convert()
            # 💡 Leave 100 pixels of empty space at the bottom for our UI bar!
            return pygame.transform.scale(img, (WIDTH, HEIGHT - 100))
        except Exception as e:
            print(f"Warning: Story image not found. {e}")
            return None

    def queue_story_sequence(self):
        """🗣️ Break the 3rd POV story down to match the 4 comic panels!"""
        
        # 0. Intro
        alpha_mini_hardware.speak("SYSTEM", "Welcome to Foodie Adventure Traveler, this adventure is about you and me loyal robot companion, Alpha Mini.")

        # 1. Panel 1 (Far Left)
        alpha_mini_hardware.speak("SYSTEM", "You discover the Alien who stole your Labubu hiding beside his wrecked ship. It seems he is stranded and in desperate need of help.")

        # 2. Panel 2 (Middle Left)
        alpha_mini_hardware.speak("SYSTEM", "The Alien explains that he only took Labubu because he is lost, starving, and unable to enter the human village for help. He pleads with you and Alpha Mini to bring him food from his list, so he can survive and begin repairing his broken ship.")

        # 3. Panel 3 (Middle Right)
        alpha_mini_hardware.speak("SYSTEM", 
                                    "Similar to how you learn in the demostration session, you will make food choices for the Alien, and I will provide insights to help you make the final decisions for his survival. "
                                    "Your mission is clear: explore the village and gather the specific foods the Alien requests."
                                  )

        # 4. Panel 4 (Far Right)
        alpha_mini_hardware.speak("SYSTEM", "Once you’ve collected everything, return the food to the Alien. Only then will he release Labubu back to you!")

        # 5. The Final Question
        alpha_mini_hardware.speak("SYSTEM", "Do you understand your mission? If you understand, select Yes to move on to the main game. If you’d like to hear the mission again, select No.")

    def run(self):
        # 1. Place the buttons side-by-side in the center of the bottom bar
        btn_w = 150
        btn_h = 45
        gap = 30
        
        # Calculate start X so both buttons and the gap are perfectly centered
        start_x = (WIDTH // 2) - ((btn_w * 2 + gap) // 2)
        
        # Adding an orange color for the repeat button directly in the tuple
        btn_repeat = Button(start_x, HEIGHT - 65, btn_w, btn_h, "NO", (220, 150, 40), (255, 180, 80))
        btn_continue = Button(start_x + btn_w + gap, HEIGHT - 65, btn_w, btn_h, "YES", GREEN, (100, 255, 100))
        
        # 🗣️ 2. Queue up the sequenced story
        self.queue_story_sequence()

        frames_passed = 0
        running = True
        
        while running:
            frames_passed += 1
            
            # 🛡️ THE BRAIN LOCK & SPEECH TRACKER
            queue_len = len(alpha_mini_hardware.speech_queue) if isinstance(alpha_mini_hardware.speech_queue, list) else alpha_mini_hardware.speech_queue.qsize()
            is_speaking = getattr(alpha_mini_hardware, 'is_speaking', False)
            
            busy = is_speaking or queue_len > 0 or frames_passed < 10 
            
            # This number perfectly tracks which sentence Alpha Mini is currently reading out loud!
            items_remaining = queue_len + (1 if is_speaking else 0)

            # First fill the screen black (this creates our bottom UI bar)
            self.screen.fill(BLACK)

            # Then draw the image (it will leave the bottom 100px alone)
            if self.bg_image:
                self.screen.blit(self.bg_image, (0, 0))
            else:
                draw_text(self.screen, "STORY IMAGE MISSING", 40, WHITE, WIDTH//2, (HEIGHT-100)//2)

            mx, my = pygame.mouse.get_pos()
            click = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "EXIT"
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.display.toggle_fullscreen()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # 🚫 Lock clicks!
                    if event.button == 1 and not busy: 
                        click = True

            # 📍 DRAW THE BOUNCING ARROW FOR THE ACTIVE PANEL
            if is_speaking:
                # Match the remaining queue length to the correct panel index
                if items_remaining == 5: panel_idx = 0     # Panel 1
                elif items_remaining == 4: panel_idx = 1   # Panel 2
                elif items_remaining == 3: panel_idx = 2   # Panel 3
                elif items_remaining == 2: panel_idx = 3   # Panel 4
                else: panel_idx = -1                       # Intro or Outro (No arrow)

                if panel_idx != -1:
                    # ✅ FIXED: Calculates the exact center of each panel in a 1x4 horizontal strip!
                    panel_w = WIDTH // 4
                    # Point the arrow at the top 1/4th of the screen so it hovers over the panel
                    y_pos = (HEIGHT - 100) // 4 
                    
                    coords_1x4 = [
                        (int(panel_w * 0.5), y_pos),  # Panel 1 (Far Left)
                        (int(panel_w * 1.5), y_pos),  # Panel 2 (Middle Left)
                        (int(panel_w * 2.5), y_pos),  # Panel 3 (Middle Right)
                        (int(panel_w * 3.5), y_pos)   # Panel 4 (Far Right)
                    ]
                    
                    target_x, target_y = coords_1x4[panel_idx] 

                    # Make the arrow bounce!
                    bounce = math.sin(pygame.time.get_ticks() * 0.01) * 10
                    ay = target_y + bounce
                    
                    # Draw a highly visible bouncing arrow pointing DOWN at the panel
                    pygame.draw.line(self.screen, (255, 230, 50), (target_x, ay - 60), (target_x, ay), 10)
                    pygame.draw.polygon(self.screen, (255, 230, 50), [
                        (target_x, ay), 
                        (target_x - 18, ay - 20), 
                        (target_x + 18, ay - 20)
                    ])
                    
                    # White outline text for contrast
                    for dx, dy in [(-1,-1),(1,-1),(-1,1),(1,1)]:
                        draw_text(self.screen, "LOOK HERE!", 24, BLACK, target_x + dx, ay - 80 + dy)
                    draw_text(self.screen, "LOOK HERE!", 24, WHITE, target_x, ay - 80)

            # 🎨 BUTTON VISUAL LOCK
            if busy:
                btn_repeat.text = "Wait..."
                btn_repeat.color = (130, 130, 130)
                btn_repeat.hover_color = (130, 130, 130)
                
                btn_continue.text = "Wait..."
                btn_continue.color = (130, 130, 130)
                btn_continue.hover_color = (130, 130, 130)
            else:
                btn_repeat.text = "No"
                btn_repeat.color = (220, 150, 40)
                btn_repeat.hover_color = (255, 180, 80)
                btn_repeat.check_hover((mx, my))
                
                btn_continue.text = "Yes"
                btn_continue.color = GREEN
                btn_continue.hover_color = (100, 255, 100)
                btn_continue.check_hover((mx, my))
                
            # ⏳ Show warning text centered in the top half of the black bar
            if busy:
                draw_text(self.screen, "Please listen to Alpha Mini...", 18, (255, 100, 100), WIDTH // 2, HEIGHT - 85)
            else:
                draw_text(self.screen, "Do you understand the mission?", 18, (200, 200, 200), WIDTH // 2, HEIGHT - 85)
            
            btn_repeat.draw(self.screen)
            btn_continue.draw(self.screen)
            
            # Proceed only if completely unlocked
            if not busy:
                if btn_continue.is_clicked((mx, my), click):
                    return "RULES"
                elif btn_repeat.is_clicked((mx, my), click):
                    # 🔄 RE-TRIGGER THE SPEECH AND RESET THE BRAIN LOCK
                    self.queue_story_sequence()
                    frames_passed = 0

            pygame.display.flip()
            self.clock.tick(60)