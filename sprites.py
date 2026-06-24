import pygame
import os
import random
from config import *

# --- PARTICLE SYSTEM FOR FOOTSTEPS & CONFETTI ---
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, velocity, lifetime, gravity=0):
        super().__init__()
        size = random.randint(3, 6)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.start_life = lifetime
        self.gravity = gravity
        self.pos_x, self.pos_y = float(x), float(y)
        
    def update(self):
        self.vy += self.gravity
        self.pos_x += self.vx
        self.pos_y += self.vy
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)
        
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        else:
            alpha = int(255 * (self.lifetime / self.start_life))
            self.image.set_alpha(alpha)

# --- SPRINT GHOST TRAIL ---
class DashTrail(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image.copy()
        self.image.set_alpha(100)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.alpha = 100

    def update(self):
        self.alpha -= 10
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)

# --- TONE-MATCHING FLOORS ---
class Floor(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_type="grass", tone=None):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        
        # OPTIMISTIC TONE (Blue-Gray matching)
        if tone == "Optimistic":
            if tile_type in ["grass", "burnt_grass"]:
                base_color = (80, 130, 120)  
                tone_colors = [(70, 110, 100), (90, 150, 140), (60, 120, 110)]
            elif tile_type in ["path", "burnt_path"]:
                base_color = (130, 140, 150) 
                tone_colors = [(110, 120, 130), (150, 160, 170), (120, 130, 140)]
                
        # PESSIMISTIC TONE (Brown matching)
        elif tone == "Pessimistic":
            if tile_type in ["grass", "burnt_grass"]:
                base_color = (130, 120, 70)  
                tone_colors = [(110, 100, 50), (150, 140, 90), (120, 110, 60)]
            elif tile_type in ["path", "burnt_path"]:
                base_color = (140, 100, 70)  
                tone_colors = [(120, 80, 50), (160, 120, 90), (130, 90, 60)]
                
        # DEFAULT (Village/Tutorial)
        else:
            if tile_type == "grass":
                base_color = (110, 190, 100)
                tone_colors = [(90, 170, 80), (130, 210, 120), (100, 180, 90)] 
            elif tile_type == "path":
                base_color = (210, 180, 140)
                tone_colors = [(190, 160, 120), (230, 200, 160), (200, 170, 130)]
            elif tile_type == "burnt_grass":
                base_color = (60, 90, 50) 
                tone_colors = [(50, 70, 40), (80, 100, 60), (40, 60, 30)]
            elif tile_type == "burnt_path":
                base_color = (120, 100, 80) 
                tone_colors = [(90, 70, 60), (140, 120, 100), (70, 50, 40)]

        self.image.fill(base_color)

        for _ in range(25):
            sx = random.randint(0, TILE_SIZE - 2)
            sy = random.randint(0, TILE_SIZE - 2)
            size = random.randint(1, 3) 
            color = random.choice(tone_colors)
            pygame.draw.rect(self.image, color, (sx, sy, size, size))
            
        self.rect = self.image.get_rect(topleft=(x, y))

class Decoration(pygame.sprite.Sprite):
    def __init__(self, x, y, dec_type="B"):
        super().__init__()
        try:
            if dec_type == "B": img = pygame.image.load(os.path.join(ASSET_DIR, 'Plant3.png')).convert_alpha() 
            elif dec_type == "F": img = pygame.image.load(os.path.join(ASSET_DIR, 'Plant4.png')).convert_alpha() 
            else: img = pygame.image.load(os.path.join(ASSET_DIR, 'Plant5.png')).convert_alpha() 
            self.image = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        except:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))

