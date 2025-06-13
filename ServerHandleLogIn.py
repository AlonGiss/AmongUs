# === server.py ===
import socket
import os

from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from tcp_by_size import send_with_size, recv_by_size
from CryptoUtils import derive_AES_key, recv_with_AES, send_with_AES
import pickle
DEBUG= True
class LoginServer:
    logged_users = {}

    def __init__(self, sock: socket):
        self.sock = sock
        self.priv_server, self.pub_server, self.base_int, self.prime_int = self.generate_dh_keys()
        self.shared_key = None
        self.users_file = 'users.pkl'
        self.ensure_users_file_exists()
        self.finish = True
        self.users = self.load_users()
        self.send_public_key()
        self.receive_client_key()
        self.recive_data()


    def ensure_users_file_exists(self):
        if not os.path.exists(self.users_file):
            print(f"Creating missing {self.users_file}...")
            with open(self.users_file, 'wb') as f:
                pickle.dump({}, f)
        else:
            print(f"{self.users_file} already exists.")

    def recive_data(self):
        while self.finish:
            data = recv_with_AES(self.sock, self.shared_key)
            if DEBUG:
                print(f"Received: {data}")

            if data.startswith('LGIN~'):
                self.handle_login(data)
            elif data.startswith('SIGN~'):
                self.handle_signup(data)
                data = recv_with_AES(self.sock, self.shared_key)
                self.handle_login(data)
            else:
                print("Unknown protocol")

    def load_users(self):
        return pickle.load(open(self.users_file, 'rb')) if os.path.exists(self.users_file) else {}

    def save_users(self):
        with open(self.users_file, 'wb') as f:
            pickle.dump(self.users, f)

    def handle_login(self, data):
        code, user, password = data.split('~')
        if user in self.users:
            if self.users[user] == password:
                if user in LoginServer.logged_users.keys():
                    send = 'ERRR~User has already connected'
                else:
                    LoginServer.logged_users[user] = self.sock
                    send = 'LOGS'
                    self.finish = False
            else:
                send = 'ERRR~User or Password Not Found'
        else:
            send = 'ERRR~User or Password Not Found'
        send_with_AES(self.sock,send,self.shared_key)

    def handle_signup(self, data):
        code, user, password = data.split('~')
        if user in self.users:
            send = f'ERRR~User already exists: {user}'
        else:
            self.users[user] = password
            self.save_users()
            send ='SGSC'
        send_with_AES(self.sock,send,self.shared_key)

    def send_public_key(self):
        param_numbers = self.priv_server.private_numbers().public_numbers.parameter_numbers
        base = param_numbers.g
        prime = param_numbers.p

        pub_bytes = self.pub_server.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Enviar como paquete: p|g|pub_key
        data = {
            'p': prime,
            'g': base,
            'pub': pub_bytes
        }
        send_with_size(self.sock, pickle.dumps(data))

    def receive_client_key(self):
        client_pub_bytes = recv_by_size(self.sock)

        client_pub_key = serialization.load_pem_public_key(client_pub_bytes, backend=default_backend())

        shared_key = self.priv_server.exchange(client_pub_key)
        if DEBUG:
            print(f'Shared Key: {shared_key.hex()}')
        self.shared_key = derive_AES_key(shared_key)

    def generate_dh_keys(self, base=2, prime=None):
        parameters = dh.generate_parameters(generator=base, key_size=512, backend=default_backend())
        priv_key = parameters.generate_private_key()
        pub_key = priv_key.public_key()
        return priv_key, pub_key, base, parameters.parameter_numbers().p


