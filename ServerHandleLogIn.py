# === server.py ===
import socket
import os
import secrets
import sympy
from tcp_by_size import send_with_size, recv_by_size
from CryptoUtils import derive_AES_key, recv_with_AES, send_with_AES
import pickle
DEBUG= True
class LoginServer:
    def __init__(self, sock: socket):
        self.sock = sock
        self.priv_server, self.pub_server, self.base_int, self.prime_int = self.generate_dh_keys()
        self.shared_key = None
        self.users_file = 'users.pkl'
        self.ensure_users_file_exists()
        self.users = self.load_users()
        self.send_public_key()
        self.receive_client_key()
        self.recive_data()

    def ensure_users_file_exists(self):
        if not os.path.exists(self.users_file):
            print(f"🛠️ Creating missing {self.users_file}...")
            with open(self.users_file, 'wb') as f:
                pickle.dump({}, f)
        else:
            print(f"✅ {self.users_file} already exists.")

    def recive_data(self):
        data = recv_with_AES(self.sock, self.shared_key)
        if DEBUG:
            print(f"📩 Received: {data}")

        if data.startswith('LGIN~'):
            self.handle_login(data)
        elif data.startswith('SIGN~'):
            self.handle_signup(data)
        else:
            print("❌ Unknown protocol")

    def load_users(self):
        return pickle.load(open(self.users_file, 'rb')) if os.path.exists(self.users_file) else {}

    def save_users(self):
        with open(self.users_file, 'wb') as f:
            pickle.dump(self.users, f)

    def handle_login(self, data):
        code, user, password = data.split('~')
        if user in self.users:
            if self.users[user] == password:
                send = 'LOGS'
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
        base_str = str(self.base_int).encode()
        prime_str = str(self.prime_int).encode()
        pub_str = str(self.pub_server).encode()

        message = b"DPPK~" + base_str + b"~" + prime_str + b"~" + pub_str
        send_with_size(self.sock, message)
        if DEBUG:
            print(f"📤 Sent DH parameters and public key to client.")

    def receive_client_key(self):
        if DEBUG:
            print("📥 Waiting for client public key...")
        data = recv_by_size(self.sock)
        if not data.startswith(b"DPPK~"):
            if DEBUG:
                print("❌ Invalid message format.")
            return

        client_pub = int(data.split(b"~")[1].decode())
        if DEBUG:
            print(f"🔐 Received Client Public Key: {client_pub}")

        shared_secret = pow(client_pub, self.priv_server, self.prime_int)
        byte_len = (self.prime_int.bit_length() + 7) // 8
        self.shared_key = derive_AES_key(shared_secret.to_bytes(byte_len, 'big'))
        if DEBUG:
            print(f"🔑 Shared AES Key (hex): {self.shared_key.hex()}")

    def generate_dh_keys(self, base=2, prime=None):
        if prime is None:
            prime = self.generate_large_prime()
        priv = secrets.randbits(128)
        pub = pow(base, priv, prime)
        if DEBUG:
            print("\n**********")
            print(f"[DEBUG] Server Private Key: {priv}")
            print(f"[DEBUG] Server Public Key:  {pub}")
            print("**********\n")
        return priv, pub, base, prime

    def generate_large_prime(self, bits=2048):
        return sympy.randprime(2 ** (bits - 1), 2 ** bits)


