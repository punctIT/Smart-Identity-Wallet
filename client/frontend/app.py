from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from kivy.vector import Vector


from backend.server_connect import ServerConnection
from frontend.screens.home_screen.home_screen import HomeScreen
from frontend.screens.login_screen import LoginScreen
from frontend.screens.home_screen.personal_docs_screen import PersonalDocsScreen
from frontend.screens.home_screen.vehicul_docs_screen import VehiculDocsScreen
from frontend.screens.home_screen.transport_docs_screen import TransportDocsScreen
from frontend.screens.home_screen.diverse_docs_screen import DiverseDocsScreen
from frontend.screens.home_screen.scan_camera_screen import CameraScanScreen
from frontend.screens.register_screen import RegisterScreen
from frontend.screens.splash_screen import SplashScreen

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
                    for screen in ["personal_docs","transport_docs","vehicul_docs",'diverse_docs','camera_scan']:
                        if self.current == screen:
                            self.transition.direction = 'right'
                            self.current = 'home'
                            return True

        
        return super().on_touch_up(touch)


class SmartIdApp(App):
    def build(self):
       
        self.title = 'Smart Identity Wallet'
        self.server = ServerConnection(size_hint_y=0.8)
                
        sm = SwipeScreenManager()
        sm.add_widget(SplashScreen(self.server))
        sm.add_widget(LoginScreen(self.server))
        sm.add_widget(RegisterScreen(self.server))
        sm.add_widget(HomeScreen(sm=sm, server=self.server))
        sm.add_widget(PersonalDocsScreen(self.server))
        sm.add_widget(VehiculDocsScreen(self.server))
        sm.add_widget(TransportDocsScreen(self.server))
        sm.add_widget(DiverseDocsScreen(self.server))
        sm.add_widget(CameraScanScreen(self.server))
       

        sm.current = 'first'
        
        Window.bind(on_key_down=self._on_key_down)
        
        return sm
    
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

  
