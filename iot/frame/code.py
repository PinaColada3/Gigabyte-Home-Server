import errno
import socketpool
import time
import wifi


def turn_on():
    pass


def turn_off():
    pass


# Init.
pool = socketpool.SocketPool(wifi.radio)

connected = False
socket = None
RECV_SIZE = 1024
recv_buffer = bytearray(1024)

# Main loop.
while True:
    # Connect to the server if not connected.
    if not connected:
        if socket is None:
            socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
            socket.settimeout(5)
        try:
            socket.connect(('gigabyte.local', 8090))
            print('Connected')
            connected = True
        except OSError:
            time.sleep(5)
            continue

    # Listen for messages.
    try:
        size = socket.recv_into(recv_buffer)
        print(size, recv_buffer[:size])
        if size > 0:
            msg = recv_buffer[:size].decode()
            if msg == 'on':
                # Turn on instruction.
                print("Turn on")
                turn_on()
            elif msg == 'off':
                # Turn off instruction.
                print("Turn off")
                turn_off()
        else:
            # Size 0 == client.close()
            connected = False
            socket.close()
            socket = None
    except OSError as e:
        if e.errno == errno.ETIMEDOUT:
            pass
        elif e.errno == errno.ECONNRESET:
            connected = False
            socket.close()
            socket = None

    # Wait.
    time.sleep(5)
