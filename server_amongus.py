import random
import socket

from IPython.terminal.embed import KillEmbeded
from scapy.contrib.pnio import PROFIsafeStatusCRCSeed

from AsyncMessages import AsyncMessages
import threading
from tcp_by_size import send_with_size,recv_by_size

asyc_mess = AsyncMessages()
THREADS = []
rooms_socks = {'ALONIS':{}}
DEBUG = True
COLORS = ['Red','Blue','Orange','Green','Yellow']
#COLORS = ['Black','Blue','Brown','Green','Orange','Pink','Purple','Red','White','Yellow']
ALL_TO_DIE = False
missions_per_room = {}

def main():
    sock = socket.socket()
    sock.bind(('127.0.0.1', 1234))
    sock.listen(3)
    finish = True

    while finish:
        print('waiting connection...')
        conn, addr = sock.accept()
        conn.settimeout(0.01)

        print('connect from:', addr)

        t = threading.Thread(target=protocol_build,args=(conn,))
        THREADS.append(t)
        t.start()



def protocol_build(sock):
    global asyc_mess,ALL_TO_DIE
    asyc_mess.add_new_socket(sock)
    finish = False
    room = ''

    while not finish and not ALL_TO_DIE:
        try:

            data = recv_by_size(sock)
            if DEBUG:
                print(f'------------\nRECIVED: {data.decode()}\n----------')
            if data == b'':
                finish = True
            elif b'CRTE' in data:
                create_room(data.decode())
            elif b'LOCA' in data:
                send_location(data,room)
            elif b'ROOM' in data:
                room = start_player(data,sock)
                put_messages_in_room(room,b'GLOC')
            elif b'GROM' in data:
                send_rooms(sock)
            elif b'STRT' in data:
                start_game(data)
            elif b'GROL' in data:
                send_rol(data)
            elif b'KILL' in data:
                kill_player(data)
            elif b'SMSG' in data:
                send_message_chat(data)
            if b'VOTE' in data:
                votes_managment(data)
            if b'SUVT' in data:
                kill_player(data)
            if b'EMRG' in data:
                call_emergency(data)
            if b'FTSK' in data:
                mission_completed(data)
        except socket.timeout:
            for mess in asyc_mess.get_async_messages_to_send(sock):
                if DEBUG:
                    print(f'message to: {mess}')
                send_with_size(sock,mess)
        except Exception as err:
            print('PROT_BUILD ERR: ' + str(err) + f'\nroom: {rooms_socks[room]}')

def mission_completed(data):
    room = data.decode().split('~')[1]
    put_messages_in_room(room,b'ATSK')

def call_emergency(data):

    data = data.decode().split('~')
    room = data[1]
    put_messages_in_room(room,b'EMRG')

def votes_managment(data):
    data = data.decode().split('~')
    room = data[1]
    color = data[2]
    color_has_voted = data[3]
    send = f'NVTE~{color}~{color_has_voted}'
    put_messages_in_room(room,send.encode())

def send_message_chat(data):
    data = data.decode().split('~')
    room = data[1]
    color = data[2]
    msg = data[3]
    send = f'GMSG~{color}~{msg}'
    put_messages_in_room(room,send.encode())

def kill_player(data):
    global asyc_mess
    data = data.decode().split('~')
    room = data[1]
    color = data[2]
    send = f'DEAD'
    asyc_mess.put_msg_in_async_msgs(send.encode(),rooms_socks[room][color])

def send_rol(data):
    global asyc_mess
    try:
        data = data.decode().split('~')
        room = data[1]
        color = data[2]
        if 'Imposter' not in rooms_socks[room]:
            return

        if rooms_socks[room]['Imposter'] == color:
            send = 'RROL~IMPOSTER'
            asyc_mess.put_msg_in_async_msgs(send.encode(),rooms_socks[room][color])
        else:
            send = 'RROL~CREWMATE'

            asyc_mess.put_msg_in_async_msgs(send.encode(),rooms_socks[room][color])
        if DEBUG:
            print('SEND ROL: ' + send)


    except Exception as err:
        print('SEND ROL ERR: ' + str(err))


def put_messages_in_room(room,message):
    global asyc_mess
    for key, sock in rooms_socks[room].items():
        if key == 'Imposter':
            continue
        asyc_mess.put_msg_in_async_msgs(message, sock)


def start_game(data):
    room = data.decode().split('~')[1]
    put_messages_in_room(room,b'STRG')
    imposter_color = random.choice(list(rooms_socks[room].keys()))
    rooms_socks[room]['Imposter'] = imposter_color


def start_player(data,sock):
    room = data.decode().split('~')[1]
    color = ''
    while color not in COLORS or color in rooms_socks[room].keys():
        color = COLORS[random.randint(0, len(COLORS) - 1)]

    rooms_socks[room][color] = sock
    asyc_mess.put_msg_in_async_msgs(f'COLO~{color}'.encode(), sock)
    if DEBUG:
        print(F'COLOR: {color}')
    return room

def send_rooms(sock):
    global rooms_socks
    for room in rooms_socks.keys():
        asyc_mess.put_msg_in_async_msgs(room.encode(), sock)
    asyc_mess.put_msg_in_async_msgs(b'finish', sock)

def send_location(data,room):
    put_messages_in_room(room,data)


def create_room(room):
    global rooms_socks
    room = room.split('~')[1]
    rooms_socks[room] = {}
    if DEBUG:
        print(f'ROOM CREATED: {room}')

main()