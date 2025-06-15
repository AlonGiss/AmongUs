import pickle
import socket
import threading

import pygame

from cryptography.hazmat.primitives import serialization

FONT = None
from Input_Box import InputBox
from Button import Button
from tcp_by_size import send_with_size, recv_by_size
from CryptoUtils import derive_AES_key, send_with_AES, recv_with_AES
DEBUG = True

class Login:
    def __init__(self, sock):
        self.sock = sock
        self.screen = pygame.display.set_mode((1000, 700))
        self.input_name = InputBox(350, 70, 100, 40, text='UserName')
        self.input_pass = InputBox(350, 130, 100, 40, text='PASSWORD',font='PASSWORD',)
        self.button_login = Button(self.screen, (450, 200, 100, 50), 'LogIn',color_back=(50,50,255,10))
        self.button_signin = Button(self.screen, (450, 260, 100, 50), 'SignIn',color_back=(50,50,255,10))
        self.show_pass = Button(self.screen, (700, 130, 130, 50), 'Show Password',font_size=26,color_back=(50,50,255,10))
        self.background = pygame.transform.scale(pygame.image.load('assets/Images/UI/AmongUs_background.jpg'),(1000,700))
        self.finish = True
        self.username = ''
        self.password = ''
        self.error = ''
        self.shared_key = None
        self.priv_client = None
        self.pub_client = None
        self.t = threading.Thread(target=self.DP)
        self.t.start()

    def waiting_room(self):
        i = 0
        while self.shared_key == None:
            self.screen.fill((0,0,0))
            self.show_text('Waiting' + ('.' * (i % 3)), 400, 340, 'Green')
            pygame.display.update()
            i +=1

    def show_login(self):
        self.waiting_room()
        self.t.join()
        self.screen.blit(self.background,(0,0))
        self.input_name.draw(self.screen)
        self.input_pass.draw(self.screen)
        self.button_login.draw()
        self.button_signin.draw()
        self.show_pass.draw()
        if self.error:
            self.show_text(self.error,375,180,'RED')
        pygame.display.update()

    def show_text(self,text,x,y,color='WHITE'):
        font = pygame.font.Font(FONT, 25)
        super_texto = font.render(text, True, color)
        self.screen.blit(super_texto, (x,y))

    def main_loop(self):
        while self.finish:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                self.input_name.handle_event(event, max_char=10)
                self.input_pass.handle_event(event, max_char=10)
            self.username = self.input_name.get_text()
            self.password = self.input_pass.get_text()
            self.show_login()

            if self.button_login.is_button_pressed(events):
                self.error = None
                if DEBUG:
                    print(f'name: {self.username}\npassword: {self.password}')

                send_with_AES(self.sock,f'LGIN~{self.username}~{self.password}',self.shared_key)
                self.recive_data()

            if self.button_signin.is_button_pressed(events):
                self.error = None
                send_with_AES(self.sock,f'SIGN~{self.username}~{self.password}',self.shared_key)
                self.recive_data()
                if self.error == None:
                    if DEBUG:
                        print(f'name: {self.username}\npassword: {self.password}')
                    send_with_AES(self.sock,f'LGIN~{self.username}~{self.password}',self.shared_key)
                    self.recive_data()

            if self.show_pass.is_button_pressed(events):
                self.input_pass.password = not self.input_pass.password

        self.screen.fill((0,0,0))
        self.show_text('Log In Succesfull',400,340,'Green')
        pygame.display.update()
        pygame.time.delay(3000)
        return self.username,self.password

    def recive_data(self):
        data = recv_with_AES(self.sock,self.shared_key)
        if data == b'':
            from error_screen import show_server_disconnection_error
            show_server_disconnection_error()

        if 'LOGS' in data:
            self.finish = False
        if 'ERRR' in data:
            self.error = data.split('~')[1]
        if 'SGSC' in data:
            return
        else:
            return

    def DP(self):
        from cryptography.hazmat.primitives.asymmetric import dh
        from cryptography.hazmat.backends import default_backend

        data = pickle.loads(recv_by_size(self.sock))
        p = data['p']
        g = data['g']
        server_pub_bytes = data['pub']

        params_numbers = dh.DHParameterNumbers(p, g)
        parameters = params_numbers.parameters(default_backend())

        self.priv_client = parameters.generate_private_key()
        self.pub_client = self.priv_client.public_key()

        client_pub_bytes = self.pub_client.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        send_with_size(self.sock, client_pub_bytes)

        server_pub_key = serialization.load_pem_public_key(server_pub_bytes, backend=default_backend())

        shared_key = self.priv_client.exchange(server_pub_key)
        self.shared_key = derive_AES_key(shared_key)
        if DEBUG:
            print(f'Shared Key: {shared_key.hex()}')

