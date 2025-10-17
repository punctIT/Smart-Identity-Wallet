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
from kivy.uix.image import Image
from pathlib import Path    
from kivy.uix.floatlayout import FloatLayout

ASSETS_DIR = Path(__file__).parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"

class SplashScreen(Screen):
    def __init__(self, server, **kwargs):
        super().__init__(name='first', **kwargs)
        self.server = server
        self.animation_event = None
        self.dot_index = 0
        self.status_base_text = 'Connecting to server'

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        logo = Image(source=str(LOGO_PATH), size_hint=(1, 0.5))
        
        title = Label(
            text='SMART ID',
            font_size='24sp',
            size_hint_y=0.2,
            color=(0.2, 0.6, 1, 1)
        )
        self.status_label = Label(
            text=self.status_base_text,
            font_size='18sp',
            size_hint_y=0.2,
            color=(0.9, 0.9, 0.9, 1)
        )

        layout.add_widget(title)
        layout.add_widget(self.status_label)
        layout.add_widget(logo)

        self.add_widget(layout)

    def on_pre_enter(self):
        self.set_status_message('Connecting to server', animate=False)
        self.dot_index = 0

    def on_enter(self):
        self.set_status_message('Connecting to server', animate=True)
        Clock.schedule_once(lambda dt: self.go_login(), 2)

    def on_leave(self):
        self.stop_status_animation()

    def set_server(self, server):
        self.server = server

    def go_next(self, *args):
        self.manager.current = 'login'

    def go_login(self):
        if self.server.connect() is not None:
            self.stop_status_animation()
            self.status_label.text = 'Connected! Redirecting...'
            Clock.schedule_once(lambda dt: self.go_next(), 0.5)
        else:
            self.set_status_message('Unable to connect. Retrying', animate=True)
            Clock.schedule_once(lambda dt: self.retry_connect(), 2)

    def retry_connect(self, *args):
        self.set_status_message('Reconnecting to server', animate=True)
        Clock.schedule_once(lambda dt: self.go_login(), 0)

    def set_status_message(self, text, animate=True):
        if animate:
            self.status_base_text = text
            self.dot_index = 0
            self.status_label.text = text
            self.start_status_animation()
        else:
            self.status_base_text = text
            self.stop_status_animation()
            self.status_label.text = text

    def start_status_animation(self):
        if self.animation_event is None:
            self.animation_event = Clock.schedule_interval(self._animate_status, 0.5)

    def stop_status_animation(self):
        if self.animation_event is not None:
            self.animation_event.cancel()
            self.animation_event = None

    def _animate_status(self, dt):
        self.dot_index = (self.dot_index + 1) % 4
        dots = '.' * self.dot_index
        self.status_label.text = f'{self.status_base_text}{dots}'

