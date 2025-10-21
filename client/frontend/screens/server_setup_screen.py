from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from frontend.screens.widgets.custom_alignment import Alignment
from frontend.screens.widgets.custom_background import GradientBackground
from frontend.screens.widgets.custom_buttons import CustomButton
from frontend.screens.widgets.custom_input import CustomInput
from frontend.screens.widgets.custom_label import CustomLabels

BG_BOTTOM = (0.03, 0.05, 0.09, 1)
CARD_BG = (0.13, 0.15, 0.20, 1)
CARD_STROKE = (1, 1, 1, 0.06)
TEXT_PRIMARY = (0.92, 0.95, 1.00, 1)
TEXT_SECONDARY = (0.70, 0.76, 0.86, 1)
ACCENT_SOFT = (0.12, 0.35, 0.70, 1)

Window.clearcolor = BG_BOTTOM


class ServerSetupScreen(Screen, CustomButton, CustomInput, CustomLabels, Alignment):
    def __init__(self, server, **kwargs):
        super().__init__(name="server_setup", **kwargs)
        self.server = server

        self.bg = GradientBackground()
        self.add_widget(self.bg)

        top_anchor = AnchorLayout(anchor_x="center", anchor_y="top")
        title = Label(
            text=(
                "[b][color=#BBD3FF]SMART[/color] "
                "[color=#8FB9FF]ID[/color] "
                "[color=#BBD3FF]WALLET[/color][/b]"
            ),
            markup=True,
            font_size=sp(32),
            size_hint=(None, None),
            height=dp(60),
            color=TEXT_PRIMARY,
        )
        top_anchor.add_widget(title)
        self.add_widget(top_anchor)

        outer = AnchorLayout(anchor_x="center", anchor_y="center")
        self.add_widget(outer)

        card = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[dp(22), dp(22), dp(22), dp(22)],
            size_hint=(None, None),
        )
        card.bind(minimum_height=card.setter("height"))

        with card.canvas.before:
            Color(*CARD_BG)
            self.card_bg = RoundedRectangle(radius=[dp(20)] * 4)
        with card.canvas.after:
            Color(*CARD_STROKE)
            self.card_border = RoundedRectangle(radius=[dp(20)] * 4)

        def _sync_bg(*_):
            self.card_bg.pos = card.pos
            self.card_bg.size = card.size
            self.card_border.pos = (card.x - 0.5, card.y - 0.5)
            self.card_border.size = (card.width + 1, card.height + 1)

        card.bind(pos=_sync_bg, size=_sync_bg)

        subtitle = Label(
            text="[b][color=#BBD3FF]Connect to server[/color][/b]",
            markup=True,
            font_size=sp(28),
            size_hint=(1, None),
            height=dp(34),
            color=TEXT_PRIMARY,
        )

        helper = Label(
            text=(
                "[color=#9FB4D9]Enter an IP or URL.[/color]\n"
                "[color=#5F7BA6]Defaults to https and port 8443 "
                "if not provided.[/color]"
            ),
            markup=True,
            font_size=sp(15),
            size_hint=(1, None),
            halign="center",
            valign="middle",
            color=TEXT_SECONDARY,
        )
        helper.bind(
            size=lambda lbl, size: setattr(lbl, "text_size", (size[0], None)),
            texture_size=lambda lbl, size: setattr(lbl, "height", size[1]),
        )

        self.address_box, self.address_input = self.make_rounded_input(
            "e.g. 192.168.0.10"
        )
        self.err_address = self.make_error_label()
        self.err_address_row = self.center_row(
            self.err_address,
            rel_width=0.85,
            min_w=dp(260),
            max_w=dp(520),
            height=self.err_address.height,
        )

        connect_btn = self.make_rounded_button("Continue", ACCENT_SOFT, self.on_submit)

        card.add_widget(subtitle)
        card.add_widget(helper)
        card.add_widget(self.err_address_row)
        card.add_widget(
            self.center_row(
                self.address_box, rel_width=0.85, min_w=dp(260), max_w=dp(520), height=dp(46)
            )
        )
        card.add_widget(
            self.center_row(
                connect_btn, rel_width=0.65, min_w=dp(200), max_w=dp(420), height=dp(46)
            )
        )
        card.add_widget(Widget(size_hint_y=None, height=dp(18)))

        outer.add_widget(card)

        def update_layout(*_):
            top_anchor.padding = [0, int(Window.height * 0.08), 0, 0]
            target_w = self._clamp(Window.width * 0.92, dp(320), dp(720))
            card.width = target_w
            outer.padding = [0, 0, 0, int(Window.height * 0.01)]

        update_layout()
        Window.bind(size=lambda *_: update_layout())

        self._set_error = self._bind_error_label(self.err_address, self.err_address_row)

    def _bind_error_label(self, lbl, row):
        def _setter(message: str):
            if message:
                lbl.text = message
                lbl.texture_update()
                lbl.height = max(dp(18), lbl.texture_size[1] + dp(2))
                row.height = lbl.height
            else:
                lbl.text = ""
                lbl.height = 0
                row.height = 0
        return _setter

    def on_pre_enter(self, *_):
        if self.server and getattr(self.server, "server_url", None):
            self.address_input.text = self.server.server_url
        else:
            self.address_input.text = ""
        self._set_error("")

    def on_submit(self, *_):
        raw_value = self.address_input.text.strip()
        self._set_error("")
        if not raw_value:
            self._set_error("Server address is required.")
            return

        normalized = self._normalize_address(raw_value)
        if not normalized:
            self._set_error("Please provide a valid IP or URL.")
            return

        self.server.set_server_url(normalized)
        if self.manager and self.manager.has_screen("first"):
            splash = self.manager.get_screen("first")
            splash.set_server(self.server)
            self.manager.transition.direction = "left"
            self.manager.current = "first"

    def _normalize_address(self, value: str) -> str:
        addr = value.strip()
        if not addr:
            return ""

        if "://" not in addr:
            addr = f"https://{addr}"

        try:
            scheme, remainder = addr.split("://", 1)
        except ValueError:
            return ""

        if not remainder:
            return ""

        path = ""
        host_port = remainder
        if "/" in remainder:
            host_port, path = remainder.split("/", 1)
            path = "/" + path

        if not host_port:
            return ""

        if host_port.startswith("["):
            closing = host_port.find("]")
            if closing == -1:
                return ""
            has_port = closing + 1 < len(host_port) and host_port[closing + 1] == ":"
        else:
            has_port = ":" in host_port

        if not has_port:
            host_port = f"{host_port}:8443"

        normalized = f"{scheme}://{host_port}{path}"
        return normalized.rstrip("/")
