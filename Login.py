import pygame
from Input_Box import InputBox
from Button import Button
from tcp_by_size import send_with_size,recv_by_size

class Login:
    def __init__(self,sock):
        self.sock = sock
        self.screen = pygame.display.set_mode((1000,700))
        self.input_name = InputBox(350,70,100,40,text='UserName')
        self.input_pass = InputBox(350,130,100,40,text='Password')
        self.button_enter = Button(self.screen,(450,200,100,50),'LogIn')
        self.finish = True
        self.username = ''
        self.password = ''

    def show_login(self):
        self.screen.fill((255,0,0))
        self.input_name.draw(self.screen)
        self.input_pass.draw(self.screen)
        self.button_enter.draw()
        pygame.display.update()

    def main_loop(self):
        while self.finish:
            events = pygame.event.get()
            for event in events:
                self.input_name.handle_event(event,max_char=10)
                self.input_pass.handle_event(event,max_char=10)
            self.username = self.input_name.get_text()
            self.password = self.input_pass.get_text()
            self.show_login()

            if self.button_enter.is_button_pressed(events):
                print(f'name: {self.username}\npassword: {self.password}')
                self.finish = False


    def send(self):
        send_with_size(self.sock,'LGN~')
a = Login()
a.show_login()
a.main_loop()
