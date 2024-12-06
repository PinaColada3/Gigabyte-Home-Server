import wifi
import socketpool
import ipaddress
import time

pool = socketpool.SocketPool(wifi.radio)

while True:
    print("Create TCP Client Socket")
    with pool.socket(pool.AF_INET, pool.SOCK_STREAM) as s:
        s.settimeout(5)

        print("Connecting")
        s.connect(('gigabyte.local', 8090))

        size = s.send(b'Hello, world')

        time.sleep(5)

# Init.
pool = socketpool.SocketPool(wifi.radio)

while True:
    