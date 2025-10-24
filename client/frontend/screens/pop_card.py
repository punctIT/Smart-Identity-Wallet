from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp, sp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton


class CardPopup:
    def __init__(self, server, card_name, title=None):
        self.server = server
        self.card_name = card_name
        self.title = title or card_name
        self.dialog = None
        
    def show_popup(self):
        content = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None, height=dp(500))
        
        # Create scroll view for the content
        scroll = ScrollView(size_hint=(1, 0.9))
        doc_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        doc_container.bind(minimum_height=doc_container.setter('height'))
        
        # Get data and populate
        data = self.server.get_specific_data("GetIdenityCard")
        print(f"Popup data: {data}")  # Debug print
        if data and 'data' in data:
            for key, value in data['data'].items():
                doc_container.add_widget(Label(
                    text=f"[b]{str(key)}[/b]", 
                    font_size=sp(16), 
                    size_hint_y=None, 
                    height=dp(30),
                    markup=True,
                    text_size=(None, None),
                    halign="left"
                ))
                doc_container.add_widget(Label(
                    text=str(value), 
                    font_size=sp(14), 
                    size_hint_y=None, 
                    height=dp(25),
                    text_size=(None, None),
                    halign="left"
                ))
        else:
            doc_container.add_widget(Label(text="No data available", font_size=sp(16)))
        
        scroll.add_widget(doc_container)
        content.add_widget(scroll)
        
        # Add close button
        close_btn = MDRaisedButton(
            text="Închide",
            size_hint_y=None,
            height=dp(40),
            md_bg_color=(0.25, 0.60, 1.00, 1),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
        close_btn.bind(on_press=lambda x: self.close_popup())
        content.add_widget(close_btn)
        
        self.dialog = MDDialog(
            title=f"[color=#2696FF][b]{self.title}[/b][/color]",
            type="custom",
            content_cls=content,
            size_hint=(0.95, 0.9),
        )
        self.dialog.open()
    
    def close_popup(self, *args):
        if self.dialog:
            self.dialog.dismiss()