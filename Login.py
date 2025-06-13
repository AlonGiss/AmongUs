import socket
import threading

import pygame
import secrets


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
        self.input_pass = InputBox(350, 130, 100, 40, text='Password')
        self.button_login = Button(self.screen, (450, 200, 100, 50), 'LogIn')
        self.button_signin = Button(self.screen, (450, 260, 100, 50), 'SignIn')

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
        self.screen.fill((255, 255, 0))
        self.input_name.draw(self.screen)
        self.input_pass.draw(self.screen)
        self.button_login.draw()
        self.button_signin.draw()
        if self.error:
            self.show_text(self.error,375,180,'RED')
        pygame.display.update()

    def show_text(self,text,x,y,color='WHITE'):
        font = pygame.font.SysFont(FONT, 25)
        super_texto = font.render(text, True, color)
        self.screen.blit(super_texto, (x,y))

    def main_loop(self):
        while self.finish:
            events = pygame.event.get()
            for event in events:
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
        # recive base, prime and public key
        data = recv_by_size(self.sock)
        if not data.startswith(b"DPPK~"):
            if DEBUG:
                print("❌ Error: expected DPPK~")
            return

        parts = data[5:].split(b"~")
        if len(parts) != 3:
            if DEBUG:
                print("❌ Error: malformed DPPK~ message")
            return

        base = int(parts[0].decode())
        prime = int(parts[1].decode())
        server_pub = int(parts[2].decode())
        if DEBUG:
            print(f"📥 base={base}, prime={prime}")
            print(f"🔐 Server Public Key (int): {server_pub}")

        self.priv_client = secrets.randbits(128)
        self.pub_client = pow(base, self.priv_client, prime)
        if DEBUG:

            print(f"🔐 Client Public Key (int): {self.pub_client}")

        send_with_size(self.sock, b'DPPK~' + str(self.pub_client).encode())

        shared_secret = pow(server_pub, self.priv_client, prime)
        byte_len = (prime.bit_length() + 7) // 8
        shared_bytes = shared_secret.to_bytes(byte_len, 'big')

        self.shared_key = derive_AES_key(shared_bytes)
        if DEBUG:
            print(f"🔑 Shared AES Key (hex): {self.shared_key.hex()}")


