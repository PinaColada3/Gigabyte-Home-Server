import socket

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 8090))
    s.sendall(b"open")
    s.close()

if __name__ == '__main__':
    main()
