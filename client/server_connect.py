from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.clock import Clock
import socket
import threading

SERVER_IP = "127.0.0.1"
SERVER_PORT = 1234


class ServerConnection(Label):
    last_message = StringProperty("Aștept conexiuni...")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client_socket = None

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_IP, SERVER_PORT))
            self.last_message = f"Conectat la {SERVER_IP}:{SERVER_PORT}"
            threading.Thread(target=self.start_receive, daemon=True).start()
        except Exception as e:
            self.last_message = f"Eroare: {e}"

    def start_receive(self):
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                message = data.decode()
                Clock.schedule_once(lambda dt: self.update_message(message))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_message("Conexiune întreruptă."))
    def sent(self,text):
        self.client_socket.send(text.encode())
    def update_message(self, msg):
        self.last_message = f"Primit: {msg}"

    def close(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None

