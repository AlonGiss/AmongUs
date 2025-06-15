import random
import socket
import threading
from AsyncMessages import AsyncMessages
from tcp_by_size import send_with_size, recv_by_size
from ServerHandleLogIn import LoginServer

asyc_mess = AsyncMessages()
THREADS = []
rooms_socks = {'ALONIS': {}}
DEBUG = True
COLORS = ['Red', 'Blue', 'Orange', 'Green', 'Yellow']
ALL_TO_DIE = False
missions_per_room = {}
def main():
    sock = socket.socket()
    sock.bind(('0.0.0.0', 1234))
    sock.listen(10)
    print(" Server listening on port 1234")

    while True:
        print('waiting connection...')
        conn, addr = sock.accept()
        print(f' Connection from {addr}')

        # Handle login in a thread
        login_thread = threading.Thread(target=handle_login_and_continue, args=(conn,))
        login_thread.start()

def handle_login_and_continue(conn):
    try:
        global srv_login
        srv_login = LoginServer(conn)  # DH + LOGIN
        conn.settimeout(0.01)

        # Once login is done, enter protocol
        t = threading.Thread(target=protocol_build, args=(conn,))
        THREADS.append(t)
        t.start()

    except Exception as e:
        print(f' Login thread failed: {e}')
        conn.close()

def protocol_build(sock):
    global asyc_mess, ALL_TO_DIE
    asyc_mess.add_new_socket(sock)
    finish = False
    room = ''
    player_color = ''
    while not finish and not ALL_TO_DIE:
        try:
            data = recv_by_size(sock)
            try:
                decoded = data.decode()
                if DEBUG:
                    print(f'------------\nRECIVED: {decoded}\n----------')
            except UnicodeDecodeError:
                print('Received non-decodable data.')
                continue

            if data == b'':
                finish = True
            elif b'CRTE' in data:
                create_room(data.decode())
            elif b'LOCA' in data:
                send_location(data, room)
            elif b'ROOM' in data:
                room, player_color = start_player(data, sock)
                put_messages_in_room(room, b'GLOC')
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
                expulse_player(data)
            if b'EMRG' in data:
                call_emergency(data)
            if b'FTSK' in data:
                mission_completed(data)
            if b'DESS' in data:
                put_messages_in_room(room, f'DESS~{data.decode().split('~')[1]}'.encode())
            if b'DISS' in data:
                cleanup_player(room,player_color,sock)
            if b'WINN' in data:
                send_win(data)

        except socket.timeout:
            for mess in asyc_mess.get_async_messages_to_send(sock):
                if DEBUG:
                    print(f'message to: {mess}')
                send_with_size(sock, mess)

        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as disconnect_err:
            print(f'Disconnected: {disconnect_err}')
            cleanup_player(room, player_color, sock)
            finish = True

        except Exception as err:
            print('PROT_BUILD ERR: ' + str(err) + f'\nroom: {rooms_socks.get(room, {})}')

def cleanup_player(room, player_color, sock):
    try:
        global srv_login
        if room in rooms_socks and player_color in rooms_socks[room]:
            del rooms_socks[room][player_color]
            print(f'{player_color} removed from room {room} due to disconnection.')

        if room in rooms_socks and rooms_socks[room].get('Imposter') == player_color:
            del rooms_socks[room]['Imposter']
            print(f'Imposter {player_color} removed from room {room}.')
            send = f'WINN~CREWMATE'
            put_messages_in_room(room, send.encode())

        if sock in LoginServer.logged_users.values():
            print('deliting')
            user_to_delete = None
            for username, user_sock in LoginServer.logged_users.items():
                if user_sock == sock:
                    user_to_delete = username
                    break
            if user_to_delete:
                del LoginServer.logged_users[user_to_delete]
                print(f"Deleted logged user: {user_to_delete}")
            print(LoginServer.logged_users)

        if room in rooms_socks and rooms_socks[room].get('admin') == player_color:
            del rooms_socks[room]['admin']
            print(f'admin {player_color} removed from room {room}.')
            available_colors = [c for c in rooms_socks[room] if c not in ('Imposter', 'admin')]
            if available_colors:
                new_admin_color = random.choice(available_colors)
                rooms_socks[room]['admin'] = new_admin_color
                get_new_admin(room, new_admin_color)

        if room in rooms_socks and len(rooms_socks[room]) == 0:
            del rooms_socks[room]
            print(f'Room {room} deleted because it is empty.')

        sock.close()
        put_messages_in_room(room, f'DESS~{player_color}'.encode())

    except Exception as cleanup_err:
        print('Cleanup error:', cleanup_err)

