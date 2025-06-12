import time

import pygame


from Button import Button

FONT = None
IMG_ADRS = r'assets\Images\Tasks\FixWiring'
TASK_SIZE = (500,500)


class FixWiring:
    def __init__(self,screen= pygame.display.set_mode((500,500))):
        self.screen = screen
        exit_button_img = pygame.image.load(r'assets\Images\Tasks\close.PNG')
        self.exit_button = Button(screen,(215,430,65,65),'Exit','BLUE','White',exit_button_img)
        self.dragging_wire = False
        self.color_now = None
        self.red_pos = (80,120)
        self.blue_pos = (80,230)
        self.yellow_pos = (80,340)
        self.pink_pos = (80,450)
        self.red_pos_end = (420,120)
        self.blue_pos_end = (420,230)
        self.yellow_pos_end = (420,340)
        self.pink_pos_end = (420,450)
        self.pos = {'RED': self.red_pos,'PINK': self.pink_pos,'YELLOW': self.yellow_pos,'BLUE': self.blue_pos}
        self.pos_end = {'RED': self.red_pos_end,'PINK': self.pink_pos_end,'YELLOW': self.yellow_pos_end,'BLUE': self.blue_pos_end}
        self.finish = []


    def start_task_Fix_Wiring(self):
        task_img = self.load_assets()


        while True:
            if len(self.finish) == 4:
                self.show_text('WELL DONE', TASK_SIZE[0] // 2 - 120, 70, 'GREEN', 50)
                pygame.display.update()
                time.sleep(3)
                return True
            events = pygame.event.get()
            if self.exit_button.is_button_pressed(events):
                return False

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.new_line():
                        self.dragging_wire  = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.dragging_wire:
                        if abs(event.pos[0] - self.pos_end[self.color_now][0]) < 35 and abs(event.pos[1] - self.pos_end[self.color_now][1]) < 35:
                            self.finish.append(self.color_now)
                    self.dragging_wire  = False

                if event.type == pygame.MOUSEMOTION and self.dragging_wire:
                    self.draw_line(self.color_now)

            self.screen.blit(task_img,(0,0))

            for colorL in self.finish:
                pygame.draw.line(self.screen, colorL, self.pos[colorL], self.pos_end[colorL], 10)
            self.exit_button.draw()
            pygame.display.update()
        return False


    def new_line(self):
        mouse_x,mouse_y = pygame.mouse.get_pos()
        if abs(self.red_pos[0] - mouse_x) < 35 and abs(self.red_pos[1] - mouse_y) < 35:
            self.draw_line('RED')
            return True
        elif abs(self.yellow_pos[0] - mouse_x) < 35 and abs(self.yellow_pos[1] - mouse_y) < 35:
            self.draw_line('YELLOW')
            return True
        elif abs(self.blue_pos[0] - mouse_x) < 35 and abs(self.blue_pos[1] - mouse_y) < 35:
            self.draw_line('BLUE')
            return True
        elif abs(self.pink_pos[0] - mouse_x) < 35 and abs(self.pink_pos[1] - mouse_y) < 35:
            self.draw_line('PINK')
            return True
        self.dragging_wire = False
        return False

    def draw_line(self,color):
        mouse_x,mouse_y = pygame.mouse.get_pos()
        self.color_now = color
        pygame.draw.line(self.screen,color,self.pos[color],(mouse_x,mouse_y),10)


        pygame.display.update()

    def load_assets(self):
        task_img = pygame.image.load(IMG_ADRS + r'\electricity_wire_base1.png')
        return task_img



    def show_text(self, text, x, y, color='WHITE', size=25):
        font = pygame.font.SysFont(None, size)
        super_texto = font.render(text, True, color)
        self.screen.blit(super_texto, (x, y))
