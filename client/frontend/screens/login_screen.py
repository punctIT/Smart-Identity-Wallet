from kivy.uix.screenmanager import Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.graphics.texture import Texture
from kivy.uix.widget import Widget
from kivy.core.window import Window
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

ALLOW_LOGIN_BYPASS = True 

INPUT_BG     = (0.18, 0.20, 0.25, 1)
INPUT_TEXT   = TEXT_PRIMARY
INPUT_HINT   = (0.60, 0.66, 0.76, 1)

Window.clearcolor = BG_BOTTOM



class LoginScreen(Screen,CustomLabels,CustomButton,CustomInput,Alignment):
    def on_enter(self, *args):
        self.server.log_out()
        return super().on_enter(*args)
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
            size_hint=(None, None) 
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

        def set_error(lbl, message: str):
            if message:
                lbl.text = message
                lbl.texture_update()
                lbl.height = max(dp(18), lbl.texture_size[1] + dp(2))
            else:
                lbl.text = ''
                lbl.height = 0

        self.username_box, self.username_input = self.make_rounded_input('Enter username')
        self.password_box, self.password_input = self.make_rounded_input('Enter password', password=True)


        self.err_user = self.make_error_label()
        self.err_pass = self.make_error_label()

        login_btn = self.make_rounded_button("Login", ACCENT_SOFT, self.go_login)

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


        card.add_widget(subtitle)
        card.add_widget(self.center_row(self.err_user,     rel_width=0.85, min_w=dp(260), max_w=dp(520), height=self.err_user.height))
        card.add_widget(self.center_row(self.username_box, rel_width=0.85, min_w=dp(260), max_w=dp(520), height=dp(46)))
        card.add_widget(self.center_row(self.err_pass,     rel_width=0.85, min_w=dp(260), max_w=dp(520), height=self.err_pass.height))
        card.add_widget(self.center_row(self.password_box, rel_width=0.85, min_w=dp(260), max_w=dp(520), height=dp(46)))

        card.add_widget(self.center_row(login_btn, rel_width=0.65, min_w=dp(220), max_w=dp(420), height=dp(46)))
        card.add_widget(Widget(size_hint_y=None, height=dp(25)))
        card.add_widget(info_label)

        outer.add_widget(card)

        def update_layout(*_):
            top_anchor.padding = [0, int(Window.height * 0.08), 0, 0]
            target_w = self._clamp(Window.width * 0.92, dp(320), dp(720))
            card.width = target_w
            outer.padding = [0, 0, 0, int(Window.height * 0.01)]

        update_layout()
        Window.bind(size=lambda *_: update_layout())
        self._set_error = set_error


    def go_next(self, *_):
        if self.manager:
            self.manager.current = 'register'

    def go_login(self, *_):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        # clear previous errors
        self._set_error(self.err_user, '')
        self._set_error(self.err_pass, '')

        if ALLOW_LOGIN_BYPASS and (not username or not password):
            response = self.server.send_login("admin", "admin2025")
            self.manager.current = 'home'
            return

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

        response = self.server.send_login(self.username_input.text, self.password_input.text)
        if response:
            if response['success'] is True:
                self.manager.transition.direction = 'left'
                self.manager.current = 'home'
        else:
            message = "Could not connect to server. Please try again."
            self._set_error(self.err_user, message)
