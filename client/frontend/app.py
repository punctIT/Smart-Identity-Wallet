from kivy.config import Config

Config.set('graphics', 'width', '675')
Config.set('graphics', 'height', '1200')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.vector import Vector


from backend.server_connect import ServerConnection
from frontend.screens.login_screen import LoginScreen
from frontend.screens.register_screen import RegisterScreen
from frontend.screens.splash_screen import SplashScreen

class SwipeScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition(direction='up', duration=0.2)
        
        # Variabile pentru swipe
        self.touch_start_pos = None
        self.min_swipe_distance = 100
        
    def on_touch_down(self, touch):
        self.touch_start_pos = touch.pos
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if self.touch_start_pos:
            # Calculează distanța swipe-ului
            swipe_vector = Vector(touch.pos) - Vector(self.touch_start_pos)
            
            # Verifică dacă e swipe horizontal suficient de lung
            if abs(swipe_vector.y) > self.min_swipe_distance and abs(swipe_vector.y) > abs(swipe_vector.x):
                if swipe_vector.y > 0:  # Swipe dreapta
                    if self.current == 'first':
                        self.transition.direction = 'up'
                        self.current = 'second'
                        return True
                else:  # Swipe stânga
                    if self.current == 'second':
                        self.transition.direction = 'down'
                        self.current = 'first'
                        return True
        
        return super().on_touch_up(touch)


class SmartIdApp(App):
    def build(self):
       
        self.title = 'Aplicație cu Swipe'
        self.server = ServerConnection(size_hint_y=0.8)
                
        sm = SwipeScreenManager()
        sm.add_widget(SplashScreen(self.server))
        sm.add_widget(LoginScreen(self.server))
        sm.add_widget(RegisterScreen(self.server))

        sm.current = 'first'
        
        # Suport pentru taste (opțional)
        Window.bind(on_key_down=self._on_key_down)
        
        return sm
    
    def _on_key_down(self, window, key, scancode, codepoint, modifier):
        # Folosește săgețile pentru navigare
        if key == 275:  # Săgeată dreapta
            if self.root.current == 'first':
                self.root.transition.direction = 'up'
                self.root.current = 'second'
            return True
        elif key == 276:  # Săgeată stânga
            if self.root.current == 'second':
                self.root.transition.direction = 'down'
                self.root.current = 'first'
            return True

        # Return False to allow other widgets (e.g., TextInput) to handle keys like backspace
        return False

  
