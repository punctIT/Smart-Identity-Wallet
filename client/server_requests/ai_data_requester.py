# "ChatBot" => AiRequests::call_python_chat(&request).await,
# "OCR" => AiRequests::call_python_ocr(&request).await,
# "health" => AiRequests::call_python_health().await,

import base64
import os
from pathlib import Path
from kivy.logger import Logger

class AI_DataRequester:
    def __init__(self):
        pass

    def sent_chatbot_msg(self, request):
        try:
            payload = {
                "message_type": "ChatBot",
                "user_id": self.user_id, 
                "content": request,
                "token": self.token
            }
            
            response = self.session.post(
                f"{self.server_url}/api/AI", 
                json=payload, 
                timeout=120,
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {data['success']}")
                return data
            else:
                print(f"❌ Eroare: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Eroare: {str(e)}")
            return None
    def sent_OCR_image(self, img_base64):
        try:
            payload = {
                "message_type": "OCR",
                "user_id": self.user_id, 
                "content": img_base64,
                "token": self.token
            }
            
            response = self.session.post(
                f"{self.server_url}/api/AI", 
                json=payload, 
                timeout=120,
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {data['success']}")
                return data
            else:
                print(f"❌ Eroare: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Eroare: {str(e)}")
            return None