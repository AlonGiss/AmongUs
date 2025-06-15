import socket
import threading
import traceback


from tcp_by_size import recv_by_size,send_with_size

from Input_Box import InputBox
from Button import Button
import pygame

FONT = r'assets\Fonts\AmongUsFont.ttf'
t = None
all_to_die = False
SIZE_MAP = (650,441)
SIZE = (1000,700)
RECT_SIZE = 263,44
DEBUG = True

class Meeting_Room:
    def __init__(self,screen,sock,room,player,players,admin=False):
        pygame.init()
        self.admin = admin
        self.screen = screen
        self.sock = sock
        self.room = room
        self.player = player
        self.players = players
        self.chat_Button = Button(self.screen,(750,90,50,48),image=pygame.transform.scale(pygame.image.load(r'assets/Images/Meeting/message_icon.png'),(50,48)))
        self.bye_background = pygame.transform.scale(pygame.image.load('assets/Images/UI/AmongUs_background.jpg'),(1000,700))
        self.Buttons = {}
        self.voted = None
        self.messages = {}
        self.counter = 0
        self.time_left = 180
        self.start_time = pygame.time.get_ticks()
        self.ending_time = False
        self.input_chat = InputBox(80,500,100,50, pygame.font.Font(None, 32))
        self.chat_open =False
        self.dead = False
        self.events = []
        self.had_voted = []
        self.votes = {}
        self.disconnected_colors= []

        if DEBUG:
            print("\n===== MEETING ROOM STATE =====")
            print(f"Admin: {self.admin}")
            print(f"Room: {self.room}")
            print(f"Player: {self.player.color}")
            print(f"Players: {[p.color for p in self.players.values()]}")
            print(f"Voted (self): {self.voted}")
            print(f"Had voted: {self.had_voted}")
            print(f"Votes: {self.votes}")
            print(f"Messages count: {len(self.messages)}")
            print(f"Chat open: {self.chat_open}")
            print(f"Time left: {self.time_left}")
            print(f"Start time (ms): {self.start_time}")
            print(f"Ending time triggered: {self.ending_time}")
            print(f"Button count: {len(self.Buttons)}")
            print("================================\n")

        self.draw()
        self.main_loop()




    def main_loop(self):
        try:
            global t,all_to_die

            t = threading.Thread(target=self.recive_data,)
            t.start()
            self.screen.fill((0,0,0))
            self.draw()

            while (len(self.had_voted) != self.are_alive()) and not self.ending_time:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        print('EXIT')
                        self.end_meeting()
                        self.exit()
                        exit()

                if self.chat_open:
                    self.chat(events)
                else:
                    for color,button in self.Buttons.items():
                        if self.player.alive and button.is_button_pressed(events)and self.player.color not in self.had_voted:
                            self.voted = color
                            send_with_size(self.sock,f'VOTE~{self.room}~{self.voted}~{self.player.color}'.encode())
                            print(self.voted)
                            voted_img = pygame.image.load(r'assets\Images\Meeting\i_voted.png')
                            self.draw_without_buttons()
                            self.screen.blit(voted_img,button.dist)
                            pygame.display.update()
                            break


                if self.chat_Button.is_button_pressed(events):
                    self.chat_open = not self.chat_open
                    if not self.chat_open:
                        self.draw()


                self.ending_time = self.show_time()
                self.chat_Button.draw()
                #print(self.votes)
                pygame.display.update()
                #pygame.display.flip()

            all_to_die = True
            max_voted = max(self.votes, key=self.votes.get)
            self.voted_anim(max_voted)
            if self.admin:
                send_with_size(self.sock,f'SUVT~{self.room}~{max_voted}'.encode())
                print(f'SEND: SUVT~{self.room}~{max_voted}')

            print('END')
            pygame.time.delay(3000)
            self.end_meeting()



        except pygame.error as err:
            print(f'ERRar: {err}')
            self.end_meeting()
            self.exit()

        except Exception as err:
            print(f'ERRar: {err}')
            self.end_meeting()
            self.exit()

    def are_alive(self):
        cnt = 0
        for color,player in self.players.items():
            if player.alive:
                cnt +=1
        return cnt

    def voted_anim(self,color):
        self.screen.blit(self.bye_background,(0,0))
        self.show_text(f'{color} Has Been Eliminated',SIZE[0]//2-70,SIZE[1]//2-20,color)
        pygame.display.update()

    def recive_data(self):
        try:
            self.sock.settimeout(0.1)
            while not all_to_die:
                try:
                    print('hello')
                    data = recv_by_size(self.sock)
                    if data == b'':
                        from error_screen import show_server_disconnection_error
                        show_server_disconnection_error()
                    data = data.decode()

                    if DEBUG:
                        print(f'DA RE: {data}')
                    if 'NVTE' in data:
                        self.has_voted(data)
                    elif 'GMSG' in data:
                        self.recive_message(data)
                    elif 'DESS' in data:
                        self.disconnect(data)
                    elif 'DEAD' in data:
                        self.dead = True

                except socket.timeout:
                    continue
            self.sock.settimeout(None)
        except Exception as err:
            print(f'ERA: {err}')
            traceback.print_exc()
            self.end_meeting()


    def disconnect(self,data):
        color = data.split('~')[1]
        self.disconnected_colors.append(color)
        if color in self.players:
            del self.players[color]
            print(f'{color} disconnected and removed from meeting.')
        self.draw()


    def recive_message(self,data):
        data = data.split('~')
        color_msg = data[1]
        msg = data[2]
        if color_msg != self.player.color:
            self.messages[self.counter] = {color_msg: msg}
            self.counter +=1

    def has_voted(self,data):
        data = data.split('~')
        self.had_voted.append(data[2])
        color = data[1]
        if color in self.votes:
            self.votes[color] += 1
        else:
            self.votes[color] = 1

    def chat(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.end_meeting()
                self.exit()

            self.input_chat.handle_event(event,25)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                msg = self.input_chat.get_text().strip()
                if msg:
                    self.messages[self.counter] = {self.player.color: msg}
                    send_with_size(self.sock,f'SMSG~{self.room}~{self.player.color}~{msg}')
                    self.counter += 1
                    self.input_chat.text = ''
                    self.input_chat.txt_surface = self.input_chat.font.render('', True, pygame.Color('blue'))

        self.draw_chat()
        loca = [100, 100]
        for i in sorted(self.messages.keys()):
            message_color = self.messages[i]
            for color, message in message_color.items():
                self.show_message(message, color, tuple(loca))
            loca[1] += RECT_SIZE[1] * 1.5 + 20

        self.input_chat.draw(self.screen)

    def show_message(self,message,color,loca):
        self.draw_rect_player(self.players[color],loca)
        self.show_text(message,loca[0]+75,loca[1]+25,color='Black')

    def exit(self):
        global t,all_to_die
        all_to_die = True
        try:
            send_with_size(self.sock,b'DISS')
        except:
            pass
        try:
            self.sock.close()
        except:
            pass
        if t and threading.current_thread() != t:
            t.join()
        from error_screen import show_server_disconnection_error
        show_server_disconnection_error()

    def draw_chat(self):
        chat_img = pygame.image.load(r'assets/Images/Meeting/chat_img.png').convert_alpha()
        chat_img = pygame.transform.scale(chat_img,(SIZE[0],SIZE[1]))
        self.screen.blit(chat_img,(-100,15))



    def draw_map(self):
        img = r'assets\Images\Meeting\e_vote_base.png'
        map_img = pygame.image.load(img)
        map_img = pygame.transform.scale(map_img,SIZE)
        self.screen.fill((0,0,0))
        self.screen.blit(map_img,(0,0))


    def draw(self):
        self.draw_map()
        loc = [70,150]
        for player in self.players.values():
            self.draw_rect_player(player,tuple(loc))
            loc[1] += RECT_SIZE[1] * 1.5 + 20
            if loc[1] > 500:
                loc[0] += 400
                loc[1] = 150
        if self.player.alive:
            self.draw_buttons()
        pygame.display.update()

    def draw_without_buttons(self):
        self.draw_map()
        loc = [70,150]
        for player in self.players.values():
            self.draw_rect_player(player,tuple(loc))
            loc[1] += RECT_SIZE[1] * 1.5 + 20
            if loc[1] > 500:
                loc[0] += 400
                loc[1] = 150
        pygame.display.update()


    def draw_rect_player(self,player,loc):
        try:
            rect_player = r'assets\Images\Meeting\rect_player.png'
            if not player.alive:
                rect_player = r'assets\Images\Meeting\rect_player_dead.png'
            img = pygame.image.load(rect_player)
            img = pygame.transform.scale(img,(RECT_SIZE[0]*1.5,RECT_SIZE[1]*1.5))
            player_img = pygame.image.load(rf"assets\player_images\{player.color}\{player.color.lower()}_down_walk\step1.png")
            player_img = pygame.transform.scale(player_img,(37,48))
            self.screen.blit(img,loc)
            self.screen.blit(player_img,(loc[0]+10,loc[1]+ 10))
        except Exception as err:
            print(err)


    def draw_buttons(self):
        img = r"assets\Images\Meeting\select_vote.png"
        img_vote = pygame.image.load(img)
        BUTTON_SIZE = [370,165,img_vote.get_width(),img_vote.get_height()]
        for player in self.players.values():
            if player.alive:
                b= Button(self.screen,tuple(BUTTON_SIZE),image=img_vote)
                self.Buttons[player.color] = b
                b.draw()
            BUTTON_SIZE[1] += RECT_SIZE[1] * 1.5 + 20
            if BUTTON_SIZE[1] > 550:
                BUTTON_SIZE[1] = 165
                BUTTON_SIZE[0] += 370

    def show_text(self,text,x,y,color='WHITE'):
        font = pygame.font.Font(FONT, 25)
        super_texto = font.render(text, True, color)
        self.screen.blit(super_texto, (x,y))

    def show_time(self):
        loca_x = 700
        loca_y = 620
        time = (pygame.time.get_ticks() - self.start_time) // 1000
        time_left = max(0, self.time_left - time)

        time_rect = pygame.Rect(loca_x-10, loca_y-10, 200, 30)
        pygame.draw.rect(self.screen, (200, 210, 250), time_rect)

        text = f'Voting Ends In: {time_left}'
        self.show_text(text, loca_x, loca_y,'BLACK')

        return time_left == 0

    def end_meeting(self):
        global all_to_die
        all_to_die = True
        for dis in self.disconnected_colors:
            send_with_size(self.sock,f'DESS~{dis}')
