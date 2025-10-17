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

BG_TOP      = (0.06, 0.07, 0.10, 1)
BG_BOTTOM   = (0.03, 0.05, 0.09, 1)
CARD_BG     = (0.13, 0.15, 0.20, 1)
CARD_STROKE = (1, 1, 1, 0.06)

TEXT_PRIMARY   = (0.92, 0.95, 1.00, 1)
TEXT_SECONDARY = (0.70, 0.76, 0.86, 1)
ACCENT         = (0.25, 0.60, 1.00, 1)
ACCENT_SOFT    = (0.12, 0.35, 0.70, 1)

INPUT_BG     = (0.18, 0.20, 0.25, 1)
INPUT_TEXT   = TEXT_PRIMARY
INPUT_HINT   = (0.60, 0.66, 0.76, 1)

Window.clearcolor = BG_BOTTOM

def make_rounded_button(text, color, on_press_callback):
    btn = Button(
        text=text,
        font_size='16sp',
        size_hint=(0.65, None),
        height=46,
        pos_hint={'center_x': 0.5},
        background_color=(0, 0, 0, 0),
        background_normal='',
        color=(1, 1, 1, 1)
    )
    with btn.canvas.before:
        btn._bg_color = Color(*color)
        btn.bg = RoundedRectangle(radius=[20, 20, 20, 20])

    def update_bg(*_):
        btn.bg.pos = btn.pos
        btn.bg.size = btn.size

    # subtle press darken effect
    def on_state(_btn, state):
        if state == 'down':
            btn._bg_color.rgba = (color[0]*0.85, color[1]*0.85, color[2]*0.85, color[3])
        else:
            btn._bg_color.rgba = color

    btn.bind(pos=update_bg, size=update_bg)
    btn.bind(on_press=on_press_callback)
    btn.bind(state=on_state)
    return btn

