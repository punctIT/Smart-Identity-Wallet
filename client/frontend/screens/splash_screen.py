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
      
      
class SplashScreen(Screen):
    def __init__(self,server,**kwargs):
        super().__init__(name='first', **kwargs)
        self.server=server
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Titlu
        title = Label(
            text='SMART ID', 
            font_size='24sp',
            size_hint_y=0.2,
            color=(0.2, 0.6, 1, 1)
        )
     
        layout.add_widget(title)

        self.add_widget(layout)
    def on_enter(self):
        
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.go_login(), 2)
    def set_server(self,server):
        self.server=server
    def go_next(self, *args):
        self.manager.current = 'login'
    def go_login(self):
        if self.server.connect() != None:
            self.go_next()
        else:
            print("nu e connectat")

