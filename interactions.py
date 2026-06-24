import pygame
import os
import socket
import json
from config import *
from ui_elements import draw_text, Button
from interaction_data import *

from interaction_flavor import FlavorSelector
from interaction_robot import RobotIntervention

# 🔌 Grab the physical robot connection to check if it's speaking!
from robot_interface import alpha_mini_hardware

class InteractionManager:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        
        self.UDP_IP = "127.0.0.1"
        self.SEND_PORT = 5005
        self.RECEIVE_PORT = 5006
        self.sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_receive.bind((self.UDP_IP, self.RECEIVE_PORT))
        self.sock_receive.setblocking(False)

        self.flavor_ui = FlavorSelector(screen, clock, self)
        self.robot_ui = RobotIntervention(screen, clock, self)

    def is_robot_busy(self):
        """🛡️ Centralized lock check used by all interaction sub-modules."""
        queue_len = len(alpha_mini_hardware.speech_queue) if isinstance(alpha_mini_hardware.speech_queue, list) else alpha_mini_hardware.speech_queue.qsize()
        return getattr(alpha_mini_hardware, 'is_speaking', False) or queue_len > 0

    def send_vision_command(self, command, phase_name):
        msg = {"command": command, "phase": phase_name}
        self.sock_send.sendto(json.dumps(msg).encode('utf-8'), (self.UDP_IP, self.SEND_PORT))

    def wait_for_vision_data(self, phase_name):
        start_wait = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_wait < 3000: 
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.display.toggle_fullscreen()
                
            try:
                data, addr = self.sock_receive.recvfrom(1024)
                msg = json.loads(data.decode('utf-8'))
                if msg.get("type") == "summary_data" and msg.get("phase") == phase_name:
                    return msg
            except BlockingIOError:
                pass
                
            self.clock.tick(60)
        print(f"Warning: Timed out waiting for OpenCV data for phase {phase_name}")
        return None

    def draw_styled_popup(self, rect, bg_color, border_color):
        shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, UI_SHADOW, shadow_surface.get_rect(), border_radius=20)
        self.screen.blit(shadow_surface, (rect.x + 8, rect.y + 8))
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=20)
        pygame.draw.rect(self.screen, border_color, rect, 4, border_radius=20)

    def load_smart_image(self, fname, size):
        path1 = os.path.join(ASSET_DIR, fname)
        path2 = os.path.join(ASSET_DIR, 'food', fname)
        
        final_path = None
        if os.path.exists(path1):
            final_path = path1
        elif os.path.exists(path2):
            final_path = path2
            
        if final_path:
            try:
                loaded = pygame.image.load(final_path).convert_alpha()
                return pygame.transform.scale(loaded, size)
            except Exception as e:
                print(f"❌ Error loading {fname}: {e}")
                return None
        else:
            print(f"❌ File Not Found: {fname}")
            return None

    def get_image_for_choice(self, food_name, choice_str):
        if food_name == "Cake" or (TUTORIAL_FOODS and food_name == TUTORIAL_FOODS[0]):
            return self.load_smart_image(f"Cake_{choice_str.lower()}.png", (80, 50))
        
        if food_name in FOOD_IMAGE_MAP:
            possible_opts = FOOD_OPTIONS.get(food_name, [])
            if choice_str in possible_opts:
                idx = possible_opts.index(choice_str)
                file_list = FOOD_IMAGE_MAP[food_name]
                if idx < len(file_list):
                    return self.load_smart_image(file_list[idx], (80, 50))
        return None

    def run_interaction_prompt(self, target_name, tone=None):
        BOX_W, BOX_H = 600, 320
        box_rect = pygame.Rect(WIDTH//2 - BOX_W//2, HEIGHT//2 - BOX_H//2, BOX_W, BOX_H)
        BUTTON_WIDTH = 450 
        BUTTON_X = WIDTH//2 - BUTTON_WIDTH//2 
        
        if "Alien" in target_name:
            if tone == "Optimistic":
                title_text = "CRYING CREATURE SPOTTED!"
                original_btn_text = "Approach the Crying Creature"
                opt_msg = "We caught the Alien! Go ahead and click the green Confront button so we can talk to him, Traveler!"
                pess_msg = "Alien caught. Click the green Confront button so we can finally get our Labubu back."
                self.robot.speak(tone, opt_msg, pess_msg)
            else:
                title_text = "ALIEN CAUGHT!" 
                original_btn_text = "Confront the Pink Weirdo"
                opt_msg = "We caught the Alien! Go ahead and click the green Confront button so we can talk to him, Traveler!"
                pess_msg = "Alien caught. Click the green Confront button so we can finally get our Labubu back."
                self.robot.speak(tone, opt_msg, pess_msg)
        else:
            title_text = f"FOUND {target_name.upper()} SELLER!"
            original_btn_text = f"Buy {target_name}"

        btn_interact = Button(BUTTON_X, HEIGHT//2, BUTTON_WIDTH, 55, original_btn_text, GREEN, (120, 255, 120))
        btn_nevermind = Button(BUTTON_X, HEIGHT//2 + 80, BUTTON_WIDTH, 55, "Maybe Later", GRAY, (170, 170, 170))

        running = True
        while running:
            # 🤖 THE BRAIN LOCK
            busy = self.is_robot_busy()

            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0,0))
            
            self.draw_styled_popup(box_rect, UI_CREAM, UI_MOCHA)
            draw_text(self.screen, title_text, 40, UI_MOCHA, WIDTH//2, HEIGHT//2 - 110)
            pygame.draw.line(self.screen, UI_MOCHA, (WIDTH//2 - 200, HEIGHT//2 - 70), (WIDTH//2 + 200, HEIGHT//2 - 70), 3)
            
            # Update button text visually
            btn_interact.text = "Please Wait..." if busy else original_btn_text

            mx, my = pygame.mouse.get_pos()
            click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return False 
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.display.toggle_fullscreen()
                    
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    # 🚫 Lock clicks!
                    if not busy:
                        click = True
            
            if not busy:
                btn_interact.check_hover((mx, my))
                btn_nevermind.check_hover((mx, my))
                
            btn_interact.draw(self.screen)
            btn_nevermind.draw(self.screen)
            
            # 🚨 NEW: BIG, HIGH-CONTRAST TOP NOTIFICATION BANNER
            if busy:
                warn_w = 550
                warn_rect = pygame.Rect(WIDTH//2 - warn_w//2, 30, warn_w, 60)
                
                # Banner shadow
                shadow_surf = pygame.Surface((warn_w, warn_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(shadow_surf, (0, 0, 0, 150), shadow_surf.get_rect(), border_radius=15)
                self.screen.blit(shadow_surf, (warn_rect.x + 5, warn_rect.y + 5))
                
                # Banner background & border
                pygame.draw.rect(self.screen, (40, 40, 40), warn_rect, border_radius=15)
                pygame.draw.rect(self.screen, (255, 100, 100), warn_rect, 3, border_radius=15)
                
                # Big bold text
                draw_text(self.screen, "⏳ PLEASE LISTEN TO ALPHA MINI...", 26, (255, 120, 120), WIDTH//2, warn_rect.centery)
            else:
                # Only allow the return values to trigger when the robot is entirely done talking
                if btn_interact.is_clicked((mx, my), click): return True 
                if btn_nevermind.is_clicked((mx, my), click): return False 

            pygame.display.flip()
            self.clock.tick(60)

    def run_robot_intervention(self, food_name, options, original_choice, tone, custom_lines, speaker_name="ROBOT", simple_mode=False):
        return self.robot_ui.run(food_name, options, original_choice, tone, custom_lines, speaker_name, simple_mode)

    def run_flavor_popup(self, food_name, robot_tone, custom_lines_dict=None, task_num=0): 
        prefix = ""
        if task_num > 0:
            suffixes = {1: "1st", 2: "2nd", 3: "3rd"}
            prefix = suffixes.get(task_num, f"{task_num}th")
            self.send_vision_command("START", f"{prefix}_Init")

        # 👉 THIS IS WHERE THE FLAVOR MENU LAUNCHES!
        selection = self.flavor_ui.run(food_name)
        
        init_data = None
        if task_num > 0:
            self.send_vision_command("STOP", f"{prefix}_Init")
            if selection:
                init_data = self.wait_for_vision_data(f"{prefix}_Init")

        if not selection:
            return None, None, False, None, None
            
        lines_to_use = custom_lines_dict.get(robot_tone.upper()) if custom_lines_dict else None
        
        if food_name == "Cake" or (TUTORIAL_FOODS and food_name == TUTORIAL_FOODS[0]):
             options = ["Vanilla", "Matcha", "Chocolate", "Strawberry"]
        else:
             options = FOOD_OPTIONS.get(food_name, [])

        if task_num > 0:
            self.send_vision_command("START", f"{prefix}_Final")
            
        final_choice, did_change = self.robot_ui.run(food_name, options, selection, robot_tone, lines_to_use)
        
        final_data = None
        if task_num > 0:
            self.send_vision_command("STOP", f"{prefix}_Final")
            final_data = self.wait_for_vision_data(f"{prefix}_Final")
        
        return selection, final_choice, did_change, init_data, final_data