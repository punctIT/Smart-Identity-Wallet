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


class Alignment:
    def __init__(self):
        pass
    def _clamp(self,val, lo, hi):
        return max(lo, min(hi, val))

    def center_row(self,child, *, rel_width=0.85, min_w=dp(260), max_w=dp(520), height=None):
        row = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, None),
                        height=height if height is not None else (child.height or dp(46)))
        child.size_hint_x = None
        def _bind_width(_row, _val):
            target = self._clamp(row.width * rel_width, min_w, max_w)
            child.width = target
        row.bind(width=_bind_width)
        row.add_widget(child)
        return row