# --- RUINS FOR THE CRASH SITE ---
class Ruin(pygame.sprite.Sprite):
    def __init__(self, x, y, ruin_id, tone):
        super().__init__()
        prefix = "Blue-gray" if tone == "Optimistic" else "Brown"
        filename = f"{prefix}_ruins{ruin_id}.png"
        try:
            img = pygame.image.load(os.path.join(ASSET_DIR, filename)).convert_alpha()
            self.image = pygame.transform.scale(img, (TILE_SIZE * 2, TILE_SIZE * 2))
        except Exception as e:
            self.image = pygame.Surface((TILE_SIZE * 2, TILE_SIZE * 2))
            color = (130, 140, 150) if tone == "Optimistic" else (140, 100, 70)
            self.image.fill(color)
            
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, wall_type="T"):
        super().__init__()
        
        # INVISIBLE WALL
        if wall_type == "W":
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            return
            
        # STANDARD TREES
        try:
            if wall_type == "T": img = pygame.image.load(os.path.join(ASSET_DIR, 'Plant1.png')).convert_alpha()
            elif wall_type == "Y": img = pygame.image.load(os.path.join(ASSET_DIR, 'Plant2.png')).convert_alpha()
            self.image = pygame.transform.scale(img, (TILE_SIZE + 10, TILE_SIZE + 10))
        except:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((34, 139, 34)) 
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.rect = pygame.Rect(x, y, 24, 24)
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.direction = "down"
        self.state = "idle"
        self.frame_index = 0
        self.animation_speed = 0.15
        
        filename = "Female_Player.png" 
        self.sprite_sheet = pygame.image.load(os.path.join(ASSET_DIR, filename)).convert_alpha()
        self.animations = {}
        self.load_animations()
        self.image = self.animations["idle_down"][0]

    def load_animations(self):
        SPRITE_SIZE = 32 
        FRAME_COUNT = 4  
        self.animations["idle_down"]  = self.get_row_images(0, FRAME_COUNT, SPRITE_SIZE)
        self.animations["idle_left"]  = self.get_row_images(2, FRAME_COUNT, SPRITE_SIZE)
        self.animations["idle_right"] = self.get_row_images(1, FRAME_COUNT, SPRITE_SIZE)
        self.animations["idle_up"]    = self.get_row_images(3, FRAME_COUNT, SPRITE_SIZE)
        self.animations["walk_down"]  = self.get_row_images(5, FRAME_COUNT, SPRITE_SIZE)
        self.animations["walk_left"]  = self.get_row_images(7, FRAME_COUNT, SPRITE_SIZE)
        self.animations["walk_right"] = self.get_row_images(9, FRAME_COUNT, SPRITE_SIZE)
        self.animations["walk_up"]    = self.get_row_images(11, FRAME_COUNT, SPRITE_SIZE)

    def get_row_images(self, row, count, sprite_size):
        images = []
        sheet_width = self.sprite_sheet.get_width()
        for col in range(count):
            x = col * sprite_size
            y = row * sprite_size
            if x + sprite_size > sheet_width: break
            rect = pygame.Rect(x, y, sprite_size, sprite_size)
            try:
                image = self.sprite_sheet.subsurface(rect)
                scaled_image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
                images.append(scaled_image)
            except ValueError:
                pass
        return images

    def update(self, keys, walls, particles):
        dx, dy = 0, 0
        self.state = "idle" 
        
        is_sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        speed = PLAYER_SPEED * 1.6 if is_sprinting else PLAYER_SPEED
        self.animation_speed = 0.30 if is_sprinting else 0.15

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -speed; self.direction = "left"; self.state = "walk"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = speed; self.direction = "right"; self.state = "walk"
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -speed; self.direction = "up"; self.state = "walk"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = speed; self.direction = "down"; self.state = "walk"
            
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
            
        if self.state == "walk":
            if is_sprinting and random.random() < 0.4:
                particles.add(DashTrail(self.image, self.rect.x, self.rect.y))
            if random.random() < (0.3 if is_sprinting else 0.1):
                p = Particle(self.rect.centerx, self.rect.bottom, (200, 180, 150), 
                             (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0)), 20)
                particles.add(p)
        
        self.pos_x += dx
        self.rect.x = int(self.pos_x)
        if pygame.sprite.spritecollideany(self, walls):
            self.pos_x -= dx
            self.rect.x = int(self.pos_x)
            
        self.pos_y += dy
        self.rect.y = int(self.pos_y)
        if pygame.sprite.spritecollideany(self, walls):
            self.pos_y -= dy
            self.rect.y = int(self.pos_y)

        self.animate()

    def animate(self):
        animation_key = f"{self.state}_{self.direction}"
        if animation_key in self.animations and self.animations[animation_key]:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations[animation_key]):
                self.frame_index = 0
            self.image = self.animations[animation_key][int(self.frame_index)]

