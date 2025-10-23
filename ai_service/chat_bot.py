import asyncio
from dotenv import load_dotenv
import os
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor

class ChatBot:
    def __init__(self, max_workers=2, max_prompt_len=500):
        load_dotenv()
        self.api_ai = os.getenv("API_AI")
        genai.configure(api_key=self.api_ai)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.max_prompt_len = max_prompt_len
        self.cache = {}  # simplu cache, pe prompt

    async def get_response(self, text):
        if len(text) > self.max_prompt_len:
            text = text[:self.max_prompt_len]

        if text in self.cache:
            print("Returnez din cache!")
            return self.cache[text]

        generation_config = {
            "candidate_count": 1,
            "temperature": 1.6,
            "top_p": 0.3,
        }

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                lambda: self.model.generate_content(
                    text,
                    generation_config=generation_config
                )
            )
            self.cache[text] = response.text
            print(response.text)
            return response.text
        except Exception as e:
            print(f"Error in get_response: {e}")
            raise e
