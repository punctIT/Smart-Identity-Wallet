from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from frontend.screens.pop_card import CardPopup

from frontend.screens.widgets.qr_code import QRCodeWidget

class SettingsScreen(Screen):
    def __init__(self, server=None, **kwargs):
        super().__init__(name='settings', **kwargs)
        self.server = server

        self.main_box = BoxLayout(orientation='vertical', size_hint_y=1,spacing=dp(16), padding=[dp(24), dp(24), dp(24), 0])

        title_lbl = Label(
            text="[color=#2696FF][b]Settings[/b][/color]",
            markup=True,
            font_size=sp(28),
            color=(0.25, 0.60, 1.00, 1),
            size_hint_y=0.2,
            height=dp(40),
            halign="left",
            valign="middle"
        )
        title_lbl.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        self.main_box.add_widget(title_lbl)

        subtitle_lbl = Label(
            text="Vizualizezi toate actele vehicului încărcate în portofel.",
            font_size=sp(16),
            color=(0.7, 0.76, 0.86, 1),
            size_hint_y=0.1,
            height=dp(28),
            halign="left",
            valign="middle"
        )
        subtitle_lbl.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        self.main_box.add_widget(subtitle_lbl)
        
        self.main_box.add_widget(Label(size_hint_y=None, height=dp(28)))

        self.scroll = ScrollView(size_hint=(1, 0.6))
        self.doc_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(18))
        self.doc_container.bind(minimum_height=self.doc_container.setter('height'))

        self.scroll.add_widget(self.doc_container)
        self.main_box.add_widget(self.scroll)
        self.qr_widget = QRCodeWidget("Salut din Settings!")
        self.qr_widget.size_hint = (1, 0.4)
        self.main_box.add_widget(self.qr_widget)

        self.add_widget(self.main_box)

    def on_pre_enter(self, *args):
        data = self.server.get_specific_data("GetWalletAuto")
    