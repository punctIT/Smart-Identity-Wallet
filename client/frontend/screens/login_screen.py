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
from kivy.metrics import dp, sp  # <-- responsive units

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

# ---------- utilities ----------
def _clamp(val, lo, hi):
    return max(lo, min(hi, val))

def make_rounded_button(text, color, on_press_callback):
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

# rounded TextInput wrapper with focus outline
def make_rounded_input(hint_text, *, password=False):
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

# center a child at a relative width with min/max clamps (all dp)
def center_row(child, *, rel_width=0.85, min_w=dp(260), max_w=dp(520), height=None):
    row = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, None),
                       height=height if height is not None else (child.height or dp(46)))
    child.size_hint_x = None

    def _bind_width(_row, _val):
        target = _clamp(row.width * rel_width, min_w, max_w)
        child.width = target
    row.bind(width=_bind_width)
    row.add_widget(child)
    return row

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
            font_size=sp(32),
            size_hint=(None, None),
            height=dp(60),
            color=TEXT_PRIMARY
        )
        top_anchor.add_widget(title)
        self.add_widget(top_anchor)

        # Center card
        outer = AnchorLayout(anchor_x='center', anchor_y='center')
        self.add_widget(outer)

        card = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(22), dp(22), dp(22), dp(22)],
            size_hint=(None, None)  # we'll make width responsive below
        )
        # let height follow content
        card.bind(minimum_height=card.setter('height'))

        with card.canvas.before:
            Color(*CARD_BG)
            self.card_bg = RoundedRectangle(radius=[dp(20)]*4)
        with card.canvas.after:
            Color(*CARD_STROKE)
            self.card_border = RoundedRectangle(radius=[dp(20)]*4)

        def _sync_bg(*_):
            self.card_bg.pos = card.pos
            self.card_bg.size = card.size
            self.card_border.pos = (card.x - 0.5, card.y - 0.5)
            self.card_border.size = (card.width + 1, card.height + 1)
        card.bind(pos=_sync_bg, size=_sync_bg)

        subtitle = Label(
            text='[b][color=#BBD3FF]Log[/color] [color=#8FB9FF]in[/color][/b]',
            markup=True,
            font_size=sp(28),
            size_hint=(1, None),
            height=dp(34),
            color=TEXT_PRIMARY
        )

        # ---- helpers for error labels
        def make_error_label():
            lbl = Label(text='',
                        color=(1, 0.35, 0.4, 1),
                        size_hint=(1, None),
                        height=0,
                        font_size=sp(13),
                        halign='left',
                        valign='middle')
            lbl.bind(size=lambda l, s: setattr(l, 'text_size', (s[0], None)))
            return lbl

        def set_error(lbl, message: str):
            if message:
                lbl.text = message
                lbl.texture_update()
                lbl.height = max(dp(18), lbl.texture_size[1] + dp(2))
            else:
                lbl.text = ''
                lbl.height = 0

        # Rounded inputs
        self.username_box, self.username_input = make_rounded_input('Enter username')
        self.password_box, self.password_input = make_rounded_input('Enter password', password=True)

        # Error labels (one per field)
        self.err_user = make_error_label()
        self.err_pass = make_error_label()

        login_btn = make_rounded_button("Login", ACCENT_SOFT, self.go_login)

        info_label = LinkLabel(
            text="[color=#9FB4D9]Not registered?[/color] "
                 "[color=#3F86FF][b]Register now[/b][/color]",
            markup=True,
            font_size=sp(15),
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

        # ---------- centered rows inside the card ----------
        card.add_widget(subtitle)

        # username (error above field)
        card.add_widget(center_row(self.err_user,     rel_width=0.85, min_w=dp(260), max_w=dp(520), height=self.err_user.height))
        card.add_widget(center_row(self.username_box, rel_width=0.85, min_w=dp(260), max_w=dp(520), height=dp(46)))

        # password (error above field)
        card.add_widget(center_row(self.err_pass,     rel_width=0.85, min_w=dp(260), max_w=dp(520), height=self.err_pass.height))
        card.add_widget(center_row(self.password_box, rel_width=0.85, min_w=dp(260), max_w=dp(520), height=dp(46)))

        card.add_widget(center_row(login_btn, rel_width=0.65, min_w=dp(220), max_w=dp(420), height=dp(46)))
        card.add_widget(Widget(size_hint_y=None, height=dp(25)))
        card.add_widget(info_label)

        outer.add_widget(card)

        # ------- responsive sizing rules -------
        def update_layout(*_):
            # title padding ~8% of height
            top_anchor.padding = [0, int(Window.height * 0.08), 0, 0]

            # card width: 92% of window, clamped between 320dp and 720dp
            target_w = _clamp(Window.width * 0.92, dp(320), dp(720))
            card.width = target_w

            # keep a tiny bottom offset
            outer.padding = [0, 0, 0, int(Window.height * 0.01)]

        update_layout()
        Window.bind(size=lambda *_: update_layout())

        # expose error setter
        self._set_error = set_error

    def set_server(self, server):
        self.server = server

    def go_next(self, *_):
        if self.manager:
            self.manager.current = 'register'

    def go_login(self, *_):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        # clear previous errors
        self._set_error(self.err_user, '')
        self._set_error(self.err_pass, '')

        has_error = False
        if not username:
            self._set_error(self.err_user, "Username is required.")
            has_error = True
        if not password:
            self._set_error(self.err_pass, "Password is required.")
            has_error = True

        if has_error:
            return

        if not self.server:
            self._set_error(self.err_user, "Server connection unavailable.")
            return

        response = self.server.send_login(username, password)
        if response:
            if self.manager and self.manager.has_screen('home'):
                home = self.manager.get_screen('home')
                home.set_server(self.server)
                home.set_user_info(response.get('user_info'))
                self.manager.transition.direction = 'left'
                self.manager.current = 'home'
        else:
            message = getattr(self.server, "last_message", None) or "Could not connect to server. Please try again."
            self._set_error(self.err_user, message)
