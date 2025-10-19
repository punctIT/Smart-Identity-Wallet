
from kivy.uix.screenmanager import Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.graphics.texture import Texture
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.metrics import dp, sp 

class LinkLabel(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_text = kwargs.get("text", "")
        self.bind(on_press=self.on_press_effect, on_release=self.on_release_effect)

    def on_press_effect(self, *_):
        darker = (self.original_text
                  .replace("#9FB4D9", "#7C97C8")
                  .replace("#3F86FF", "#2E66CC"))
        self.text = darker

    def on_release_effect(self, *_):
        self.text = self.original_text
        
class CustomLabels:
    def make_error_label(self):
        lbl = Label(text='',
                    color=(1, 0.35, 0.4, 1),
                    size_hint=(1, None),
                    height=0,
                    font_size=sp(13),
                    halign='left',
                    valign='middle')
        lbl.bind(size=lambda l, s: setattr(l, 'text_size', (s[0], None)))
        return lbl