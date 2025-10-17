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
      
      
class LoginScreen(Screen):
    def __init__(self,server,**kwargs):
        super().__init__(name='login', **kwargs)
        self.server=server
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Titlu
        title = Label(
            text='SMART ID', 
            font_size='24sp',
            size_hint_y=0.2,
            color=(0.2, 0.6, 1, 1)
        )
        self.username_input = TextInput(
            hint_text='Enter username',
            multiline=False
        )
        self.password_input = TextInput(
            hint_text='Enter password',
            password=True, 
            multiline=False
        )
        register_btn = Button(
            text='Register',
            size_hint_y=0.2,
            font_size='18sp',
            background_color=(0.2, 0.6, 1, 1)
        )
        register_btn.bind(on_press=self.go_next)
        login_btn = Button(
            text='Login',
            size_hint_y=0.2,
            font_size='18sp',
            background_color=(0.2, 0.6, 1, 1)
        )
        login_btn.bind(on_press=self.go_login)
       
        layout.add_widget(title)
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(register_btn)
        layout.add_widget(login_btn)
        
        self.add_widget(layout)
        
    def set_server(self,server):
        self.server=server
    def go_next(self, *args):
        self.manager.current = 'register'
    # def go_next(self, instance):
    #     self.server.send_specific_message("nimic",self.text_input.text)
    def go_login(self, instance):
        if self.server.send_login("admin","admin2025") != None:
            self.go_next()
        else:
            print("nu e connectat")

