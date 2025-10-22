#"InsertIdenityCard" => WalletCards::insert("identity_card",&request, app_state).await,
#"GetIdenityCard" => WalletCards::get("identity_card",&request, app_state).await,
# "InsertDrivingLicense" => WalletCards::insert("driving_license",&request, app_state).await,
#"GetDrivingLicense" => WalletCards::get("driving_license",&request, app_state).await,
#"InsertPassport" => WalletCards::insert("passport",&request, app_state).await,
#"GetPassport" => WalletCards::get("passport",&request, app_state).await,
#"InsertVehicleRegistration" => WalletCards::insert("vehicle_registration",&request, app_state).await,
#"GetVehicleRegistration" => WalletCards::get("vehicle_registration",&request, app_state).await,
#"InsertInsuranceAuto" => WalletCards::insert("insurance_auto",&request, app_state).await,
#"GetInsuranceAuto" => WalletCards::get("insurance_auto",&request, app_state).await,
#"GetWalletCards" => PersonalDataManager::get_wallet_data(&request, app_state).await,
# "News"=>NewsData::get_latest_news(app_state).await,


class DataRequester:
    _MOCK_WALLET_CARDS = [
        {
            "title": "Carte identitate",
            "subtitle": "Seria RX 123456",
            "status": "Valid",
            "number": "RX123456",
            "expiry": "12.08.2030",
        },
        {
            "title": "Pasaport",
            "subtitle": "Simplu electronic",
            "status": "Activ",
            "number": "045678912",
            "expiry": "05.04.2029",
        },
        {
            "title": "Permis conducere",
            "subtitle": "Categoria B",
            "status": "Reinnoit recent",
            "number": "B1234567",
            "expiry": "21.11.2027",
        },
    ]

    def __init__(self):
        pass

    def _mock_wallet_cards(self, message_type: str):
        """Return a mocked wallet response to populate the UI without a backend."""
        return {
            "success": True,
            "message_type": message_type,
            "data": {
                "cards": list(self._MOCK_WALLET_CARDS),
                "last_synced": "2024-03-14T12:00:00Z",
            },
        }

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
                #print(data['data'])
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
    
