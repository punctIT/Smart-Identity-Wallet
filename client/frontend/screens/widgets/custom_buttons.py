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



class CustomButton:
    def __init__(self):
        pass
    def make_rounded_button(self,text, color, on_press_callback):
        btn = Button(
            text=text,
            font_size=sp(16),
            size_hint=(None, None),
            height=dp(46),
            background_color=(0, 0, 0, 0),
            background_normal='',
            color=(1, 1, 1, 1)
        )
        with btn.canvas.before:
            btn._bg_color = Color(*color)
            btn.bg = RoundedRectangle(radius=[dp(20)]*4)

        def update_bg(*_):
            btn.bg.pos = btn.pos
            btn.bg.size = btn.size

        def on_state(_btn, state):
            if state == 'down':
                btn._bg_color.rgba = (color[0]*0.85, color[1]*0.85, color[2]*0.85, color[3])
            else:
                btn._bg_color.rgba = color

        btn.bind(pos=update_bg, size=update_bg)
        btn.bind(on_press=on_press_callback)
        btn.bind(state=on_state)
        return btn