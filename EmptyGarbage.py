import time

import pygame
import random
from Button import Button

FONT = None
IMG_ADRS = r'assets\Images\Tasks\EmptyGarbage'
TASK_SIZE = (500,500)


class EmptyGarbage:
    def __init__(self,screen= pygame.display.set_mode((500,500))):
        self.screen = screen
        exit_button_img = pygame.image.load(r'assets\Images\Tasks\close.PNG')
        self.exit_button = Button(screen,(215,430,65,65),'Exit','BLUE','White',exit_button_img)

    def start_task_Empty_Garbage(self):
        task_img,task_img_full,liver_up = self.load_assets()


        while True:
            events = pygame.event.get()
            if self.exit_button.is_button_pressed(events):
                return False

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if abs(pygame.mouse.get_pos()[0] - 375) < 70 and abs(pygame.mouse.get_pos()[1] - 200) < 70:
                        self.Go_Down()
                        return True


            self.screen.blit(task_img,(0,0))
            self.screen.blit(task_img_full ,(0,0))
            self.screen.blit(liver_up, (375,200))
            self.exit_button.draw()
            pygame.display.update()
        return True



    def load_assets(self):
        task_img = pygame.image.load(IMG_ADRS + r'\gb3.png')
        task_img_full = pygame.image.load(IMG_ADRS + r'\garbage_base_full.png')
        liver_up = pygame.image.load(IMG_ADRS + r'\liver_up.png')

        return task_img,task_img_full,liver_up


    def Go_Down(self):
        liver_down = pygame.image.load(IMG_ADRS + r'\liver_down.png')
        img = pygame.image.load(IMG_ADRS + r'\garbage_base_full.png')
        img2 = pygame.image.load(IMG_ADRS + r'\gb3.png')
        self.screen.blit(img2,(0,0))
        cnt = 0
        while cnt < 500:

            self.screen.blit(img2, (0, 0))
            self.screen.blit(img,(0,cnt))
            self.screen.blit(liver_down, (375, 200))
            self.show_text('WELL DONE', TASK_SIZE[0] // 2 - 150, 100, 'GREEN', 50)
            cnt+=3
            time.sleep(0.001)
            pygame.display.update()

    def show_text(self, text, x, y, color='WHITE', size=25):
        font = pygame.font.SysFont(None, size)
        super_texto = font.render(text, True, color)
        self.screen.blit(super_texto, (x, y))

