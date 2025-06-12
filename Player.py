import time

import pygame


PLAYER_SIZE = (76*0.8,91*0.8)
SPEED = 3
class Player:
    def __init__(self,color, x, y,alive=True,admin = False):
        self.color = color
        self.x = x
        self.y = y
        self.last_x = x
        self.last_y = y
        self.direction = "down"
        self.frame = 1
        self.image = f'assets/player_images/{self.color}/{self.color.lower()}_{self.direction}_walk/step{self.frame}.png'
        self.alive = alive
        self.admin = admin
        self.update_image()


    def update_image(self):
        if self.frame == 0:
            self.frame = 1
        path = f'assets/player_images/{self.color}/{self.color.lower()}_{self.direction}_walk/step{self.frame}.png'
        if not self.alive:
            path = rf'assets\player_images\{self.color}\{self.color.lower()}_ghost\step1_left.png'
        try:
            loaded_image = pygame.image.load(path).convert_alpha()  # <- convert to unlock and match display
            self.image = pygame.transform.scale(loaded_image, PLAYER_SIZE)
        except FileNotFoundError:
            print(f"Image not found: {path}")
            self.image = None


    def get_movement(self,mask_map):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            if keys[pygame.K_LEFT]:
                if not self.is_walkable_area(self.x-SPEED, self.y, mask_map):
                    return False
                self.update_location(self.x - SPEED, self.y,'left')
            elif keys[pygame.K_RIGHT]:
                if not self.is_walkable_area(self.x+ SPEED, self.y, mask_map):
                    return False
                self.update_location(self.x + SPEED, self.y,'right')
            if keys[pygame.K_UP]:
                if not self.is_walkable_area(self.x, self.y-SPEED, mask_map):
                   return False
                self.update_location(self.x, self.y-SPEED,'up')
            elif keys[pygame.K_DOWN]:
                if not self.is_walkable_area(self.x, self.y+SPEED, mask_map):
                   return False
                self.update_location(self.x, self.y+SPEED,'down')
            return True
        else:
            return False


    def update_location(self,newx,newy,direction):

        self.direction = direction
        self.x = newx
        self.y = newy
        self.frame += 1
        self.frame %= 18
        self.update_image()


    def is_walkable_pixel(self, x, y,mask_map):
        if x < 0 or y < 0 or x >= mask_map.get_width() or y >= mask_map.get_height():
            return False
        return mask_map.get_at((int(x), int(y))) == (255, 255, 255, 255)


    def is_walkable_area(self,dx, dy,mask_map):
        if not self.alive:
            return True
        for x in range(int(dx + 13), int(dx + 14)):
            for y in range(int(dy + 22), int(dy + 23)):
                if not self.is_walkable_pixel(x, y,mask_map):
                    return False
        return True


    def set_X_Y(self,x,y):
        self.x = x
        self.y = y


    def dead_body(self):
        self.alive = False
        path = f'assets/Images/DeadBodies/{self.color}_dead.jpg'
        try:
            loaded_image = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(loaded_image, PLAYER_SIZE)
        except FileNotFoundError:
            print(f"Image not found: {path}")
            self.image = None



    def check_near_dead_body(self, dead_bodies):
        """
        dead_bodies: list of (x, y)
        returns True if near any
        """
        if self.alive:
            for color,loc in dead_bodies.items():
                if self.distance(self.x, self.y, loc[0], loc[1]) < 50:
                    return color
            return None

    def distance(self, x1, y1, x2, y2):
        return ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5