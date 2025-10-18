


# "InsertIdenityCard" => IdentityCard::insert(&request, app_state).await,
# "GetIdenityCard" => IdentityCard::get(&request, app_state).await,
# "UpdateIdenityCard" => IdentityCard::update(&request, app_state).await,
# "GetWalletCards" => PersonalDataManager::get_wallet_data(&request, app_state).await,

class DataRequester:
    def __init__(self):
        pass
    def get_personal_data_cards(self):
        
        pass
    def insert_identity_card(self,json_content):
        try:
            payload = {
                "message_type": "InsertIdenityCard",
                "user_id": self.user_id, 
                "content": json_content,
                "token": self.token
            }
            
            response = self.session.post(
                f"{self.server_url}/api/message", 
                json=payload, 
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ {data['data']}")
                return data
            else:
                print(f"❌ Eroare: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Eroare: {str(e)}")
            return None
        
    def update_identity_card(self):
        pass
    def get_identity_card(self):
        try:
            payload = {
                "message_type": "GetIdenityCard",
                "user_id": self.user_id, 
                "content": None,
                "token": self.token
            }
            
            response = self.session.post(
                f"{self.server_url}/api/message", 
                json=payload, 
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {data['data']}")
                return data
            else:
                print(f"❌ Eroare: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Eroare: {str(e)}")
            return None
    def send_specific_message(self, message_type, content=None, parameters=None):
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
    