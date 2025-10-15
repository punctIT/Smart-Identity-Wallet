from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.clock import Clock
import requests
import threading
import json
import urllib3
from datetime import datetime

# Disable SSL warnings pentru certificatele self-signed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ServerConnection(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = requests.Session()
        self.token=""
        self.server_url="https://127.0.0.1:8443"
        
        # Acceptă certificatele self-signed
        self.session.verify = False
    def set_server_url(self,URL)->"ServerConnection":
        self.set_server_url=URL
        return self
    def connect(self):
        """Test conexiunea la server"""
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

    def get_data(self):
        """Primește date de la server"""
        try:
            response = self.session.get(f"{self.server_url}/api/data", timeout=5)
            if response.status_code == 200:
                data = response.json()
                message = data['data']['message']
                timestamp = data['data']['timestamp']
                self.last_message = f"📨 {message} ({timestamp})"
                return data
            else:
                self.last_message = f"❌ Eroare la primirea datelor: {response.status_code}"
                return None
        except Exception as e:
            self.last_message = f"❌ Eroare: {str(e)}"
            return None

    def send_specific_message(self, message_type, content=None, parameters=None):
        """Trimite mesaj specific la server"""
        try:
            payload = {
                "message_type": message_type,
                "user_id": "punctITok", 
                "content": content,
                "token": self.token
            }
            
            response = self.session.post(
                f"{self.server_url}/api/message", 
                json=payload, 
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.last_message = f"✅ {data['data']}"
                return data
            else:
                self.last_message = f"❌ Eroare: {response.status_code}"
                return None
                
        except Exception as e:
            self.last_message = f"❌ Eroare: {str(e)}"
            return None

    def send_login(self, username, password):
        """Trimite request de login la server"""
        try:
            payload = {
                "username": username,
                "password": password, 
            }
            
            response = self.session.post(
                f"{self.server_url}/login", 
                json=payload, 
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success', False):
                    # Salvează tokenul pentru requesturile viitoare
                    self.token = data.get('token')
                    if self.token:
                        self.session.headers.update({
                            'Authorization': f'Bearer {self.token}'
                        })
                    
                    # Afișează mesajul de succes
                    self.last_message = f"✅ {data.get('message', 'Login reușit')}"
                    return data
                else:
                    # Login eșuat
                    self.last_message = f"❌ {data.get('message', 'Login eșuat')}"
                    return None
            else:
                self.last_message = f"❌ Eroare HTTP: {response.status_code}"
                return None
                
        except Exception as e:
            self.last_message = f"❌ Eroare: {str(e)}"
            return None

        

    def start_periodic_check(self, interval=5):
        """Verifică periodic starea serverului"""
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
        """Închide sesiunea"""
        if self.session:
            self.session.close()