class FoodItem(pygame.sprite.Sprite):
    def __init__(self, x, y, name, color):
        super().__init__()
        self.name = name
        SPRITE_WIDTH = 16  
        SPRITE_HEIGHT = 16 
        
        seller_row_map = {
            "Taco": 0, "Pizza": 1, "Rice Bowl": 2, "Pasta": 3, "Noodles": 4,
            "Sandwich": 5, "Tea": 6, "Coffee": 7, "Juice": 8, "Snack": 9,
            "Cake": 10 
        }
        
        try:
            sheet = pygame.image.load(os.path.join(ASSET_DIR, 'Characters_V3_Colour.png')).convert_alpha()
            row = seller_row_map.get(name, 0)
            frame_rect = pygame.Rect(0, row * SPRITE_HEIGHT, SPRITE_WIDTH, SPRITE_HEIGHT)
            image = sheet.subsurface(frame_rect)
            self.image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        except Exception as e:
            self.image = pygame.Surface((TILE_SIZE - 10, TILE_SIZE - 10))
            self.image.fill(color)
            pygame.draw.rect(self.image, WHITE, self.image.get_rect(), 2)
            
        self.rect = self.image.get_rect()
        self.rect.center = (x + TILE_SIZE//2, y + TILE_SIZE//2)

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        offset_x = -4 
        offset_y = -8
        rect_to_draw = entity.rect.move(self.camera.topleft)
        rect_to_draw.x += offset_x
        rect_to_draw.y += offset_y
        return rect_to_draw

    def update(self, target):
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)
        x = min(0, max(-(self.width - WIDTH), x))
        y = min(0, max(-(self.height - HEIGHT), y))
        self.camera = pygame.Rect(x, y, self.width, self.height)

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, tone):
        super().__init__()
        if tone == "Optimistic": filename = "Optimist_alien.png"
        else: filename = "Pessimist_alien.png"
            
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 0.1 
        
        try:
            sheet = pygame.image.load(os.path.join(ASSET_DIR, filename)).convert_alpha()
            SPRITE_WIDTH = 32
            SPRITE_HEIGHT = 32
            for i in range(4):
                frame_rect = pygame.Rect(i * SPRITE_WIDTH, 0, SPRITE_WIDTH, SPRITE_HEIGHT)
                image = sheet.subsurface(frame_rect)
                scaled_image = pygame.transform.scale(image, (48, 48))
                
                # CRASH SURVIVOR TEXTURE (DIRT & ASH)
                dirt_surface = pygame.Surface((48, 48), pygame.SRCALPHA)
                for _ in range(50): 
                    sx = random.randint(0, 47)
                    sy = random.randint(0, 47)
                    size = random.randint(1, 3)
                    color = random.choice([(40, 40, 40, 180), (70, 50, 40, 180), (120, 40, 40, 120)])
                    pygame.draw.rect(dirt_surface, color, (sx, sy, size, size))
                    
                mask = pygame.mask.from_surface(scaled_image)
                mask_surf = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(255, 255, 255, 0))
                dirt_surface.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                scaled_image.blit(dirt_surface, (0, 0))
                self.frames.append(scaled_image)
        except Exception as e:
            color = (100, 255, 100) if tone == "Optimistic" else (100, 100, 100)
            fallback = pygame.Surface((48, 48))
            fallback.fill(color)
            self.frames = [fallback, fallback, fallback, fallback]

        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
        self.image = self.frames[int(self.current_frame)]

