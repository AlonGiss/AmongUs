
from Game import Game
from Button import Button
from Menu import Menu
import pygame
import socket
from tcp_by_size import recv_by_size,send_with_size
from Lobby import Lobby
from Login import  Login

def main():
    try:
        pygame.init()
        lobby = None
        admin = False
        sock = socket.socket()
        sock.connect(('127.0.0.1', 1234))
        login = Login(sock)
        username,password = login.main_loop()
        game = True
        while game:
            lobby = start_menu(sock)
            player,players = start_lobby(lobby,sock,admin)
            if 'CRTE' in lobby:
                lobby = lobby.split('~')[1]
            game = start_game(sock,player,players,lobby)

    except Exception as err:
        import error_screen
        print(f"Unexpected disconnection: {err}")
        error_screen.show_server_disconnection_error()

def start_game(sock,player,players,lobby):
    game = Game(sock,lobby,player,len(players.keys()))
    return game.main_game()

def start_lobby(lobby,sock,admin):
    if 'CRTE' in lobby:
        send_with_size(sock,lobby.encode())
        lobby = lobby.split('~')[1]
        admin = True

    send_with_size(sock,b'ROOM~' + lobby.encode())
    lobby_room = Lobby(sock,lobby,admin)
    return lobby_room.main_lobby()

def start_menu(sock):
    menu = Menu(sock)
    return menu.start_menu()

main()