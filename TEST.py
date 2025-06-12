import threading
import traceback
import pygame
import sys

from tcp_by_size import send_with_size, recv_by_size
from Input_Box import InputBox
from Button import Button
from Imposter_Crewmate import Imposter
from Player import Player

FONT = None
DEBUG = True
SIZE_MAP = (1000, 700)
SIZE = (1000, 700)
RECT_SIZE = (263, 44)
MAP = "assets/map/map.jpg"
MAP_MASK = 'assets/map/mask.jpg'
ZOOM = 4
START_LOCA = (557, 168)

class Game:
    def __init__(self, sock, room_id, player):
        pygame.init()
        self.sock = sock
        self.room = room_id
        self.player = player
        self.player.set_X_Y(*START_LOCA)
        self.players = {self.player.color: self.player}
        self.screen = pygame.display.set_mode(SIZE_MAP)
        self.map = None
        self.mask_map = None
        self.rol = None
        self.game = True
        self.stop_meeting = False
        self.cam_x = self.cam_y = None
        self.players_lock = threading.Lock()
        self.events = []
        self.imposter = Imposter(self.screen)
        self.input_chat = InputBox(80, 500, 100, 50, pygame.font.Font(None, 32))
        self.chat_Button = Button(self.screen, (750, 90, 50, 48), image=pygame.transform.scale(pygame.image.load(r'assets/Images/Meeting/message_icon.png'), (50, 48)))
        self.chat_open = True
        self.messages = {}
        self.counter = 0
        self.Buttons = {}
        self.had_voted = []
        self.votes = {}
        self.voted = None
        self.time_left = 180
        self.start_time = pygame.time.get_ticks()
        self.ending_time = False

        if DEBUG:
            print(f'\n--------\nroom: {self.room}\ncolor: {self.player.color}\n------------\n')

        self.load_assets()
        self.main_game_loop()

    def load_assets(self):
        self.map = pygame.transform.scale(pygame.image.load(MAP).convert(), SIZE_MAP)
        self.mask_map = pygame.transform.scale(pygame.image.load(MAP_MASK).convert(), SIZE_MAP)

    def main_game_loop(self):
        threading.Thread(target=self.receive_data).start()
        self.wait_for_role()

        while self.game:
            if not self.stop_meeting:
                self.events = pygame.event.get()
                keys = pygame.key.get_pressed()

                if keys[pygame.K_1]:
                    send_with_size(self.sock, f'EMRG~{self.room}'.encode())

                for event in self.events:
                    if event.type == pygame.QUIT:
                        self.exit_game()

                self.draw_zoomed_map()
                self.send_location()
                self.player.get_movement(self.mask_map)
                self.draw_players()

                if self.rol == 'IMPOSTER':
                    self.imposter.show_button()
                    self.kill_player(self.events)

                pygame.display.flip()
                pygame.time.Clock().tick(60)

    def wait_for_role(self):
        send_with_size(self.sock, f'GROL~{self.room}~{self.player.color}'.encode())
        while not self.rol:
            pygame.time.delay(100)
        img = pygame.image.load(f'assets/Images/Rol/{self.rol[0] + self.rol[1:].lower()}.jpg')
        self.screen.blit(pygame.transform.scale(img, SIZE_MAP), (0, 0))
        pygame.display.update()
        pygame.time.delay(3000)

    def receive_data(self):
        try:
            while self.game:
                data = recv_by_size(self.sock).decode()
                if 'RROL' in data:
                    self.rol = data.split('~')[1]
                elif 'LOCA' in data:
                    self.update_players(data)
                elif data == 'DEAD':
                    self.animate_death()
                elif 'EMRG' in data:
                    self.start_meeting()
                elif 'NVTE' in data:
                    self.receive_vote_data(data)
                elif 'GMSG' in data:
                    self.receive_chat_message(data)
        except:
            traceback.print_exc()
            self.exit_game()

    def update_players(self, data):
        location = data.split('~')[1:]
        with self.players_lock:
            for i in range(0, len(location), 5):
                color, x, y, direction, alive = location[i], int(location[i+1]), int(location[i+2]), location[i+3], location[i+4] == 'True'
                if color == self.player.color:
                    continue
                if color not in self.players:
                    self.players[color] = Player(color, x, y, alive)
                else:
                    if not alive:
                        self.players[color].dead_body()
                    self.players[color].update_location(x, y, direction)

    def send_location(self):
        msg = f'LOCA~{self.player.color}~{self.player.x}~{self.player.y}~{self.player.direction}~{self.player.alive}'
        send_with_size(self.sock, msg.encode())

    def start_meeting(self):
        self.stop_meeting = True
        self.draw_meeting_screen()
        self.handle_meeting_loop()
        self.stop_meeting = False

    def handle_meeting_loop(self):
        self.start_time = pygame.time.get_ticks()
        while len(self.had_voted) != len(self.players) and not self.ending_time:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.exit_game()
            if self.chat_open:
                self.handle_chat(events)
            else:
                for color, button in self.Buttons.items():
                    if button.is_button_pressed(events) and self.player.color not in self.had_voted:
                        self.voted = color
                        send_with_size(self.sock, f'VOTE~{self.room}~{self.voted}~{self.player.color}'.encode())
            if self.chat_Button.is_button_pressed(events):
                self.chat_open = not self.chat_open
            self.ending_time = self.show_timer()
            self.chat_Button.draw()
            pygame.display.update()

        if self.rol == 'ADMIN':
            max_voted = max(self.votes, key=self.votes.get)
            send_with_size(self.sock, f'SUVT~{self.room}~{max_voted}'.encode())
        pygame.time.delay(3000)

    def receive_vote_data(self, data):
        _, color, voter = data.split('~')
        self.had_voted.append(voter)
        self.votes[color] = self.votes.get(color, 0) + 1

    def receive_chat_message(self, data):
        _, color, msg = data.split('~')
        if color != self.player.color:
            self.messages[self.counter] = {color: msg}
            self.counter += 1

    def handle_chat(self, events):
        for event in events:
            self.input_chat.handle_event(event, 25)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                msg = self.input_chat.get_text().strip()
                if msg:
                    self.messages[self.counter] = {self.player.color: msg}
                    send_with_size(self.sock, f'SMSG~{self.room}~{self.player.color}~{msg}')
                    self.counter += 1
                    self.input_chat.text = ''
        self.draw_chat_interface()

    def draw_chat_interface(self):
        self.screen.fill((0, 0, 0))
        loc = [100, 100]
        for i in sorted(self.messages):
            for color, message in self.messages[i].items():
                self.draw_text(f"{color}: {message}", loc[0], loc[1], 'WHITE')
                loc[1] += 30
        self.input_chat.draw(self.screen)

    def draw_meeting_screen(self):
        self.screen.fill((0, 0, 0))
        loc = [70, 150]
        for player in self.players.values():
            self.draw_text(player.color, loc[0], loc[1], 'WHITE')
            loc[1] += 60
        pygame.display.update()

    def show_timer(self):
        elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
        time_left = max(0, self.time_left - elapsed)
        self.draw_text(f'Voting Ends In: {time_left}', 700, 620, 'BLACK')
        return time_left == 0

    def kill_player(self, events):
        if self.imposter.kill(events):
            dead = self.find_closest_player()
            if dead:
                send_with_size(self.sock, f'KILL~{self.room}~{dead}'.encode())

    def find_closest_player(self):
        closest = None
        min_dist = float('inf')
        for color, player in self.players.items():
            if color == self.player.color or not player.alive:
                continue
            dx, dy = player.x - self.player.x, player.y - self.player.y
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < min_dist and dist < 35:
                min_dist, closest = dist, color
        return closest

    def animate_death(self):
        self.player.dead_body()
        for i in range(1, 19):
            img = pygame.image.load(f"assets/Images/Alerts/kill{i}.png")
            self.screen.blit(img, (0, 0))
            pygame.display.update()
            pygame.time.delay(100)

    def draw_players(self):
        for player in self.players.values():
            draw_x = int((player.x - self.cam_x) * ZOOM)
            draw_y = int((player.y - self.cam_y) * ZOOM)
            self.screen.blit(player.image, (draw_x, draw_y))

    def draw_zoomed_map(self):
        cam_w, cam_h = SIZE_MAP[0] // ZOOM, SIZE_MAP[1] // ZOOM
        self.cam_x = max(0, min(self.player.x - cam_w // 2, self.map.get_width() - cam_w))
        self.cam_y = max(0, min(self.player.y - cam_h // 2, self.map.get_height() - cam_h))
        camera_rect = pygame.Rect(self.cam_x, self.cam_y, cam_w, cam_h)
        view = self.map.subsurface(camera_rect)
        self.screen.blit(pygame.transform.scale(view, SIZE_MAP), (0, 0))

    def draw_text(self, text, x, y, color='WHITE'):
        font = pygame.font.SysFont(FONT, 25)
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def exit_game(self):
        pygame.quit()
        sys.exit(0)
