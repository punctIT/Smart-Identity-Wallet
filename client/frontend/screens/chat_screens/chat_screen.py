from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle

from frontend.screens.widgets.custom_buttons import CustomButton
from frontend.screens.widgets.custom_input import CustomInput
from frontend.screens.widgets.custom_label import CustomLabels


class ChatScreen(
    Screen,
    CustomLabels,
    CustomButton,
    CustomInput,
):
    TITLE_TEXT = "Chat Assistant"
    
    def __init__(self, server=None, **kwargs):
        Screen.__init__(self, name="chat", **kwargs)
        self.server = server
        self.scroll_scheduled = None 
        self.setup_chat_screen()
    def on_enter(self, *args):
        self.chat_layout.clear_widgets()
        self.add_message("Assistant", "Bună! Sunt aici să te ajut. Întreabă-mă orice!", is_user=False)
        return super().on_enter(*args)
    def setup_chat_screen(self):
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title_label = Label(
            text=self.TITLE_TEXT,
            size_hint_y=None,
            height=50,
            font_size='20sp',
            bold=True
        )
        main_layout.add_widget(title_label)
        
        # Chat messages container with scroll
        self.scroll = ScrollView()
        self.chat_layout = BoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            padding=[10, 0]
        )
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.scroll.add_widget(self.chat_layout)
        main_layout.add_widget(self.scroll)
        
        # Input area container cu fundal rotund
        input_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=60,
            spacing=0,
            padding=[5, 5, 5, 5]
        )
        
        # Canvas pentru input container
        with input_container.canvas.before:
            Color(0.2, 0.2, 0.2, 1)  # Gri foarte închis
            input_container.bg_rect = RoundedRectangle(
                pos=input_container.pos,
                size=input_container.size,
                radius=[25]
            )
        
        def update_input_bg(instance, value):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
        
        input_container.bind(pos=update_input_bg, size=update_input_bg)
        
        # Text input cu fundal transparent
        self.message_input = TextInput(
            hint_text="Scrie un mesaj...",
            multiline=False,
            size_hint_x=1,
            background_color=(0, 0, 0, 0),  # Transparent
            foreground_color=(1, 1, 1, 1),  # Text alb
            hint_text_color=(0.7, 0.7, 0.7, 1),  # Hint gri deschis
            cursor_color=(1, 1, 1, 1),  # Cursor alb
            padding=[15, 15, 60, 15]  # Padding extra în dreapta pentru buton
        )
        self.message_input.bind(on_text_validate=self.send_message)
        
        # Send button poziționat peste input
        send_button = Button(
            text="=>",
            size_hint=(None, None),
            size=(50, 50),
            font_size='20sp',
            background_color=(0.2, 0.6, 1, 1),  # Albastru
            color=(1, 1, 1, 1)  # Text alb
        )
        
        # Canvas pentru send button rotund
        with send_button.canvas.before:
            Color(0.2, 0.6, 1, 1)  # Albastru
            send_button.bg_circle = RoundedRectangle(
                pos=send_button.pos,
                size=send_button.size,
                radius=[25]
            )
        
        def update_button_bg(instance, value):
            instance.bg_circle.pos = instance.pos
            instance.bg_circle.size = instance.size
        
        send_button.bind(pos=update_button_bg, size=update_button_bg)
        send_button.bind(on_press=self.send_message)
        send_button.background_color = (0, 0, 0, 0)  # Face fundalul transparent
        
        # Layout pentru a poziționa butonul peste input
        input_layout = BoxLayout(orientation='horizontal')
        input_layout.add_widget(self.message_input)
        
        # Container pentru butonul poziționat absolut
        button_container = BoxLayout(size_hint_x=None, width=55, padding=[5, 5, 5, 5])
        button_container.add_widget(send_button)
        
        input_container.add_widget(input_layout)
        input_container.add_widget(button_container)
        
        main_layout.add_widget(input_container)
        self.add_widget(main_layout)
        
        # Add welcome message
        #self.add_message("Assistant", "Bună! Sunt aici să te ajut. Întreabă-mă orice!", is_user=False)
    
    def add_message(self, sender, message, is_user=True):
        """Add a message to the chat"""
        # Salvează poziția curentă de scroll
        old_height = self.chat_layout.height
        
        # Create message container with proper height
        message_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=60,
            spacing=10
        )
        
        message_label = Label(
            text="",
            text_size=(300, None),
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=60,
            markup=True,
            color=(1, 1, 1, 1)  # Text alb
        )
        
        # Desenează chenarul rotund pe canvas - gri foarte închis
        with message_label.canvas.before:
            Color(0.15, 0.15, 0.15, 1)  # Gri foarte foarte închis
            message_label.rect = RoundedRectangle(
                pos=message_label.pos,
                size=message_label.size,
                radius=[20]  # Colțuri mai rotunde
            )
        
        # Actualizează chenarul când se schimbă poziția sau mărimea
        def update_rect(instance, value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
        
        message_label.bind(pos=update_rect, size=update_rect)
        
        if is_user:
            message_label.text = f"[color=3366ff]{sender}:[/color] {message}"
        else:
            message_label.text = f"[color=33cc33]{sender}:[/color] {message}"
        
        if is_user:
            spacer_left = Label(size_hint_x=0.3)
            message_layout.add_widget(spacer_left)
            message_layout.add_widget(message_label)
        else:
            message_layout.add_widget(message_label)
            spacer_right = Label(size_hint_x=0.3)
            message_layout.add_widget(spacer_right)
        
        # Add to chat layout
        self.chat_layout.add_widget(message_layout)
        
        
    
    def send_message(self, instance=None):
        """Send a message and get response"""
        message_text = self.message_input.text.strip()
        
        if not message_text:
            return

        self.add_message("Tu", message_text, is_user=True)
        
        # Clear input
        self.message_input.text = ""
        response=self.server.sent_chatbot_msg(message_text)
        if response != None:
            if response['success']==True:
                Clock.schedule_once(lambda dt: self.add_response(response['data']), 0.5)
            else:
                Clock.schedule_once(lambda dt: self.add_response("error"), 0.5)
       
    
    def add_response(self,text):
        self.add_message("Assistant",text, is_user=False)


__all__ = ["ChatScreen"]