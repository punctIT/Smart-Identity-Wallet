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
    def sent_OCR_image(self, img_path, delete_after=True):
        """
        Convert image to base64, send to server for OCR processing, optionally delete the original file.
        
        Args:
            img_path (str or Path): Path to the image file to process
            delete_after (bool): Whether to delete the original file after successful upload
            
        Returns:
            dict or None: Server response data if successful, None if failed
        """
        img_path = Path(img_path)
        
        try:
            # Check if file exists
            if not img_path.exists():
                Logger.error(f"AI_DataRequester: Image file not found: {img_path}")
                print(f"❌ Eroare: Fișierul nu există: {img_path}")
                return None
            
            # Read and convert image to base64
            Logger.info(f"AI_DataRequester: Converting image to base64: {img_path}")
            with open(img_path, "rb") as image_file:
                image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare payload with base64 image
            payload = {
                "message_type": "OCR",
                "user_id": self.user_id, 
                "content": base64_image,
                "token": self.token
            }
            
            Logger.info(f"AI_DataRequester: Sending OCR request to server")
            response = self.session.post(
                f"{self.server_url}/api/AI", 
                json=payload, 
                timeout=30  # Increased timeout for image processing
            )
            
            if response.status_code == 200:
                data = response.json()
                Logger.info(f"AI_DataRequester: OCR request successful")
                print(f"✅ OCR Success: {data.get('success', 'Processed successfully')}")
                
                # Delete the original image file after successful upload if requested
                if delete_after:
                    try:
                        os.remove(img_path)
                        Logger.info(f"AI_DataRequester: Deleted original image: {img_path}")
                        print(f"🗑️ Imagine ștearsă: {img_path.name}")
                    except OSError as delete_error:
                        Logger.warning(f"AI_DataRequester: Could not delete image {img_path}: {delete_error}")
                        print(f"⚠️ Nu s-a putut șterge imaginea: {delete_error}")
                
                return data
            else:
                Logger.error(f"AI_DataRequester: OCR request failed with status {response.status_code}")
                print(f"❌ Eroare server: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"❌ Detalii eroare: {error_data}")
                except:
                    print(f"❌ Response text: {response.text}")
                return None
                
        except FileNotFoundError:
            Logger.error(f"AI_DataRequester: Image file not found: {img_path}")
            print(f"❌ Eroare: Fișierul nu a fost găsit: {img_path}")
            return None
        except PermissionError:
            Logger.error(f"AI_DataRequester: Permission denied accessing: {img_path}")
            print(f"❌ Eroare: Acces refuzat la fișier: {img_path}")
            return None
        except Exception as e:
            Logger.error(f"AI_DataRequester: OCR request failed: {str(e)}")
            print(f"❌ Eroare OCR: {str(e)}")
            return None