from dotenv import load_dotenv
import os



class ChatBot:
    def __init__(self):
        load_dotenv()  # Dacă fișierul nu e în același folder, specifică path-ul: load_dotenv("cale/catre/.env")
        self.api_ai = os.getenv("API_AI")
    def get_response(self,text):
        if text == "salut":
            return "ana re mere msau cevaana re mere msau cevaana re mere msau cevaana re mere msau cevaana re mere msau cevaana re mere msau cevaana re mere msau cevaana re mere msau cevaana re mere msau cevaana re mere msau cevaana re mere msau cevaana re mere msau cevaana re mere msau cevaana re mere msau cevaana re mere msau ceva"
        elif text =="api":
            return self.api_ai 
        else :
            return "nu m ai salutat"