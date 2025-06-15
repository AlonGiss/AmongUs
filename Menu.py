import sys

import pygame
from Input_Box import InputBox

from Button import Button
import random
from tcp_by_size import recv_by_size,send_with_size

FONT = r'assets\Fonts\AmongUsFont.ttf'
SIZE = (900,900)
BUTTON_SIZE = (SIZE[0]//4,SIZE[1]//11)
DEFAULT_WIDTH = SIZE[0] // 2 - BUTTON_SIZE[0]//2
DEFAULT_HEIGHT = (SIZE[1]//2)-BUTTON_SIZE[0]//2
class Menu:
    def __init__(self,sock):
        self.sock = sock
        self.screen = pygame.display.set_mode(SIZE)
        self.join_lobby_button = Button(self.screen,(DEFAULT_WIDTH,DEFAULT_HEIGHT+100,BUTTON_SIZE[0],BUTTON_SIZE[1]),'join lobby')
        self.create_lobby_button = Button(self.screen,(DEFAULT_WIDTH,DEFAULT_HEIGHT + 200,BUTTON_SIZE[0],BUTTON_SIZE[1]),'create lobbys')
        self.exit_button = Button(self.screen,(DEFAULT_WIDTH,DEFAULT_HEIGHT + 300,BUTTON_SIZE[0],BUTTON_SIZE[1]),'Exit')

    def buttons(self,events):
        if self.join_lobby_button.is_button_pressed(events):
            return self.join_lobby()
        if self.create_lobby_button.is_button_pressed(events):
            room =  self.random_room()
            print('CRTE~' + room)
            return 'CRTE~' + room
        if self.exit_button.is_button_pressed(events):
                self.exit()
                exit()
        return None

    def join_lobby(self):
        screen = self.screen
        prompt = 'Enter Lobby Code'
        pygame.font.init()
        font = pygame.font.Font(FONT, 36)
        input_box = InputBox(100, 100, 600, 50, font)

        clock = pygame.time.Clock()
        finished = False
        error = ''

        while not finished:
            rooms = self.get_rooms()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.exit()
                input_box.handle_event(event)

                if event.type == pygame.KEYDOWN and input_box.active:
                    if event.key == pygame.K_RETURN:
                        if len(input_box.get_text()) == 6:
                            if input_box.get_text() in rooms:
                                finished = True
                            else:
                                error = f'No Lobby: {input_box.get_text()}'
                        else:
                            error = 'Lobby Code must be 6 characters'

            screen.fill((30, 30, 30))

            prompt_surface = font.render(prompt, True, pygame.Color('gray'))
            screen.blit(prompt_surface, (input_box.rect.x, input_box.rect.y - 40))

            input_box.draw(screen)
            self.draw_rooms(rooms)

            if error:
                self.show_error(error)

            pygame.display.flip()
            clock.tick(30)

        return input_box.get_text()

    def exit(self):
        global t
        try:
            send_with_size(self.sock,b'DISS')
            print('diss')
        except:
            pass
        try:
            self.sock.close()
        except:
            pass


    def draw_rooms(self,rooms):
        x = 100
        y = 200
        for i in range(len(rooms)):
            self.show_text(f'ROOM {i+1}: {rooms[i]}' ,x,y,50,'BLUE',True)
            y += 60

    def show_title(self):

        font = pygame.font.Font(FONT, 100)
        super_texto = font.render('AMONG', True, 'BLUE')
        self.screen.blit(super_texto, (SIZE[0]//3-50, 100))

        font = pygame.font.Font(FONT, 100)
        super_texto = font.render('US', True, 'BLUE')
        self.screen.blit(super_texto, (SIZE[0]//3+200, 200))

    def show_error(self,err):

        font = pygame.font.Font(FONT, 25)
        super_text = font.render(err, True, 'RED')
        self.screen.blit(super_text, (SIZE[0]//3-25, 160))



    def draw_buttons(self):
        self.join_lobby_button.draw()
        self.create_lobby_button.draw()
        self.exit_button.draw()


    def start_menu(self):
        clock = pygame.time.Clock()

        while True:
            events = pygame.event.get()
            self.screen.fill((30, 30, 30))
            lobby = self.buttons(events)
            if lobby:
                return lobby

            self.draw_buttons()
            self.show_title()
            pygame.display.flip()
            clock.tick(60)

    def random_room(self):
        abc = 'ASDFGHJKLPOIUYTREWQZXCVBNMA'
        rooms = self.get_rooms()
        room = rooms[0]
        while room in rooms:
            room = ''
            for i in range(6):
                room += abc[random.randint(0, len(abc) - 1)]
        return room

    def get_rooms(self):
        rooms = []
        send_with_size(self.sock,b'GROM')
        while True:
            room = recv_by_size(self.sock)
            if room == b'finish' or room == b'':
                break
            rooms.append(room.decode())
        return rooms

    def show_text(self, text, x, y, size=25,color='WHITE', with_box=False):
        font = pygame.font.Font(FONT, size)
        super_texto = font.render(text, True, color)

        if with_box:
            text_rect = super_texto.get_rect(topleft=(x, y))
            pygame.draw.rect(self.screen, 'BLACK', text_rect.inflate(10, 6), border_radius=5)

        self.screen.blit(super_texto, (x, y))

