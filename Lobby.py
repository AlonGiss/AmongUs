import sys
from Button import Button
import pygame
from Player import Player
from tcp_by_size import send_with_size,recv_by_size
import threading


MAP = "assets/Lobby.jpg"
MAP_MASK = 'assets/Lobby_Mask.jpg'
VISION_RADIUS = 200
DEBUG = False
FONT = None
SIZE_MAP = (547*1.5,578*1.5)
t = None
class Lobby:
    def __init__(self,sock,id,admin=False):
        pygame.init()
        self.id = id
        self.sock = sock
        self.color = self.recv_color()
        self.player = Player(self.color,500,500,admin=admin)
        self.game_start = False
        self.players = {self.player.color:self.player}
        self.screen = pygame.display.set_mode(SIZE_MAP)
        self.admin = admin
        if self.admin:
            self.start_button = Button(self.screen, (SIZE_MAP[0]//2-30,SIZE_MAP[1]-100,100,70), 'Start')
        self.map = None
        self.mask_map =None
        self.players_lock = threading.Lock()
        self.load_assets()
        self.draw_map()



    def main_lobby(self):
        global t
        try:
            t = threading.Thread(target=self.recive_data)
            t.start()
            move = True
            while not self.game_start:
                events = pygame.event.get()

                for event in events:
                    if event.type == pygame.QUIT:
                        self.exit()

                self.draw_map()
                self.start_game(events)
                if self.game_start:
                    break

                if move:
                    send_with_size(self.sock,f'LOCA~{self.player.color}~{self.player.x}~{self.player.y}~{self.player.direction}'.encode())
                    if DEBUG:
                        print(f'SEND: LOCA~{self.player.color}~{self.player.x}~{self.player.y}~{self.player.direction}')
                move = self.player.get_movement(self.mask_map)

                self.draw_players()
                pygame.display.flip()
                pygame.time.Clock().tick(60)

            t.join()
            pygame.quit()
            return self.player,self.players
        except Exception as err:
            print(f'ERROR0: {err}')
            self.exit()


    def load_assets(self):
        try:
            self.map = pygame.image.load(MAP).convert()
            self.map = pygame.transform.scale(self.map, SIZE_MAP)
            self.mask_map = pygame.image.load(MAP_MASK).convert()
            self.mask_map = pygame.transform.scale(self.mask_map, SIZE_MAP)
        except Exception as err:
            print(f'ERROR2: {err}')
            self.exit()


    def recive_data(self):
        try:
            while not self.game_start:
                data = recv_by_size(self.sock)
                if data == b'':
                    self.exit()

                data = data.decode()
                if DEBUG:
                    print(f'RECIVED: {data}')
                if 'COLO' in data:
                    self.color = data.split('~')[1]
                if 'LOCA' in data:
                    self.print_players(data)
                if 'STRG' == data:
                    self.game_start = True
                if 'GLOC' in data:
                    send_with_size(self.sock,f'LOCA~{self.player.color}~{self.player.x}~{self.player.y}~{self.player.direction}'.encode())

        except Exception as err:
            print(f'ERROR1: {err}')
            self.exit()

    def recv_color(self):
        try:
            while True:
                data = recv_by_size(self.sock)
                if data == b'':
                    self.exit()
                data = data.decode()
                if DEBUG:
                    print(f'RECIVED: {data}')
                if 'COLO' in data:
                    return data.split('~')[1]
        except Exception as err:
            print(f'ERROR3: {err}')
            self.exit()

    def print_players(self, data):
        try:
            location = data.split('~')[1:]
            with self.players_lock:
                for i in range(0, len(location), 4):
                    color, x, y,direction = location[i], int(location[i + 1]), int(location[i + 2]), location[i+3]
                    if color == self.player.color:
                        continue
                    if color not in self.players:
                        self.players[color] = Player(color, x, y)
                    else:
                        self.players[color].update_location(x, y,direction)
        except Exception as err:
            print(f'ERROR4: {err}')
            self.exit()


    def draw_players(self):
        try:
            with self.players_lock:
                for player in self.players.values():
                    self.screen.blit(player.image, (int(player.x), int(player.y)))
        except Exception as err:
            print(f'ERROR5: {err}')
            self.exit()


    def exit(self):
        global t
        if t:
            t.join()
        pygame.quit()
        sys.exit(0)


    def draw_map(self):
        try:
            self.screen.blit(self.map, (0, 0))
            self.show_text(f'LOBBY: {self.id}',SIZE_MAP[0]//2-60,100,)
            if self.admin:
                self.start_button.draw()

        except Exception as err:
            print(f'ERROR6: {err}')
            self.exit()

    def show_text(self,text,x,y,color='WHITE'):
        font = pygame.font.SysFont(FONT, 25)
        super_texto = font.render(text, True, color)
        self.screen.blit(super_texto, (x,y))

    def start_game(self,events):
        if self.admin:
            if self.start_button.is_button_pressed(events) and len(self.players) > 0:
                self.game_start = True
                send_with_size(self.sock,f'STRT~{self.id}'.encode())
