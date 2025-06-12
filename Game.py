import socket
import sys
import pygame
from pygame.examples.music_drop_fade import play_file

from Button import Button
from Imposter_Crewmate import Imposter,Crewmate
from Player import Player
from tcp_by_size import send_with_size,recv_by_size
import threading
from Meeting_Room import Meeting_Room

MAP = "assets/map/map.jpg"
MAP_MASK = 'assets/map/mask.jpg'
VISION_RADIUS = 200
DEBUG = True
FONT = None
SIZE = (3000,1500)
SIZE_MAP = (1000,700)
t = None
ZOOM = 4
START_LOCA = (557,168)

class Game:
    def __init__(self,sock,id,player):
        pygame.init()
        self.id = id
        self.sock = sock
        self.player = player
        player.set_X_Y(START_LOCA[0],START_LOCA[1])
        self.game = True
        self.players = {self.player.color:self.player}
        self.tasks = 0
        self.screen = pygame.display.set_mode(SIZE_MAP)
        self.dead_bodies_loc = {}
        self.report_button_a = Button(self.screen, (750, 600, 83, 82),image=pygame.image.load(r'assets/Images/UI/report_button.png'))
        self.emergency_button1 = Button(self.screen,(880, 510, 83, 82),image=pygame.image.load(r'assets/Images/UI/emergency_icon.png'))
        self.report_button = False
        self.map = None
        self.mask_map =None
        self.rol = None
        self.events = []
        self.stop_metting = False
        self.imposter = Imposter(self.screen)
        self.crewmate = Crewmate(self.screen,self.player)
        self.meeting = None
        self.has_won = None
        self.cam_x,self.cam_y = None,None
        self.players_lock = threading.Lock()
        if DEBUG:
            print(f'\n--------\nroom: {self.id}\ncolor: {self.player.color}\n------------\n')
        self.load_assets()
        self.draw_map()
        self.main_game()


    def waiting_rol(self):
        send_with_size(self.sock,f'GROL~{self.id}~{self.player.color}'.encode())
        if DEBUG:
            print(f'WAITING ROL: GROL~{self.id}~{self.player.color}')
        while not self.rol:
            pygame.time.delay(100)


        img = rf'assets/Images/Rol/{self.rol[0] + (self.rol[1:]).lower()}.jpg'
        img = pygame.image.load(img)
        img = pygame.transform.scale(img, SIZE_MAP)
        self.screen.blit(img,(0,0))
        pygame.display.update()
        pygame.time.delay(3000)

    def get_rol(self,data):
        rol = data.split('~')[1]
        self.rol = rol

    def emergency_button(self,events):
        x,y = 557,158
        if self.player.distance(self.player.x,self.player.y,x,y) < 50:
            print('loc: ', self.player.distance(self.player.x, self.player.y, x, y))
            self.emergency_button1.draw()
            if self.emergency_button1.is_button_pressed(events):
                return True
        return False

    def main_game(self):
        global t
        try:
            t = threading.Thread(target=self.recive_data)
            t.start()
            move = True
            self.waiting_rol()

            while self.game:


                if not self.stop_metting:
                    self.events = pygame.event.get()
                    keys = pygame.key.get_pressed()

                    for event in self.events:
                        if event.type == pygame.QUIT:
                            self.exit()


                    self.draw_map2()

                    if self.emergency_button(self.events):
                        send_with_size(self.sock,f'EMRG~{self.id}'.encode())
                        print(f'EMRG~{self.id}')
                    try:
                        self.report_body()
                        if self.report_button:
                            self.report_button_a.draw()
                            if self.report_button_a.is_button_pressed(self.events):
                                send_with_size(self.sock, f'EMRG~{self.id}'.encode())
                                print(f'EMRG~{self.id}')
                    except Exception as err:
                        print(f'lalala: {err}')
                        continue

                    if not self.game:
                        break

                    if move:
                        send_loca = f'LOCA~{self.player.color}~{self.player.x}~{self.player.y}~{self.player.direction}~{self.player.alive}'
                        send_with_size(self.sock,send_loca.encode())
                        if DEBUG:
                            print(send_loca)
                    move = self.player.get_movement(self.mask_map)

                    self.draw_players()
                    if self.rol == 'IMPOSTER':
                        self.imposter.show_button()
                        self.kill(self.events)
                        self.draw_task_bar()
                        self.imposter.try_vent_jump(self.player)
                    else:
                        self.crewmate.total_tasks.show_tasks()
                        self.draw_task_bar()
                        self.crewmate.show_button()
                        if self.crewmate.button_presed(self.events):
                            task = self.crewmate.check_near_task()
                            if task:
                                if self.crewmate.do_task(task):
                                    send_with_size(self.sock,f'FTSK~{self.id}'.encode())

                else:
                    if not self.meeting:
                        self.meeting = Meeting_Room(self.screen, self.sock, self.id, self.player, self.players,admin=self.player.admin)

                    self.meeting = None
                    self.stop_metting = False

                pygame.display.flip()
                pygame.time.Clock().tick(60)

            self.has_won = self.win()
            print(f'WIN: {self.has_won}')
            t.join()
            pygame.quit()
            return self.player,self.players
        except Exception as err:
            print(f'ERROR10: {err}')
            self.exit()

    def kill(self,events):
        try:
            if self.imposter.kill(events):
                dead = self.find_closest_player()
                if dead:
                    send_with_size(self.sock,f'KILL~{self.id}~{dead}'.encode())
                    if DEBUG:
                        print(f'KILL~{self.id}~{dead}')
        except Exception as err:
            print('KILL ERR: ' + str(err))


    def find_closest_player(self):
        closest_player = None
        min_distance = float('inf')

        with self.players_lock:
            for color, player in self.players.items():
                if color == self.player.color:
                    continue  # Skip my player
                if not player.alive:
                    continue #if player is died

                dx = player.x - self.player.x
                dy = player.y - self.player.y
                distance = (dx ** 2 + dy ** 2) ** 0.5 #sqrt(((x1-x2)^2 + (y1-y2)^2))

                if distance < min_distance:
                    min_distance = distance
                    closest_player = color
        if min_distance < 35:
            return closest_player
        return None

    def win(self):
        alive = 0
        for color,player in self.players.items():
            if player.alive and self.player.color != color:
                alive+= 1
        if alive == 0:
            self.game = False
            return self.rol == 'IMPOSTER'
        elif not self.game:
            return self.rol != 'IMPOSTER'
        return None

    def load_assets(self):
        try:
            self.map = pygame.image.load(MAP).convert()
            self.map = pygame.transform.scale(self.map, SIZE_MAP)
            self.mask_map = pygame.image.load(MAP_MASK).convert()
            self.mask_map = pygame.transform.scale(self.mask_map, SIZE_MAP)
        except Exception as err:
            print(f'ERROR9: {err}')
            self.exit()

    def recive_data(self):
        try:
            while self.game:
                try:
                    if not self.stop_metting:
                        print(f'stop: {self.stop_metting}')
                        data = recv_by_size(self.sock)
                        data = data.decode()
                        if DEBUG:
                            print('RECV: ' + data)
                        if 'RROL' in data:
                            self.get_rol(data)
                        elif 'LOCA' in data:
                            self.update_players(data)
                        if data == 'DEAD':
                            self.dead()
                        if 'EMRG' in data:
                            self.emergency_meeting()
                        if 'ATSK' in data:
                            self.add_task()
                except socket.timeout:
                    continue

        except Exception as err:
            print(f'ERROR6: {err}')
            self.exit()

    def add_task(self):
        self.tasks += 1
        total_tasks = (len(self.players.values())-1) * 3
        percentage = self.tasks / total_tasks if total_tasks > 0 else 0
        print(f'percentage: {percentage}')
        if percentage == 1.0:
            self.game = False


    def draw_task_bar(self):
        total_tasks = (len(self.players.values()) - 1) * 3
        percentage = self.tasks / total_tasks if total_tasks > 0 else 0
        x = 10
        y = 10
        w = 200
        h =20
        outer_rect = pygame.Rect(h, y, w, h)
        pygame.draw.rect(self.screen, 'Black', outer_rect, 2)

        inner_bg_rect = pygame.Rect(x + 10, y + 2, w - 4, h - 4)
        pygame.draw.rect(self.screen, (50,50,50), inner_bg_rect)

        fill_width = (w - 4) * percentage
        fill_rect = pygame.Rect(x + 10, y + 2, fill_width, h - 4)
        pygame.draw.rect(self.screen, 'Green', fill_rect)


    def emergency_meeting(self):
        self.screen.fill((0,0,0))
        pygame.display.update()
        self.stop_metting = True

    def dead(self):
        self.player.dead_body()
        send_loca = f'LOCA~{self.player.color}~{self.player.x}~{self.player.y}~{self.player.direction}~{self.player.alive}'
        send_with_size(self.sock, send_loca.encode())
        self.anim_dead()

    def anim_dead(self):
        with self.players_lock:
            for i in range(1,19):
                path = rf"assets\Images\Alerts\kill{i}.png"
                img = pygame.image.load(path)
                self.screen.blit(img,(0,0))
                pygame.display.update()
                pygame.time.delay(100)

    def report_body(self):
        try:
            if self.player.check_near_dead_body(self.dead_bodies_loc) != None:
                self.report_button = True
            else:
                self.report_button = False
        except Exception as err:
            print(f'REP ERR: {err}')
    def update_players(self, data):
        try:
            location = data.split('~')[1:]
            with self.players_lock:
                for i in range(0, len(location), 5):
                    color, x, y,direction,alive = location[i], int(location[i + 1]), int(location[i + 2]), location[i+3],location[i+4]
                    if color == self.player.color:
                        continue
                    if color not in self.players:
                        self.players[color] = Player(color, x, y,(alive == 'True'))
                    else:
                        if alive == 'False' and self.players[color].alive:
                            self.players[color].dead_body()
                            self.dead_bodies_loc[color] = (x,y)

                        if alive == 'True' or not self.player.alive:
                            self.players[color].update_location(x, y,direction)
        except Exception as err:
            print(f'ERROR12: {err}')
            self.exit()

    def draw_players(self):
        try:
            with self.players_lock:
                for player in self.players.values():
                    draw_x = int(player.x - self.cam_x) * ZOOM
                    draw_y = int(player.y - self.cam_y) * ZOOM
                    if draw_x > 0 and draw_y > 0:
                        self.screen.blit(player.image, (draw_x, draw_y))
        except Exception as err:
            print(f'ERROR3: {err}')
            self.exit()


    def exit(self):
        global t
        if t and threading.current_thread() != t:
            t.join()
        pygame.quit()
        sys.exit(0)


    def draw_map(self):
        try:
            self.screen.blit(self.map, (0, 0))
        except Exception as err:
            print(f'ERROR: {err}')
            self.exit()

    def show_text(self,text,x,y,color='WHITE'):
        font = pygame.font.SysFont(FONT, 25)
        super_texto = font.render(text, True, color)
        self.screen.blit(super_texto, (x,y))

    def draw_map2(self):
        zoom = ZOOM
        cam_w, cam_h = SIZE_MAP[0] // zoom, SIZE_MAP[1] // zoom
        self.cam_x = max(0, min(self.player.x - cam_w // 2, self.map.get_width() - cam_w))
        self.cam_y = max(0, min(self.player.y - cam_h // 2, self.map.get_height() - cam_h))
        camera_rect = pygame.Rect(self.cam_x, self.cam_y, cam_w, cam_h)
        view = self.map.subsurface(camera_rect)
        view_scaled = pygame.transform.scale(view, (SIZE_MAP[0], SIZE_MAP[1]))
        self.screen.blit(view_scaled, (0, 0))




















