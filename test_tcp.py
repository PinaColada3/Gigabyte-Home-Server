import socket

def send_mailbox_opened():
    server_address = ('192.168.0.21', 8090)
    message = b"mailbox left opened"
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(server_address)
        s.sendall(message)
        print("Message sent: mailbox opened")

send_mailbox_opened()

