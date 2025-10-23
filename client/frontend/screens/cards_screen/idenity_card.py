from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp


class IDScreen(Screen):
    def __init__(self, server=None, **kwargs):
        super().__init__(name='identity_card', **kwargs)
        self.server = server
        self.dialog = None

        # Create popup content instead of screen content
        self.main_box = MDBoxLayout(
            orientation="vertical", 
            spacing=dp(12), 
            padding=[dp(24), dp(24), dp(24), dp(12)],
            size_hint_y=None,
            height=dp(600)
        )

        title_lbl = Label(
            text="[color=#2696FF][b]Carte de identitiate[/b][/color]",
            markup=True,
            font_size=sp(28),
            color=(0.25, 0.60, 1.00, 1),
            size_hint_y=None,
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
            size_hint_y=None,
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

        # Create the dialog popup
        self.dialog = MDDialog(
            title="",
            type="custom",
            content_cls=self.main_box,
            buttons=[
                Button(
                    text="Închide",
                    size_hint=(None, None),
                    height=dp(40),
                    width=dp(100),
                    on_release=self.close_popup
                )
            ],
            size_hint=(0.9, 0.85),
        )

    def close_popup(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def on_pre_enter(self, *args):
        self.doc_container.clear_widgets()
        data = self.server.get_specific_data("GetIdenityCard")
        for key, value in data['data'].items():
            self.doc_container.add_widget(Label(text=str(key), font_size=sp(18)))
            self.doc_container.add_widget(Label(text=str(value), font_size=sp(10)))
        
        # Open the popup when entering the screen
        self.dialog.open()
        
        return super().on_pre_enter(*args)