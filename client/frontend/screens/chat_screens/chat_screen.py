from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty


class MessageBubble(MDCard):
    """Custom message bubble widget"""
    message_text = StringProperty("")
    sender_name = StringProperty("")
    is_user = BooleanProperty(True)
    
    def __init__(self, message_text="", sender_name="", is_user=True, **kwargs):
        super().__init__(**kwargs)
        self.message_text = message_text
        self.sender_name = sender_name
        self.is_user = is_user
        
        # Card properties
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.padding = dp(12)
        self.spacing = dp(4)
        self.radius = [dp(20), dp(20), dp(20), dp(20)]
        self.elevation = 2
        
        # Set colors based on sender
        if is_user:
            self.md_bg_color = (0.2, 0.4, 1, 1)  # Blue for user
        else:
            self.md_bg_color = (0.2, 0.2, 0.2, 1)  # Dark gray for assistant
        
        self.build_bubble()
    
    def build_bubble(self):
        """Build the message bubble content"""
        # Sender label
        sender_label = MDLabel(
            text=self.sender_name,
            font_style="Caption",
            size_hint_y=None,
            height=dp(16),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.7) if self.is_user else (0.2, 0.8, 0.2, 1)
        )
        self.add_widget(sender_label)
        
        # Message label
        message_label = MDLabel(
            text=self.message_text,
            size_hint_y=None,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            markup=True
        )
        message_label.bind(texture_size=message_label.setter('size'))
        self.add_widget(message_label)
        
        # Calculate bubble height
        def calculate_height(*args):
            self.height = sender_label.height + message_label.height + self.padding[1] * 2 + self.spacing
        
        message_label.bind(texture_size=calculate_height)
        Clock.schedule_once(calculate_height, 0.1)


class ChatScreen(MDScreen):
    """Chat screen with KivyMD components"""
    TITLE_TEXT = "Chat Assistant"
    
    def __init__(self, server=None, **kwargs):
        super().__init__(name="chat", **kwargs)
        self.server = server
        self.scroll_scheduled = None
        self.setup_chat_screen()
    
    def on_enter(self, *args):
        """Called when entering the screen"""
        self.chat_layout.clear_widgets()
        self.add_message("Assistant", "Bună! Sunt aici să te ajut. Întreabă-mă orice!", is_user=False)
        Clock.schedule_once(self.scroll_to_top_delayed, 0.2)
        return super().on_enter(*args)
    
    def scroll_to_top_delayed(self, dt):
        """Delayed scroll to top"""
        self.scroll.scroll_y = 1
    
    def setup_chat_screen(self):
        """Setup the chat screen layout"""
        # Main layout
        main_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10)
        )
        
        # Title using MDLabel with Material Design styling
        title_label = MDLabel(
            text=self.TITLE_TEXT,
            size_hint_y=None,
            height=dp(56),
            font_style='H5',
            halign='center',
            theme_text_color="Primary"
        )
        main_layout.add_widget(title_label)
        
        # Chat messages container with scroll
        self.scroll = MDScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['content'],
            bar_width=dp(4),
            bar_color=(0.2, 0.6, 1, 0.7)
        )
        
        self.chat_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=[dp(10), 0]
        )
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        
        self.scroll.add_widget(self.chat_layout)
        main_layout.add_widget(self.scroll)
        
        # Input area container
        input_container = MDCard(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            padding=[dp(8), dp(8)],
            spacing=dp(8),
            radius=[dp(30)],
            md_bg_color=(0.15, 0.15, 0.15, 1),
            elevation=4
        )
        
        # Text input using MDTextField with correct parameters
        self.message_input = MDTextField(
            hint_text="Scrie un mesaj...",
            size_hint_x=1,
            multiline=False,
            mode="rectangle",  # or "round" for rounded style
            font_size=dp(16)
        )
        self.message_input.bind(on_text_validate=self.send_message)
        
        # Send button using MDIconButton
        send_button = MDIconButton(
            icon="send",
            md_bg_color=(0.2, 0.6, 1, 1),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            on_release=self.send_message
        )
        
        input_container.add_widget(self.message_input)
        input_container.add_widget(send_button)
        
        main_layout.add_widget(input_container)
        self.add_widget(main_layout)
    
    def add_message(self, sender, message, is_user=True):
        """Add a message to the chat"""
        # Create container for message alignment
        message_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(80),  # Will be adjusted by bubble
            spacing=dp(10),
            padding=[dp(5), dp(5)]
        )
        
        # Create message bubble
        bubble = MessageBubble(
            message_text=message,
            sender_name=sender,
            is_user=is_user,
            size_hint_x=0.7
        )
        
        # Align message based on sender
        if is_user:
            spacer_left = MDLabel(size_hint_x=0.3)
            message_container.add_widget(spacer_left)
            message_container.add_widget(bubble)
        else:
            message_container.add_widget(bubble)
            spacer_right = MDLabel(size_hint_x=0.3)
            message_container.add_widget(spacer_right)
        
        # Adjust container height to match bubble
        def adjust_height(*args):
            message_container.height = bubble.height + dp(10)
        
        bubble.bind(height=adjust_height)
        
        self.chat_layout.add_widget(message_container)
        Clock.schedule_once(self.scroll_to_bottom, 0.1)
    
    def scroll_to_bottom(self, dt=None):
        """Scroll to the last added message"""
        self.scroll.scroll_y = 0
    
    def send_message(self, instance=None):
        """Send a message and get response"""
        message_text = self.message_input.text.strip()
        
        if not message_text:
            return
        
        # Add user message
        self.add_message("Tu", message_text, is_user=True)
        
        # Clear input
        self.message_input.text = ""
        
        # Get response from server
        response = self.server.sent_chatbot_msg(message_text)
        if response is not None:
            if response.get('success', False):
                Clock.schedule_once(
                    lambda dt: self.add_message("Assistant", response['data'], is_user=False),
                    0.5
                )
            else:
                Clock.schedule_once(
                    lambda dt: self.add_message("Assistant", "Error: Nu am putut procesa mesajul.", is_user=False),
                    0.5
                )


__all__ = ["ChatScreen"]