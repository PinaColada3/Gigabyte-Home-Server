import datetime as dt
from flask import Flask, render_template, Response
import json
import os
import socket
import threading
import time

import gigabyte_constants
from gigabyte_logger import GigabyteLogger


INTERNAL_SERVER_ERROR = 500
SERVICE_UNAVAILABLE = 503
LOGGER_OUTPUT = '/home/chisan/runtime_logs'


app = Flask(__name__)


@app.route('/api/mailbox/status', methods=['GET'])
def mailbox_status() -> Response:
    """Return the status of the mailbox.

    Returns:
        Response: The status of the mailbox.
    """
    status = INTERNAL_SERVER_ERROR
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('192.168.0.21',
                       gigabyte_constants.GIGABYTE_TCP_SERVER_PORT))
            s.sendall('mailbox status'.encode())
            ret = s.recv(1024).decode()
            return Response(json.dumps(ret),
                            mimetype='application/json',
                            status=200)
    except socket.timeout:
        status = SERVICE_UNAVAILABLE
    except socket.error:
        status = INTERNAL_SERVER_ERROR
    except json.JSONDecodeError:
        status = INTERNAL_SERVER_ERROR
    return Response(status=status)


class MailboxStatus:
    EMPTY = 'empty'
    FILLED = 'filled'
    LEFT_OPENED = 'left opened'


class Gigabyte:
    """
    Gigabyte Backend Server.
    
    This acts as the TCP backend server for Gigabyte.
    
    Current responsiblities:
    - Host a TCP server at port GIGABYTE_TCP_SERVER_PORT.
    - Respond to messages from the RESTFul API.
    - Handle mailbox status & messages from the ESP32C3 mailbox.
    """
    def __init__(self, debug: bool = False) -> None:
        self.debug = debug
        log_filename = dt.datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S_gigabyte.log"
            )
        self.log_output = os.path.join(LOGGER_OUTPUT, log_filename)
        self.gigabyte_logger = GigabyteLogger(self.log_output)
        
        # Socket.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('192.168.0.21',
                          gigabyte_constants.GIGABYTE_TCP_SERVER_PORT))
        self.socket.settimeout(0.1)

        # Private.
        self._running = threading.Event()
        self._running.clear()
        self._run_thread = threading.Thread(target=self.run)
            
        # Mailbox handling.
        self.mailbox_opened = MailboxStatus.EMPTY

    def start(self) -> None:
        """Start the TCP server."""
        self._running.set()
        self._run_thread.start()
        print("Gigabyte started")

    def stop(self) -> None:
        """Stop the TCP server."""
        self._running.clear()
        self._run_thread.join()
        print("Gigabyte stopped")

    def run(self) -> None:
        """Connect with TCP at port GIGABYTE_TCP_SERVER_PORT.
        
        NOTE: Expects clients to send one message and then close the connection.
        """
        while self._running.is_set():
            try:
                # Accept connections.
                self.socket.listen(10)
                client, _ = self.socket.accept()
                print('New client')
                msg = client.recv(1024).decode()
                
                # Process messages.
                if msg == 'mailbox opened':
                    if self.debug:
                        print("Mailbox opened")
                    self.mailbox_opened = MailboxStatus.FILLED
                elif msg == 'mailbox emptied':
                    if self.debug:
                        print("Mailbox emptied")
                    self.mailbox_opened = MailboxStatus.EMPTY
                elif msg == 'mailbox status':
                    if self.debug:
                        print("Mailbox status")
                    ret = {
                        'mailbox_status': self.mailbox_opened
                    }
                    client.sendall(json.dumps(ret).encode())
                elif msg == 'mailbox left opened':
                    print("Mailbox left opened!!!")
                    self.mailbox_opened = MailboxStatus.LEFT_OPENED
                else:
                    print(f'Unknown message: {msg}')
                # Close.
                client.close()
            except socket.timeout:
                # No new connection; skip.
                pass
            except socket.error:
                # Send error.
                pass

    def debug_run(self) -> None:
        while self._running.is_set():
            try:
                self.socket.listen(1)
                client, addr = self.socket.accept()
                print(addr, dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                ret = client.recv(1024)
                print(ret.decode())
                # client.sendall(b"on")
                client.close()
            except socket.timeout:
                pass


def main():
    """Main entry point.
    
    Starts the TCP server and RESTful API. Expected on only expose the API
    on localhost only.
    """
    gigabyte = Gigabyte(debug=True)
    gigabyte.start()
    app.run(host='localhost', port=gigabyte_constants.GIGABYTE_HTTP_SERVER_PORT)
    gigabyte.stop()


def backend_only():
    gigabyte = Gigabyte(debug=True)
    gigabyte.start()
    while True:
        try:
            time.sleep(.1)
        except KeyboardInterrupt:
            gigabyte.stop()
            break


def frontend_only():
    app.run(host='0.0.0.0', port=gigabyte_constants.GIGABYTE_HTTP_SERVER_PORT)        


if __name__ == '__main__':
    main()
