import asyncio
from dotenv import load_dotenv
import os
import google.generativeai as genai

class ChatBot:
    def __init__(self):
        load_dotenv() 
        self.api_ai = os.getenv("API_AI")
        genai.configure(api_key=self.api_ai)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        
    async def get_response(self, text):
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self.model.generate_content, 
                text
            )
            print(response.text)
            return response.text
        except Exception as e:
            print(f"Error in get_response: {e}")
            raise e