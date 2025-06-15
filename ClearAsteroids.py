import pygame
import random
from Button import Button
import time
FONT = r'assets\Fonts\AmongUsFont.ttf'
IMG_ADRS = r'assets\Images\Tasks\ClearAsteroids'
TASK_SIZE = (500,500)


class ClearAsteroids:
    def __init__(self,screen= pygame.display.set_mode((500,500))):
        self.screen = screen
        exit_button_img = pygame.image.load(r'assets\Images\Tasks\close.PNG')
        self.exit_button = Button(screen,(215,430,65,65),'Exit','BLUE','White',exit_button_img)


    def start_task_Clear_Asteroid(self):
        task_img, asteroid_img, target_img = self.load_assets()
        task_img_dest = (0, 0)
        asteroid_img_dest = self.set_random_location_asteroid()
        asteroid_count = 3
        target_loc = (500,500)
        while asteroid_count > 0:
            events = pygame.event.get()
            if self.exit_button.is_button_pressed(events):
                return False

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.destroy_asteroid(event.pos,asteroid_img_dest):
                        asteroid_count -= 1
                        if asteroid_count <= 0:
                            break
                        asteroid_img_dest = self.set_random_location_asteroid()

            self.screen.blit(task_img,task_img_dest)
            self.screen.blit(asteroid_img, asteroid_img_dest)

            if pygame.mouse.get_pos()[0] - 35< 500 or pygame.mouse.get_pos()[1] - 35 > 500:
                target_loc = pygame.mouse.get_pos()[0] - 35, pygame.mouse.get_pos()[1] - 35
            self.screen.blit(target_img,target_loc)
            self.exit_button.draw()
            pygame.display.update()

        self.show_text('WELL DONE', TASK_SIZE[0] // 2 - 150, 100, 'GREEN', 50)
        pygame.display.update()
        time.sleep(3)
        return True

    def show_text(self, text, x, y, color='WHITE', size=25):
        font = pygame.font.Font(None, size)
        super_texto = font.render(text, True, color)
        self.screen.blit(super_texto, (x, y))

    def set_random_location_asteroid(self):
        return (random.randint(50,450),random.randint(50,450))

    def destroy_asteroid(self,pos,asteroid_img_dest):
        target_x = pygame.mouse.get_pos()[0] - 35
        target_y = pygame.mouse.get_pos()[1] - 35
        asteroid_x = asteroid_img_dest[0]
        asteroid_y = asteroid_img_dest[1]

        if abs(target_x - asteroid_x) < 50 and abs(target_y - asteroid_y) < 50:
            return True

    def load_assets(self):
        task_img = pygame.image.load(IMG_ADRS + r'\weapons_base.png')
        asteroid_img = pygame.image.load(IMG_ADRS + r'\weapons_asteroid1.png')
        target_img = pygame.image.load(IMG_ADRS + r'\weapons_target.png')
        return task_img,asteroid_img,target_img