class GradientBackground(BoxLayout):
    def __init__(self, color_top=BG_TOP, color_bottom=BG_BOTTOM, **kwargs):
        super().__init__(**kwargs)
        self.color_top = color_top
        self.color_bottom = color_bottom
        with self.canvas:
            self.rect = Rectangle()
        self._build_texture()
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _build_texture(self):
        h = 128
        tex = Texture.create(size=(1, h), colorfmt='rgba')
        buf = bytearray()
        r1, g1, b1, a1 = self.color_top
        r2, g2, b2, a2 = self.color_bottom
        for i in range(h):
            t = i / (h - 1)
            r = int((r1 * (1 - t) + r2 * t) * 255)
            g = int((g1 * (1 - t) + g2 * t) * 255)
            b = int((b1 * (1 - t) + b2 * t) * 255)
            a = int((a1 * (1 - t) + a2 * t) * 255)
            buf += bytes((r, g, b, a))
        tex.blit_buffer(bytes(buf), colorfmt='rgba', bufferfmt='ubyte')
        tex.wrap = 'repeat'
        self.rect.texture = tex
        self.rect.tex_coords = (0, 0, 1, 0, 1, 1, 0, 1)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class LinkLabel(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_text = kwargs.get("text", "")
        self.bind(on_press=self.on_press_effect, on_release=self.on_release_effect)

    def on_press_effect(self, *_):
        # Slight darken effect on hex colors used below
        darker = (self.original_text
                  .replace("#9FB4D9", "#7C97C8")
                  .replace("#3F86FF", "#2E66CC"))
        self.text = darker

    def on_release_effect(self, *_):
        self.text = self.original_text

class LoginScreen(Screen):
    def __init__(self, server=None, **kwargs):
        super().__init__(name='login', **kwargs)
        self.server = server

        # Background gradient
        self.bg = GradientBackground()
        self.add_widget(self.bg)

        # Top title
        top_anchor = AnchorLayout(anchor_x='center', anchor_y='top')
        title = Label(
            text='[b][color=#BBD3FF]SMART[/color] '
                 '[color=#8FB9FF]ID[/color] '
                 '[color=#BBD3FF]WALLET[/color][/b]',
            markup=True,
            font_size='32sp',
            size_hint=(None, None),
            height=60,
            color=TEXT_PRIMARY
        )
        top_anchor.add_widget(title)
        self.add_widget(top_anchor)

        # Center card
        outer = AnchorLayout(anchor_x='center', anchor_y='center')
        self.add_widget(outer)

        card = BoxLayout(
            orientation='vertical',
            spacing=14,
            padding=[22, 22, 22, 22],
            size_hint=(0.9, None)
        )
        card.bind(minimum_height=card.setter('height'))

        with card.canvas.before:
            Color(*CARD_BG)
            self.card_bg = RoundedRectangle(radius=[20, 20, 20, 20])
        with card.canvas.after:
            Color(*CARD_STROKE)
            self.card_border = RoundedRectangle(radius=[20, 20, 20, 20])

        def _sync_bg(*_):
            self.card_bg.pos = card.pos
            self.card_bg.size = card.size
            # slight halo border
            self.card_border.pos = (card.x - 0.5, card.y - 0.5)
            self.card_border.size = (card.width + 1, card.height + 1)

        card.bind(pos=_sync_bg, size=_sync_bg)

        subtitle = Label(
            text='[b][color=#BBD3FF]Log[/color] [color=#8FB9FF]in[/color][/b]',
            markup=True,
            font_size='28sp',
            size_hint=(1, None),
            height=34,
            color=TEXT_PRIMARY
        )

        self.username_input = TextInput(
            hint_text='Enter username', multiline=False,
            size_hint=(0.85, None), height=42,
            pos_hint={'center_x': 0.5}, padding=(10, 10),
            background_color=INPUT_BG,
            foreground_color=INPUT_TEXT,
            cursor_color=ACCENT,
            hint_text_color=INPUT_HINT
        )
        self.password_input = TextInput(
            hint_text='Enter password', password=True, multiline=False,
            size_hint=(0.85, None), height=42,
            pos_hint={'center_x': 0.5}, padding=(10, 10),
            background_color=INPUT_BG,
            foreground_color=INPUT_TEXT,
            cursor_color=ACCENT,
            hint_text_color=INPUT_HINT
        )

        login_btn = make_rounded_button("Login", ACCENT_SOFT, self.go_login)

        info_label = LinkLabel(
            text="[color=#9FB4D9]Not registered?[/color] "
                 "[color=#3F86FF][b]Register now[/b][/color]",
            markup=True,
            font_size="15sp",
            size_hint_y=None,
            halign="center",
            valign="middle",
            color=TEXT_SECONDARY
        )
        info_label.bind(
            size=lambda lbl, size: setattr(lbl, "text_size", (size[0], None)),
            texture_size=lambda lbl, size: setattr(lbl, "height", size[1])
        )
        info_label.bind(on_press=lambda *_: self.go_next())

        for w in (
            subtitle,
            self.username_input,
            self.password_input,
            login_btn,
            Widget(size_hint_y=None, height=25),
            info_label
        ):
            card.add_widget(w)

        outer.add_widget(card)

        # Dynamic offsets
        def update_layout(*_):
            top_anchor.padding = [0, int(Window.height * 0.08), 0, 0]
            outer.padding = [0, 0, 0, int(Window.height * 0.01)]

        update_layout()
        Window.bind(size=lambda *_: update_layout())

    def set_server(self, server):
        self.server = server

    def go_next(self, *_):
        if self.manager:
            self.manager.current = 'register'

    def go_login(self, *_):
        username = self.username_input.text.strip()
        password = self.password_input.text
        if not username or not password:
            print("Completează utilizatorul și parola.")
            return
        if self.server and self.server.send_login(username, password) is not None:
            self.go_next()
        else:
            print("nu e conectat")
