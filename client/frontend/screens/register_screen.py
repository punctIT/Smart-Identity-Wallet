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

from kivy.uix.popup import Popup

class RegisterScreen(Screen):
    def __init__(self,server, **kwargs):
        super().__init__(name='register', **kwargs)
        self.server=server
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Titlu
        title = Label(
            text='A Doua Fereastră', 
            font_size='24sp',
            size_hint_y=0.2,
            color=(1, 0.4, 0.2, 1)
        )
        
        # Conținut
        content = Label(
            text='Aceasta este a doua fereastră.\n\nSwipe stânga sau apasă butonul\npentru a te întoarce.',
            font_size='16sp',
            halign='center',
            text_size=(None, None)
        )
        content.bind(size=content.setter('text_size'))
        
        # Buton navigare
        prev_btn = Button(
            text='← Înapoi',
            size_hint_y=0.2,
            font_size='18sp',
            background_color=(1, 0.4, 0.2, 1)
        )
        prev_btn.bind(on_press=self.go_back)
        btn = Button(text="Arată popup")
        btn.bind(on_press=lambda x: self.show_popup("Atenție", "Acesta este un mesaj!"))
        layout.add_widget(title)
        layout.add_widget(content)
        layout.add_widget(prev_btn)
        layout.add_widget(btn)
        self.add_widget(layout)
    
    def go_back(self, *args):
        self.manager.current = 'login'
    def show_popup(self, title, message):
        self.server.send_specific_message("nimic")
        # Layout pentru conținut
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Mesaj
        label = Label(text=message)
        content.add_widget(label)
        
        # Buton de închidere
        btn_close = Button(text="OK", size_hint_y=0.3)
        content.add_widget(btn_close)
        
        # Creează popup-ul
        popup = Popup(title=title,
                    content=content,
                    size_hint=(0.7, 0.4),  
                    auto_dismiss=False) 
        
        # Leagă butonul de închidere
        btn_close.bind(on_press=popup.dismiss)
        
        # Arată popup-ul
        popup.open()