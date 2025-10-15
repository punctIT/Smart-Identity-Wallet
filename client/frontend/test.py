from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.vector import Vector

class FirstScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name='first', **kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Titlu
        title = Label(
            text='Prima Fereastră', 
            font_size='24sp',
            size_hint_y=0.2,
            color=(0.2, 0.6, 1, 1)
        )
        
        # Conținut
        content = Label(
            text='Aceasta este prima fereastră.\n\nSwipe dreapta sau apasă butonul\npentru a merge la următoarea.',
            font_size='16sp',
            halign='center',
            text_size=(None, None)
        )
        content.bind(size=content.setter('text_size'))
        
        # Buton navigare
        next_btn = Button(
            text='→ Următoarea',
            size_hint_y=0.2,
            font_size='18sp',
            background_color=(0.2, 0.6, 1, 1)
        )
        next_btn.bind(on_press=self.go_next)
        
        layout.add_widget(title)
        layout.add_widget(content)
        layout.add_widget(next_btn)
        
        self.add_widget(layout)
    
    def go_next(self, *args):
        self.manager.current = 'second'

class SecondScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name='second', **kwargs)
        
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
        
        layout.add_widget(title)
        layout.add_widget(content)
        layout.add_widget(prev_btn)
        
        self.add_widget(layout)
    
    def go_back(self, *args):
        self.manager.current = 'first'

class SwipeScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition(duration=0.3)
        
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
            if abs(swipe_vector.x) > self.min_swipe_distance and abs(swipe_vector.x) > abs(swipe_vector.y):
                if swipe_vector.x > 0:  # Swipe dreapta
                    if self.current == 'first':
                        self.transition.direction = 'left'
                        self.current = 'second'
                        return True
                else:  # Swipe stânga
                    if self.current == 'second':
                        self.transition.direction = 'right'
                        self.current = 'first'
                        return True
        
        return super().on_touch_up(touch)

class SwipeApp(App):
    def build(self):
        # Setează titlul ferestrei
        self.title = 'Aplicație cu Swipe'
        
        # Creează screen manager-ul
        sm = SwipeScreenManager()
        
        # Adaugă ecranele
        sm.add_widget(FirstScreen())
        sm.add_widget(SecondScreen())
        
        # Setează primul ecran ca activ
        sm.current = 'first'
        
        # Suport pentru taste (opțional)
        Window.bind(on_key_down=self._on_key_down)
        
        return sm
    
    def _on_key_down(self, window, key, scancode, codepoint, modifier):
        # Folosește săgețile pentru navigare
        if key == 275:  # Săgeată dreapta
            if self.root.current == 'first':
                self.root.transition.direction = 'left'
                self.root.current = 'second'
        elif key == 276:  # Săgeată stânga
            if self.root.current == 'second':
                self.root.transition.direction = 'right'
                self.root.current = 'first'
        return True

if __name__ == '__main__':
    SwipeApp().run()