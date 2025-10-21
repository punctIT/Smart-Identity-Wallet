from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock

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
        self.setup_chat_screen()
    def on_enter(self, *args):
        print("aslasd")
        
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
        
        # Input area at bottom
        input_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50,
            spacing=10
        )
        
        # Text input
        self.message_input = TextInput(
            hint_text="Scrie un mesaj...",
            multiline=False,
            size_hint_x=0.8
        )
        self.message_input.bind(on_text_validate=self.send_message)
        input_layout.add_widget(self.message_input)
        
        # Send button
        send_button = Button(
            text="Trimite",
            size_hint_x=0.2
        )
        send_button.bind(on_press=self.send_message)
        input_layout.add_widget(send_button)
        
        main_layout.add_widget(input_layout)
        self.add_widget(main_layout)
        
        # Add welcome message
        self.add_message("Assistant", "Bună! Sunt aici să te ajut. Întreabă-mă orice!", is_user=False)
    
    def add_message(self, sender, message, is_user=True):
        """Add a message to the chat"""
        # Create message container with proper height
        message_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=60,  # Fixed height instead of None
            spacing=10
        )
        
        
        message_label = Label(
            text="",  # We'll set this below
            text_size=(300, None),  # Fixed width for text wrapping
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=60,
            markup=True
        )
        
        # Set different colors and text for user and assistant
        if is_user:
            message_label.text = f"[color=3366ff]{sender}:[/color] {message}"
        else:
            message_label.text = f"[color=33cc33]{sender}:[/color] {message}"
        
        # Add spacing and message based on sender
        if is_user:
            # User messages aligned to the right
            spacer_left = Label(size_hint_x=0.3)
            message_layout.add_widget(spacer_left)
            message_layout.add_widget(message_label)
        else:
            # Assistant messages aligned to the left
            message_layout.add_widget(message_label)
            spacer_right = Label(size_hint_x=0.3)
            message_layout.add_widget(spacer_right)
        
        # Add to chat layout
        self.chat_layout.add_widget(message_layout)
        
        # Scroll to bottom
        Clock.schedule_once(self.scroll_to_bottom, 0.1)
    
    def scroll_to_bottom(self, dt):
        """Scroll to the bottom of the chat"""
        self.scroll.scroll_y = 0
    
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