# --- REWRITTEN: FIXED ANIMAL BLINKING ---
class Animal(pygame.sprite.Sprite):
    def __init__(self, x, y, animal_type):
        super().__init__()
        self.animal_type = animal_type
        filename = f"{animal_type}_animation_with_shadow.png"
        
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.direction = "down"
        self.frame_index = 0
        self.animation_speed = 0.15
        self.move_timer = random.randint(0, 60)
        
        # Babies walk slightly slower than adults
        self.speed = 0.3 if animal_type in ["Chick", "Calf", "Lamb"] else 0.5 
        
        self.animations = {}
        try:
            self.sprite_sheet = pygame.image.load(os.path.join(ASSET_DIR, filename)).convert_alpha()
            self.load_animations()
            self.image = self.animations["walk_down"][0]
            self.rect = self.image.get_rect(topleft=(x, y))
        except Exception as e:
            print(f"Failed to load animal: {filename}")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((200, 150, 150)) 
            self.rect = self.image.get_rect(topleft=(x, y))
            self.animations = None

    def load_animations(self):
        sheet_w = self.sprite_sheet.get_width()
        sheet_h = self.sprite_sheet.get_height()
        
        # Calculate exactly how big one frame is (6 columns, 8 rows)
        SPRITE_WIDTH = sheet_w // 6
        SPRITE_HEIGHT = sheet_h // 8
        
        # --- THE FIX: The walking animations only have 4 frames drawn! ---
        # By telling it to slice exactly 4 frames instead of 6, 
        # it skips the empty/transparent spaces at the end of the row.
        self.animations["walk_down"]  = self.get_row_images(4, 4, SPRITE_WIDTH, SPRITE_HEIGHT)
        self.animations["walk_up"]    = self.get_row_images(5, 4, SPRITE_WIDTH, SPRITE_HEIGHT)
        self.animations["walk_left"]  = self.get_row_images(6, 4, SPRITE_WIDTH, SPRITE_HEIGHT)
        self.animations["walk_right"] = self.get_row_images(7, 4, SPRITE_WIDTH, SPRITE_HEIGHT)

    def get_row_images(self, row, count, sprite_w, sprite_h):
        images = []
        
        scale_factor = TILE_SIZE / 32.0 
        scaled_w = int(sprite_w * scale_factor)
        scaled_h = int(sprite_h * scale_factor)
        
        for col in range(count):
            x = col * sprite_w
            y = row * sprite_h
            rect = pygame.Rect(x, y, sprite_w, sprite_h)
            try:
                img = self.sprite_sheet.subsurface(rect)
                images.append(pygame.transform.scale(img, (scaled_w, scaled_h)))
            except:
                pass
        return images if images else [pygame.Surface((TILE_SIZE, TILE_SIZE))]

    def update(self, walls):
        self.move_timer -= 1
        
        if self.move_timer <= 0:
            self.move_timer = random.randint(30, 120)
            self.direction = random.choice(["up", "down", "left", "right", "idle", "idle"])
        
        dx, dy = 0, 0
        if self.direction == "up": dy = -self.speed
        elif self.direction == "down": dy = self.speed
        elif self.direction == "left": dx = -self.speed
        elif self.direction == "right": dx = self.speed

        self.pos_x += dx
        self.rect.x = int(self.pos_x)
        if pygame.sprite.spritecollideany(self, walls):
            self.pos_x -= dx
            self.rect.x = int(self.pos_x)
            self.direction = random.choice(["up", "down", "left", "right"]) 
            
        self.pos_y += dy
        self.rect.y = int(self.pos_y)
        if pygame.sprite.spritecollideany(self, walls):
            self.pos_y -= dy
            self.rect.y = int(self.pos_y)
            self.direction = random.choice(["up", "down", "left", "right"]) 

        if self.animations:
            anim_key = f"walk_{self.direction}" if self.direction != "idle" else "walk_down"
            if anim_key in self.animations:
                self.frame_index += self.animation_speed
                if self.frame_index >= len(self.animations[anim_key]):
                    self.frame_index = 0
                self.image = self.animations[anim_key][int(self.frame_index)]