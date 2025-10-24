from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.clock import Clock
import requests
import threading
import urllib3


from server_requests.data_requester import DataRequester
from server_requests.auth_requester import AuthRequester
from server_requests.ai_data_requester import AI_DataRequester


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ServerConnection(Label,DataRequester,AuthRequester,AI_DataRequester):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = requests.Session()
        self.token=""
        self.user_id=""
        self.server_url="https://127.0.0.1:8443"
        self.session.verify = False
    def set_server_url(self, url: str) -> "ServerConnection":
        """Update the base URL that subsequent requests should hit."""
        if not isinstance(url, str):
            raise TypeError("Server URL must be a string.")
        self.server_url = url.rstrip("/")
        return self
    def connect(self):
        try:
            response = self.session.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return True
            else:
                self.last_message = f"❌ Eroare HTTP: {response.status_code}"
                return None
        except Exception as e:
            self.last_message = f"❌ Eroare conexiune: {str(e)}"
            return None
    def clear_data(self):
        self.token=""
        self.user_id=""
    def start_periodic_check(self, interval=5):
        def check_server():
            while True:
                try:
                    response = self.session.get(f"{self.server_url}/health", timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        Clock.schedule_once(
                            lambda dt: self.update_message(f"🟢 Server OK - {data['timestamp']}")
                        )
                    else:
                        Clock.schedule_once(
                            lambda dt: self.update_message("🔴 Server nu răspunde")
                        )
                except:
                    Clock.schedule_once(
                        lambda dt: self.update_message("🔴 Conexiune pierdută")
                    )
                threading.Event().wait(interval)
        threading.Thread(target=check_server, daemon=True).start()

    def close(self):
        if self.session:
            self.session.close()
