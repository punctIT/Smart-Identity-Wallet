


from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp


BG_TOP      = (0.06, 0.07, 0.10, 1)
BG_BOTTOM   = (0.03, 0.05, 0.09, 1)
CARD_BG     = (0.13, 0.15, 0.20, 1)
CARD_STROKE = (1, 1, 1, 0.06)

TEXT_PRIMARY   = (0.92, 0.95, 1.00, 1)
TEXT_SECONDARY = (0.70, 0.76, 0.86, 1)
ACCENT         = (0.25, 0.60, 1.00, 1)
ACCENT_SOFT    = (0.12, 0.35, 0.70, 1)

ALLOW_LOGIN_BYPASS = True  # set False when real login is needed

INPUT_BG     = (0.18, 0.20, 0.25, 1)
INPUT_TEXT   = TEXT_PRIMARY
INPUT_HINT   = (0.60, 0.66, 0.76, 1)



class CustomInput:
    def __init__(self):
        pass
    def make_rounded_input(self,hint_text, *, password=False):
        wrapper = AnchorLayout(size_hint=(None, None), height=dp(46), anchor_x='center', anchor_y='center')

        with wrapper.canvas.before:
            wrapper._fill = Color(*INPUT_BG)
            wrapper._bg = RoundedRectangle(radius=[dp(12)]*4)
            wrapper._outline_color = Color(1, 1, 1, 0.08)
            wrapper._outline = RoundedRectangle(radius=[dp(12)]*4)

        def sync_bg(*_):
            wrapper._bg.pos = wrapper.pos
            wrapper._bg.size = wrapper.size
            wrapper._outline.pos = (wrapper.x - 0.5, wrapper.y - 0.5)
            wrapper._outline.size = (wrapper.width + 1, wrapper.height + 1)
        wrapper.bind(pos=sync_bg, size=sync_bg)

        ti = TextInput(
            hint_text=hint_text,
            password=password,
            multiline=False,
            size_hint=(1, 1),
            padding=(dp(12), dp(12)),
            background_color=(0, 0, 0, 0),
            foreground_color=INPUT_TEXT,
            cursor_color=ACCENT,
            hint_text_color=INPUT_HINT,
            write_tab=False
        )
        wrapper.add_widget(ti)

        def on_focus(_inst, focus):
            wrapper._outline_color.rgba = (ACCENT[0], ACCENT[1], ACCENT[2], 0.75) if focus else (1, 1, 1, 0.08)
        ti.bind(focus=on_focus)

        return wrapper, ti