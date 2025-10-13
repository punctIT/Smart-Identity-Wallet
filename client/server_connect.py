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

SERVER_URL = "https://127.0.0.1:8443"


class ServerConnection(Label):
    last_message = StringProperty("Aștept conexiuni...")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = requests.Session()
        # Acceptă certificatele self-signed
        self.session.verify = False
        
    def connect(self):
        """Test conexiunea la server"""
        try:
            response = self.session.get(f"{SERVER_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.last_message = f"✅ Conectat la server - {data['message']}"
                return True
            else:
                self.last_message = f"❌ Eroare HTTP: {response.status_code}"
                return False
        except Exception as e:
            self.last_message = f"❌ Eroare conexiune: {str(e)}"
            return False

    def get_data(self):
        """Primește date de la server"""
        try:
            response = self.session.get(f"{SERVER_URL}/api/data", timeout=5)
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
                "parameters": parameters
            }
            
            response = self.session.post(
                f"{SERVER_URL}/api/message", 
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


    def authenticate(self, username, certificate_data=None):
        """Autentificare cu serverul"""
        try:
            payload = {
                "username": username,
                "certificate": certificate_data or "client_cert_data",
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(
                f"{SERVER_URL}/api/auth", 
                json=payload, 
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('authenticated'):
                    self.last_message = f"🔐 Autentificat cu succes! Token primit."
                    return data.get('token')
                else:
                    self.last_message = f"❌ Autentificare eșuată"
                    return None
            else:
                self.last_message = f"❌ Eroare autentificare: {response.status_code}"
                return None
                
        except Exception as e:
            self.last_message = f"❌ Eroare autentificare: {str(e)}"
            return None

    def start_periodic_check(self, interval=5):
        """Verifică periodic starea serverului"""
        def check_server():
            while True:
                try:
                    response = self.session.get(f"{SERVER_URL}/health", timeout=2)
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

    def sent(self, text):
        """Compatibilitate cu codul vechi - trimite text simplu"""
        return self.send_data("mobile_user", "Kivy_App", text)

    def update_message(self, msg):
        """Actualizează mesajul afișat"""
        self.last_message = msg

    def close(self):
        """Închide sesiunea"""
        if self.session:
            self.session.close()