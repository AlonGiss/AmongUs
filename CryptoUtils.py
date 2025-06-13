from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os

from tcp_by_size import send_with_size, recv_by_size




def derive_AES_key(shared_key):
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
        backend=default_backend()
    ).derive(shared_key)


def send_with_AES(sock, plaintext, key):
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    send_with_size(sock, iv + ciphertext)

def recv_with_AES(sock, key):
    data = recv_by_size(sock)
    if not data or len(data) < 16:
        print(f"❌ recv_with_AES: Data too short ({len(data) if data else 0} bytes)")
        return ''
    try:
        iv, ciphertext = data[:16], data[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(ciphertext), AES.block_size).decode()
    except Exception as e:
        print(f"❌ AES decryption error: {e}")
        return ''

