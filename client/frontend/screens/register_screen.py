from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.vector import Vector

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
        size_hint=(None, None),   # <-- no horizontal stretching; we'll set width via wrapper
        height=46,
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

    def on_state(_btn, state):
        if state == 'down':
            btn._bg_color.rgba = (color[0]*0.85, color[1]*0.85, color[2]*0.85, color[3])
        else:
            btn._bg_color.rgba = color

    btn.bind(pos=update_bg, size=update_bg)
    btn.bind(on_press=on_press_callback)
    btn.bind(state=on_state)
    return btn

# --- rounded TextInput wrapper with focus outline ---
def make_rounded_input(hint_text, *, password=False):
    wrapper = AnchorLayout(size_hint=(None, None), height=46, anchor_x='center', anchor_y='center')

    with wrapper.canvas.before:
        wrapper._fill = Color(*INPUT_BG)
        wrapper._bg = RoundedRectangle(radius=[12, 12, 12, 12])
        wrapper._outline_color = Color(1, 1, 1, 0.08)
        wrapper._outline = RoundedRectangle(radius=[12, 12, 12, 12])

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
        padding=(12, 12),
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

# --- NEW: center a child at a relative width of its parent ---
def center_row(child, *, rel_width=0.85, height=None):
    row = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, None),
                       height=height if height is not None else child.height)
    # make child fixed-width inside the row; width tracks a fraction of row width
    child.size_hint_x = None
    def _bind_width(_row, _val):
        child.width = row.width * rel_width
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

