from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from kivy.uix.widget import Widget
from kivy.metrics import dp, sp


from frontend.screens.widgets.custom_background import GradientBackground
from frontend.screens.widgets.custom_buttons import CustomButton
from frontend.screens.widgets.custom_input import CustomInput
from frontend.screens.widgets.custom_label import CustomLabels,LinkLabel 
from frontend.screens.widgets.custom_alignment import Alignment

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


class RegisterScreen(Screen,CustomButton,CustomInput,CustomLabels,Alignment):
    def open_success_popup(self, username: str):
        box = BoxLayout(orientation='vertical', spacing=dp(14), padding=[dp(20)]*4)

        msg = Label(
            text=f"[b]Registration complete![/b]\nWelcome, [color=#8FB9FF]{username}[/color].",
            markup=True, color=TEXT_PRIMARY,
            halign="center", valign="middle",
            size_hint=(1, None), font_size=sp(16)
        )
        msg.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        msg.texture_update()
        msg.height = max(dp(60), msg.texture_size[1] + dp(4))

        ok_btn = self.make_rounded_button("OK", ACCENT_SOFT, lambda *_: popup.dismiss())

        box.add_widget(msg)
        box.add_widget(self.center_row(ok_btn, rel_width=0.5, height=dp(46), min_w=dp(160), max_w=dp(260)))

        popup = Popup(
            title="Success",
            content=box,
            size_hint=(0.8, None),
            height=dp(220),
            auto_dismiss=False,
            separator_color=(1, 1, 1, 0.08)
        )
        popup.bind(on_dismiss=lambda *_: self.go_prev())
        popup.open()

    def __init__(self, server, **kwargs):
        super().__init__(name='register', **kwargs)
        self.server = server

        # Background
        self.bg = GradientBackground()
        self.add_widget(self.bg)

        # Card container
        outer = AnchorLayout(anchor_x='center', anchor_y='center')
        self.add_widget(outer)

        card = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(22), dp(22), dp(22), dp(22)],
            size_hint=(None, None)
        )
        card.bind(minimum_height=card.setter('height'))

        with card.canvas.before:
            Color(*CARD_BG); self.card_bg = RoundedRectangle(radius=[dp(20)]*4)
        with card.canvas.after:
            Color(*CARD_STROKE); self.card_border = RoundedRectangle(radius=[dp(20)]*4)

        def _sync_bg(*_):
            self.card_bg.pos = card.pos; self.card_bg.size = card.size
            self.card_border.pos = (card.x - 0.5, card.y - 0.5)
            self.card_border.size = (card.width + 1, card.height + 1)
        card.bind(pos=_sync_bg, size=_sync_bg)

        subtitle = Label(
            text='[b][color=#BBD3FF]Register[/color][/b]',
            markup=True, font_size=sp(32),
            size_hint=(1, None), height=dp(34),
            color=TEXT_PRIMARY
        )

        # error label helpers
        def make_error_label():
            lbl = Label(text='', color=(1, 0.35, 0.4, 1),
                        size_hint=(1, None), height=0,
                        font_size=sp(13), halign='left', valign='middle')
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

        # Inputs
        self.username_box, self.username_input = self.make_rounded_input('Enter username')
        self.password_box, self.password_input = self.make_rounded_input('Enter password', password=True)
        self.email_box,    self.email_input    = self.make_rounded_input('Enter email')
        self.phone_box,    self.phone_input    = self.make_rounded_input('Enter phone number')

        # Error labels
        self.err_user  = make_error_label()
        self.err_pass  = make_error_label()
        self.err_email = make_error_label()
        self.err_phone = make_error_label()

        # Actions
        register_btn = self.make_rounded_button("Register", ACCENT_SOFT, self.go_register)
        info_label = LinkLabel(
            text="[color=#9FB4D9]Already registered?[/color] "
                 "[color=#3F86FF][b]Log in now[/b][/color]",
            markup=True, font_size=sp(15), size_hint_y=None,
            halign="center", valign="middle", color=TEXT_SECONDARY
        )
        info_label.bind(
            size=lambda lbl, size: setattr(lbl, "text_size", (size[0], None)),
            texture_size=lambda lbl, size: setattr(lbl, "height", size[1])
        )
        info_label.bind(on_press=lambda *_: self.go_prev())

        # Layout
        card.add_widget(subtitle)

        card.add_widget(self.center_row(self.err_user,  rel_width=0.85, height=self.err_user.height))
        card.add_widget(self.center_row(self.username_box, rel_width=0.85, height=dp(46)))

        card.add_widget(self.center_row(self.err_pass,  rel_width=0.85, height=self.err_pass.height))
        card.add_widget(self.center_row(self.password_box, rel_width=0.85, height=dp(46)))

        card.add_widget(self.center_row(self.err_email, rel_width=0.85, height=self.err_email.height))
        card.add_widget(self.center_row(self.email_box,   rel_width=0.85, height=dp(46)))

        card.add_widget(self.center_row(self.err_phone, rel_width=0.85, height=self.err_phone.height))
        card.add_widget(self.center_row(self.phone_box,  rel_width=0.85, height=dp(46)))

        card.add_widget(self.center_row(register_btn, rel_width=0.65, height=dp(46), min_w=dp(200), max_w=dp(420)))
        card.add_widget(Widget(size_hint_y=None, height=dp(20)))
        card.add_widget(info_label)

        outer.add_widget(card)

        
        def update_layout(*_):
            target_w = self._clamp(Window.width * 0.92, dp(320), dp(720))
            card.width = target_w
            outer.padding = [0, 0, 0, int(Window.height * 0.01)]
        update_layout()
        Window.bind(size=lambda *_: update_layout())
        self._set_error = set_error
        
    def go_prev(self, *_):
        if self.manager:
            self.manager.current = 'login'

    def go_register(self, *_):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        email    = self.email_input.text.strip()
        phone    = self.phone_input.text.strip()

        # clear previous errors
        self._set_error(self.err_user,  '')
        self._set_error(self.err_pass,  '')
        self._set_error(self.err_email, '')
        self._set_error(self.err_phone, '')

        # validation
        has_error = False
        if not username:
            self._set_error(self.err_user, "Username is required."); has_error = True
        if not password:
            self._set_error(self.err_pass, "Password is required."); has_error = True
        if not email:
            self._set_error(self.err_email, "Email is required."); has_error = True
        elif '@' not in email or '.' not in email.split('@')[-1]:
            self._set_error(self.err_email, "Please enter a valid email address."); has_error = True
        if not phone:
            self._set_error(self.err_phone, "Phone number is required."); has_error = True
        elif not phone.replace(' ', '').replace('+', '').isdigit():
            self._set_error(self.err_phone, "Phone should contain only digits (and optional +)."); has_error = True

        if has_error:
            return

        # call server
        if self.server and self.server.send_register_request(username, password, email, phone) is not None:
            self.open_success_popup(username)
        else:
            self._set_error(self.err_user, "Could not connect to server. Please try again.")