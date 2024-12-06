import datetime as dt
from flask import Flask, render_template, make_response
import socket
import threading
import time

import gigabyte_constants

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/api/mailbox/emptied', methods=['POST'])
def mailbox_emptied():
    return

@app.route('/api/mailbox/opened', methods=['POST'])
def mailbox_opened():
    return


class Gigabyte:
    def __init__(self, debug: bool = False):
        
        # Socket.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("0.0.0.0", 
                          gigabyte_constants.GIGABYTE_TCP_SERVER_PORT))
        self.socket.settimeout(0.1)

        # Private
        self._running = threading.Event()
        self._running.clear()
        if debug:
            self._run_thread = threading.Thread(target=self.debug_run)
        else:
            self._run_thread = threading.Thread(target=self.run)

    def start(self):
        self._running.set()
        self._run_thread.start()
        print("Gigabyte started")

    def stop(self):
        self._running.clear()
        self._run_thread.join()
        print("Gigabyte stopped")

    def run(self):
        """Connect with TCP at port 8090.
        
        NOTE: Expects clients to send one message and then close the connection.
        """
        while self._running.is_set():
            try:
                self.socket.listen(1)
                client, _ = self.socket.accept()
                client.sendall(b"on")
                client.close()
            except socket.timeout:
                pass
    
    def debug_run(self):
        while self._running.is_set():
            try:
                self.socket.listen(1)
                client, addr = self.socket.accept()
                print(addr, dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                client.sendall(b"on")
                client.close()
            except socket.timeout:
                pass


def main():
    gigabyte = Gigabyte()
    gigabyte.start()
    app.run(host='0.0.0.0', port=gigabyte_constants.GIGABYTE_HTTP_SERVER_PORT)
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


if __name__ == '__main__':
    backend_only()
