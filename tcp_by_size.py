__author__ = 'Yossi'

# from  tcp_by_size import send_with_size ,recv_by_size


SIZE_HEADER_FORMAT = "000000000|" # n digits for data size + one delimiter
size_header_size = len(SIZE_HEADER_FORMAT)
TCP_DEBUG = True
LEN_TO_PRINT = 100


def recv_by_size(sock):
    size_header = b''
    while len(size_header) < size_header_size:
        _s = sock.recv(size_header_size - len(size_header))
        if _s == b'':
            return b''
        size_header += _s

    try:
        data_len = int(size_header[:size_header_size - 1])
    except ValueError:
        print("❌ Invalid size header received:", size_header)
        return b''

    data = b''
    while len(data) < data_len:
        _d = sock.recv(data_len - len(data))
        if _d == b'':
            return b''
        data += _d

    if TCP_DEBUG:
        print(f"\nRecv({size_header})>>>", end='')
        print(data[:min(len(data), LEN_TO_PRINT)])
    return data  # ✅ return full raw data, no .split()




def send_with_size(sock, bdata):
    if type(bdata) == str:
        bdata = bdata.encode()
    len_data = len(bdata)
    header_data = str(len(bdata)).zfill(size_header_size - 1) + "|"

    bytea = bytearray(header_data,encoding='utf8') + bdata

    sock.send(bytea)
    if TCP_DEBUG and  len_data > 0:
        print ("\nSent(%s)>>>" % (len_data,), end='')
        print ("%s"%(bytea[:min(len(bytea),LEN_TO_PRINT)],))
