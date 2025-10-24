from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from kivy.vector import Vector
from kivy.utils import platform

from kivymd.app import MDApp

from server_requests.server_connect import ServerConnection
from frontend.screens.home_screen.home_screen import HomeScreen
from frontend.screens.login_screen import LoginScreen
from frontend.screens.home_screen.personal_docs_screen import PersonalDocsScreen
from frontend.screens.home_screen.vehicul_docs_screen import VehiculDocsScreen
from frontend.screens.home_screen.transport_docs_screen import TransportDocsScreen
from frontend.screens.home_screen.diverse_docs_screen import DiverseDocsScreen
from frontend.screens.home_screen.scan_camera_screen import CameraScanScreen
from frontend.screens.register_screen import RegisterScreen
from frontend.screens.splash_screen import SplashScreen
from frontend.screens.server_setup_screen import ServerSetupScreen
from frontend.screens.chat_screens.chat_screen import ChatScreen
from frontend.screens.cards_screen.idenity_card import IDScreen
from frontend.screens.settings.settings import SettingsScreen
from frontend.screens.settings.account_info_screen import AccountInfoScreen
from frontend.screens.settings.security_screen import SecurityScreen
from frontend.screens.save_screens.save_data import SaveScreen

if platform == "android":
    from android.permissions import request_permissions, Permission




class SwipeScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition(direction='up', duration=0.2)
        self.touch_start_pos = None
        self.min_swipe_distance = 100
        
    def on_touch_down(self, touch):
        self.touch_start_pos = touch.pos
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if self.touch_start_pos:
            swipe_vector = Vector(touch.pos) - Vector(self.touch_start_pos)
            if abs(swipe_vector.y) > self.min_swipe_distance and abs(swipe_vector.y) > abs(swipe_vector.x):
                if swipe_vector.y > 0:  
                    if self.current == 'login':
                        self.transition.direction = 'up'
                        self.current = 'register'
                        return True
                else:  
                    if self.current == 'register':
                        self.transition.direction = 'down'
                        self.current = 'login'
                        return True
            if abs(swipe_vector.x) > self.min_swipe_distance and abs(swipe_vector.x) > abs(swipe_vector.y):
                if swipe_vector.x > 0:  
                    for screen in ["personal_docs","transport_docs","vehicul_docs",'diverse_docs','camera_scan','chat','settings','save_data']:
                        if self.current == screen:
                            self.transition.direction = 'right'
                            self.current = 'home'
                            return True
                    if self.current == 'account_info':
                        self.transition.direction = 'right'
                        self.current = 'settings'
                        return True
                    if self.current == 'security' or self.current=='account_info':
                        self.transition.direction = 'right'
                        self.current = 'settings'
                        return True
                    if self.current=='identity_card':
                        self.transition.direction = 'right'
                        self.current = 'personal_docs'
                        return True
                else:
                    for screen in ["personal_docs","transport_docs","vehicul_docs",'diverse_docs','camera_scan','chat','settings','save_data']:
                        if self.current == screen:
                            self.transition.direction = 'left'
                            self.current = 'home'
                            return True
                    if self.current == 'account_info' or self.current=='account_info':
                        self.transition.direction = 'left'
                        self.current = 'settings'
                        return True
                    if self.current == 'security':
                        self.transition.direction = 'left'
                        self.current = 'settings'
                        return True
                    if self.current=='identity_card':
                        self.transition.direction = 'left'
                        self.current = 'personal_docs'
                        return True
                            
        return super().on_touch_up(touch)


class SmartIdApp(MDApp):
    def build(self):
        self.title = 'Smart Identity Wallet'
        self.server = ServerConnection(size_hint_y=0.8)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
                
        sm = SwipeScreenManager()
        sm.add_widget(ServerSetupScreen(self.server))
        sm.add_widget(SplashScreen(self.server))
        sm.add_widget(LoginScreen(self.server))
        sm.add_widget(RegisterScreen(self.server))
        sm.add_widget(HomeScreen(sm=sm, server=self.server))
        sm.add_widget(PersonalDocsScreen(self.server))
        sm.add_widget(VehiculDocsScreen(self.server))
        sm.add_widget(TransportDocsScreen(self.server))
        sm.add_widget(DiverseDocsScreen(self.server))
        sm.add_widget(CameraScanScreen(self.server))
        sm.add_widget(ChatScreen(self.server))
        sm.add_widget(IDScreen(self.server))
        sm.add_widget(SettingsScreen(self.server))
        sm.add_widget(AccountInfoScreen(self.server))
        sm.add_widget(SecurityScreen(self.server))
        sm.add_widget(SaveScreen(self.server))
        sm.current = 'server_setup'
        
        Window.bind(on_key_down=self._on_key_down)
        
        return sm
    
    def on_start(self):
        super().on_start()
        if platform == "android":
            permissions_to_request = [Permission.CAMERA]
            
            # For Android 13+ (API 33+), we need READ_MEDIA_IMAGES instead of READ_EXTERNAL_STORAGE
            if hasattr(Permission, 'READ_MEDIA_IMAGES'):
                permissions_to_request.append(Permission.READ_MEDIA_IMAGES)
            else:
                # Fallback for older Android versions
                permissions_to_request.extend([
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                ])
            
            request_permissions(permissions_to_request)
    
    def _on_key_down(self, window, key, scancode, codepoint, modifier):
        if key == 274: 
            if self.root.current == 'login':
                self.root.transition.direction = 'up'
                self.root.current = 'register'
            return True
        elif key == 273: 
            
            if self.root.current == 'register':
                self.root.transition.direction = 'down'
                self.root.current = 'login'
            return True

      
        return False

  
