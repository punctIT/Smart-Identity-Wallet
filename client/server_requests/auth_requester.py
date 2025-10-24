


class AuthRequester:
    def __init__(self):
        pass
    def log_out(self):
        if self.token == "":
            return
        try:
            payload = {
                "message_type": "logout",
                "user_id": self.token, 
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
                print(f"✅ {data['success']}")
                #self.get_specific_data("ceva")
                return data
            else:
                print(f"❌ Eroare: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Eroare: {str(e)}")
            return None
        

    def send_login(self, username, password):
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
                    self.token = data.get('token')
                    self.user_id = data.get('user_info').get('username')
                    if self.token:
                        self.session.headers.update({
                            'Authorization': f'Bearer {self.token}'
                        })
                    print("login succesdful")
                    return data
                else:
                    print(f"❌ {data.get('message', 'Login eșuat')}")
                    return None
            else:
                print(f"❌ Eroare HTTP: {response.status_code}")
                return None
                
        except Exception as e:
            print("❌ Eroare: {str(e)}")
            return None
        
    def send_register_request(self, username,password,email,phone_number, content=None, parameters=None):
        try:
            payload = {
                "username":username,
                "password":password, 
                "email":email,
                "phone_number": phone_number
            }
            
            response = self.session.post(
                f"{self.server_url}/register", 
                json=payload, 
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print( f"✅ {data['success']}")
                
                return data
            else:
                print(f"❌ Eroare: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Eroare: {str(e)}")
            return None