class RegisterScreen(Screen):
    def open_success_popup(self, username: str):
        # Content
        box = BoxLayout(orientation='vertical', spacing=14, padding=[20, 18, 20, 18])

        msg = Label(
            text=f"[b]Registration complete![/b]\nWelcome, [color=#8FB9FF]{username}[/color].",
            markup=True,
            color=TEXT_PRIMARY,
            halign="center",
            valign="middle",
            size_hint=(1, None)
        )
        msg.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        msg.texture_update()
        msg.height = max(60, msg.texture_size[1] + 4)

        ok_btn = make_rounded_button("OK", ACCENT_SOFT, lambda *_: popup.dismiss())

        # center the button nicely
        box.add_widget(msg)
        box.add_widget(center_row(ok_btn, rel_width=0.5, height=46))

        popup = Popup(
            title="Success",
            content=box,
            size_hint=(0.8, None),
            height=220,
            auto_dismiss=False,
            separator_color=(1, 1, 1, 0.08)
        )
    # when the popup closes, go back to login
        popup.bind(on_dismiss=lambda *_: self.go_prev())
        popup.open()

    def __init__(self, server, **kwargs):
        super().__init__(name='register', **kwargs)
        self.server = server
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Background
        self.bg = GradientBackground()
        self.add_widget(self.bg)

        # Center card
        outer = AnchorLayout(anchor_x='center', anchor_y='center')
        self.add_widget(outer)

        card = BoxLayout(
            orientation='vertical',
            spacing=10,                # a hair tighter so errors fit nicely
            padding=[22, 22, 22, 22],
            size_hint=(0.9, None)
        )
        card.bind(minimum_height=card.setter('height'))

        with card.canvas.before:
            Color(*CARD_BG); self.card_bg = RoundedRectangle(radius=[20, 20, 20, 20])
        with card.canvas.after:
            Color(*CARD_STROKE); self.card_border = RoundedRectangle(radius=[20, 20, 20, 20])

        def _sync_bg(*_):
            self.card_bg.pos = card.pos; self.card_bg.size = card.size
            self.card_border.pos = (card.x - 0.5, card.y - 0.5)
            self.card_border.size = (card.width + 1, card.height + 1)
        card.bind(pos=_sync_bg, size=_sync_bg)

        subtitle = Label(
            text='[b][color=#BBD3FF]Register[/color][/b]',
            markup=True, font_size='32sp', size_hint=(1, None), height=34, color=TEXT_PRIMARY
        )

        # ---- Helpers for error labels ----
        def make_error_label():
            # starts hidden (height=0). set text to show, clear text to hide
            lbl = Label(text='', color=(1, 0.35, 0.4, 1),          # soft red
                        size_hint=(1, None), height=0,             # hidden by default
                        font_size='13sp', halign='left', valign='middle')
            # enable wrapping to row width
            lbl.bind(size=lambda l, s: setattr(l, 'text_size', (s[0], None)))
            return lbl

        def set_error(lbl, message: str):
            if message:
                lbl.text = message
                # compute natural height from texture; add small padding
                lbl.texture_update()
                lbl.height = max(18, lbl.texture_size[1] + 2)
            else:
                lbl.text = ''
                lbl.height = 0

        # Rounded inputs
        self.username_box, self.username_input = make_rounded_input('Enter username')
        self.password_box, self.password_input = make_rounded_input('Enter password', password=True)
        self.email_box,    self.email_input    = make_rounded_input('Enter email')
        self.phone_box,    self.phone_input    = make_rounded_input('Enter phone number')

        # Error labels (one per field)
        self.err_user  = make_error_label()
        self.err_pass  = make_error_label()
        self.err_email = make_error_label()
        self.err_phone = make_error_label()

        register_btn = make_rounded_button("Register", ACCENT_SOFT, self.go_register)

        info_label = LinkLabel(
            text="[color=#9FB4D9]Already registered?[/color] "
                 "[color=#3F86FF][b]Log in now[/b][/color]",
            markup=True, font_size="15sp", size_hint_y=None,
            halign="center", valign="middle", color=TEXT_SECONDARY
        )
        info_label.bind(
            size=lambda lbl, size: setattr(lbl, "text_size", (size[0], None)),
            texture_size=lambda lbl, size: setattr(lbl, "height", size[1])
        )
        info_label.bind(on_press=lambda *_: self.go_prev())

        # ---------- centered rows inside the card ----------
        card.add_widget(subtitle)

        # username
        card.add_widget(center_row(self.err_user, rel_width=0.85, height=self.err_user.height))
        card.add_widget(center_row(self.username_box, rel_width=0.85, height=46))

        # password
        card.add_widget(center_row(self.err_pass, rel_width=0.85, height=self.err_pass.height))
        card.add_widget(center_row(self.password_box, rel_width=0.85, height=46))

        # email
        card.add_widget(center_row(self.err_email, rel_width=0.85, height=self.err_email.height))
        card.add_widget(center_row(self.email_box, rel_width=0.85, height=46))

        # phone
        card.add_widget(center_row(self.err_phone, rel_width=0.85, height=self.err_phone.height))
        card.add_widget(center_row(self.phone_box, rel_width=0.85, height=46))

        card.add_widget(center_row(register_btn, rel_width=0.65, height=46))
        card.add_widget(Widget(size_hint_y=None, height=20))
        card.add_widget(info_label)

        outer.add_widget(card)

        # Dynamic offsets
        def update_layout(*_):
            outer.padding = [0, 0, 0, int(Window.height * 0.01)]
        update_layout()
        Window.bind(size=lambda *_: update_layout())

        # expose helpers on self for reuse in go_login
        self._set_error = set_error

    def set_server(self, server):
        self.server = server

    def go_prev(self, *_):
        if self.manager:
            self.manager.current = 'login'

    def go_register(self, *_):
    # read values
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        email    = self.email_input.text.strip()
        phone    = self.phone_input.text.strip()

    # clear previous errors
        self._set_error(self.err_user,  '')
        self._set_error(self.err_pass,  '')
        self._set_error(self.err_email, '')
        self._set_error(self.err_phone, '')

    # simple validation
        has_error = False
        if not username:
            self._set_error(self.err_user, "Username is required.")
            has_error = True
        if not password:
            self._set_error(self.err_pass, "Password is required.")
            has_error = True
        if not email:
            self._set_error(self.err_email, "Email is required.")
            has_error = True
        elif '@' not in email or '.' not in email.split('@')[-1]:
            self._set_error(self.err_email, "Please enter a valid email address.")
            has_error = True
        if not phone:
            self._set_error(self.err_phone, "Phone number is required.")
            has_error = True
        elif not phone.replace(' ', '').replace('+', '').isdigit():
            self._set_error(self.err_phone, "Phone should contain only digits (and optional +).")
            has_error = True

        if has_error:
            return

    # send registration request
        if self.server and self.server.send_register_request(username, password, email, phone) is not None:
            self.open_success_popup(username)
        else:
            self._set_error(self.err_user, "Could not connect to server. Please try again.")