def send_win(data):
    data = data.decode().split('~')
    room = data[1]
    win = data[2]
    put_messages_in_room(room,f'WINN~{win}'.encode())


def get_new_admin(room, color):
    global asyc_mess
    asyc_mess.put_msg_in_async_msgs(b'ADMN', rooms_socks[room][color])

def mission_completed(data):
    room = data.decode().split('~')[1]
    color = data.decode().split('~')[2]
    put_messages_in_room(room, b'ATSK~' + color.encode())

def call_emergency(data):
    data = data.decode().split('~')
    room = data[1]
    put_messages_in_room(room, b'EMRG')

def votes_managment(data):
    data = data.decode().split('~')
    room = data[1]
    color = data[2]
    color_has_voted = data[3]
    send = f'NVTE~{color}~{color_has_voted}'
    put_messages_in_room(room, send.encode())

def send_message_chat(data):
    data = data.decode().split('~')
    room = data[1]
    color = data[2]
    msg = data[3]
    send = f'GMSG~{color}~{msg}'
    put_messages_in_room(room, send.encode())

def expulse_player(data):
    global asyc_mess
    data = data.decode().split('~')
    room = data[1]
    color = data[2]
    if rooms_socks[room]['Imposter'] != color:
        send = f'DEAD'
        asyc_mess.put_msg_in_async_msgs(send.encode(), rooms_socks[room][color])
    else:
        send = f'DEAD'
        asyc_mess.put_msg_in_async_msgs(send.encode(), rooms_socks[room][color])
        send = f'WINN~CREWMATE'
        put_messages_in_room(room, send.encode())

def kill_player(data):
    global asyc_mess
    data = data.decode().split('~')
    room = data[1]
    color = data[2]
    send = f'DEAD'
    asyc_mess.put_msg_in_async_msgs(send.encode(), rooms_socks[room][color])

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
            asyc_mess.put_msg_in_async_msgs(send.encode(), rooms_socks[room][color])
        else:
            send = 'RROL~CREWMATE'
            asyc_mess.put_msg_in_async_msgs(send.encode(), rooms_socks[room][color])
        if DEBUG:
            print('SEND ROL: ' + send)

    except Exception as err:
        print('SEND ROL ERR: ' + str(err))

def put_messages_in_room(room, message):
    global asyc_mess
    for key, sock in rooms_socks[room].items():
        if key == 'Imposter' or key == 'admin':
            continue
        asyc_mess.put_msg_in_async_msgs(message, sock)

def start_game(data):
    room = data.decode().split('~')[1]
    put_messages_in_room(room, b'STRG')
    imposter_color = random.choice([c for c in rooms_socks[room] if c not in ('Imposter', 'admin')])
    rooms_socks[room]['Imposter'] = imposter_color

def start_player(data, sock):
    room = data.decode().split('~')[1]
    color = ''
    while color not in COLORS or color in rooms_socks[room].keys():
        color = random.choice(COLORS)

    rooms_socks[room][color] = sock

    if 'admin' not in rooms_socks[room]:
        rooms_socks[room]['admin'] = color

    asyc_mess.put_msg_in_async_msgs(f'COLO~{color}'.encode(), sock)
    if DEBUG:
        print(f'COLOR: {color}')
    return room, color

def send_rooms(sock):
    global rooms_socks
    for room in rooms_socks.keys():
        asyc_mess.put_msg_in_async_msgs(room.encode(), sock)
    asyc_mess.put_msg_in_async_msgs(b'finish', sock)

def send_location(data, room):
    put_messages_in_room(room, data)

def create_room(room):
    global rooms_socks
    room = room.split('~')[1]
    rooms_socks[room] = {}
    if DEBUG:
        print(f'ROOM CREATED: {room}')

main()
