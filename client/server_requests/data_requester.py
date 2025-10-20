


# "InsertIdenityCard" => IdentityCard::insert(&request, app_state).await,
# "GetIdenityCard" => IdentityCard::get(&request, app_state).await,
# "UpdateIdenityCard" => IdentityCard::update(&request, app_state).await,
# "GetWalletCards" => PersonalDataManager::get_wallet_data(&request, app_state).await,

class DataRequester:
    def __init__(self):
        pass
    def get_specific_data(self, message_type):
        try:
            payload = {
                "message_type": message_type,
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
                print(data)
                if data['success'] is False:
                    return None
                return data
            else:
                print(f"❌ Eroare: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Eroare: {str(e)}")
            return None
    def sent_specific_data(self, message_type, json_content):
        try:
            payload = {
                "message_type": message_type,
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
                print(f"✅ {data['success']}")
                return data
            else:
                print(f"❌ Eroare: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Eroare: {str(e)}")
            return None
    