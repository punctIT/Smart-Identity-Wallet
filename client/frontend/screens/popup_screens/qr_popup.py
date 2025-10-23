from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivymd.uix.dialog import MDDialog
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp


from frontend.screens.widgets.qr_code import QRCodeWidget

def match_name(name)->str:
    if name=='identity_card':
        return "Carte de identitate"
    if name=='driving_license':
        return "Carnet de conducere"
    else :
        return name

class QrPopup:
    def __init__(self, entry_point,server, card_name):
        self.server = server
        self.ep=entry_point
        self.card_name = card_name
        self.dialog = None
        
    def show_popup(self):
        content = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None, height=dp(500))
        
        data = self.server.get_specific_data(self.ep)
        if data != None:
            qr_widget = QRCodeWidget(str(data['data']))
            qr_widget.size_hint = (1, 0.4)
        else :
            qr_widget = QRCodeWidget("Error")
            qr_widget.size_hint = (1, 0.4)
        content.add_widget(qr_widget)
        close_btn = Button(
            text="Închide",
            size_hint_y=None,
            height=dp(40),
            background_color=(0.25, 0.60, 1.00, 1),
            color=(1, 1, 1, 1)
        )
        close_btn.bind(on_press=lambda x: self.close_popup())
        content.add_widget(close_btn)
        
        self.dialog = MDDialog(
            title=f"[color=#2696FF][b]{match_name(self.card_name)}[/b][/color]",
            type="custom",
            content_cls=content,
            size_hint=(0.95, 0.9),
        )
        self.dialog.open()
    
    def close_popup(self, *args):
        if self.dialog:
            self.dialog.dismiss()