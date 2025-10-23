from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from frontend.screens.popup_screens.pop_card import CardPopup

class Card(BoxLayout):
    def __init__(self, height=dp(80), radius=dp(22), bg_color=(0.18, 0.20, 0.25, 1), **kwargs):
        super().__init__(orientation='horizontal', size_hint=(1, None), height=height, padding=[dp(24), 0, dp(24), 0], **kwargs)
        with self.canvas.before:
            Color(*bg_color)
            self.bg = RoundedRectangle(radius=[radius], pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


def match_name(name)->str:
    if name=='car_registration':
        return "Certificat înmatriculare"
    if name=='insurance':
        return "Asigurare auto"
    if name=='technical_inspection':
        return "Inspecție tehnică"
    else :
        return name


class VehiculDocsScreen(Screen):
    def __init__(self, server=None, **kwargs):
        super().__init__(name='vehicul_docs', **kwargs)
        self.server = server

        self.main_box = BoxLayout(orientation='vertical', size_hint_y=1,spacing=dp(16), padding=[dp(24), dp(24), dp(24), 0])

        title_lbl = Label(
            text="[color=#2696FF][b]Acte Vehicul[/b][/color]",
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
        self.add_widget(self.main_box)

    def on_pre_enter(self, *args):
        data = self.server.get_specific_data("GetWalletAuto")
        if data is not None:
            self.clear_docs()
            print(data['data']['cards'])
            self.add_docs(data['data']['cards'])
            return super().on_pre_enter(*args)
        else:
            self.add_docs({})

    def clear_docs(self):
        self.doc_container.clear_widgets()

    def add_docs(self, doc_names):
        self.clear_docs()
        for doc_name in doc_names:
            card = Card()
            # Acceptă fie dict cu 'title', fie string
            title = doc_name['title'] if isinstance(doc_name, dict) and 'title' in doc_name else str(doc_name)
            btn = Button(
                text=f"[b]{match_name(title)}[/b]",
                markup=True,
                font_size=sp(22),
                color=(0.92, 0.95, 1.00, 1),
                background_normal='',
                background_color=(0,0,0,0),
                halign="left",
                valign="middle"
            )
            btn.bind(size=lambda instance, value: setattr(instance, "text_size", value))
            # Print the name when button is pressed
            def go_card(name):
                popup = CardPopup(self.server, name, match_name(name))
                popup.show_popup()
            btn.bind(on_press=lambda instance, name=title: go_card(name))
            card.add_widget(btn)
            self.doc_container.add_widget(card)

        # Card pentru "Adaugă document"
        add_card = Card(height=dp(110))
        add_box = BoxLayout(orientation="vertical", size_hint=(1, 1), spacing=dp(4), padding=[0, dp(22), 0, dp(22)])
        plus_btn = Button(
            text="[b]+[/b]",
            markup=True,
            font_size=sp(38),
            color=(0.25, 0.60, 1.00, 1),
            background_normal='',
            background_color=(0,0,0,0),
            size_hint_y=None,
            height=dp(44)
        )
        add_label = Label(
            text="Adaugă document",
            font_size=sp(18),
            color=(0.7, 0.76, 0.86, 1),
            size_hint_y=None,
            height=dp(28),
            halign="center",
            valign="middle"
        )
        add_label.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        def go_cam(*args):
            #print("as")
            self.manager.current = 'camera_scan' 
        plus_btn.bind(on_press= go_cam)
        add_box.add_widget(plus_btn)
        add_box.add_widget(add_label)
        add_card.clear_widgets()
        add_card.add_widget(add_box)
        self.doc_container.add_widget(add_card)