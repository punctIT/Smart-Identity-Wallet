from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.spinner import MDSpinner
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty
import threading
import time


class LoadingBubble(MDCard):
    """Loading indicator bubble"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Card properties
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = dp(12)
        self.spacing = dp(8)
        self.radius = [dp(20), dp(20), dp(20), dp(20)]
        self.elevation = 2
        self.md_bg_color = (0.2, 0.2, 0.2, 1)  # Dark gray for assistant
        
        self.build_bubble()
    
    def build_bubble(self):
        """Build the loading bubble content"""
        # Loading spinner
        spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            pos_hint={'center_y': 0.5},
            active=True,
            palette=[(0.2, 0.8, 0.2, 1)]  # Green color
        )
        self.add_widget(spinner)
        
        # "Typing..." label
        typing_label = MDLabel(
            text="Assistant scrie...",
            size_hint_y=None,
            height=dp(20),
            theme_text_color="Custom",
            text_color=(0.2, 0.8, 0.2, 1),
            font_style="Body2",
            pos_hint={'center_y': 0.5}
        )
        self.add_widget(typing_label)


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
        self.loading_container = None  # Reference to loading message
        self.is_loading = False  # Track loading state
        self.setup_chat_screen()
    
    def on_pre_enter(self, *args):
        """Called when entering the screen"""
        data =  {
            "title": "Permis conducere",
            "subtitle": "Categoria B",
            "status": "Reinnoit recent",
            "number": "B1234567",
            "expiry": "21.11.2027",
        }
        self.server.sent_specific_data("InsertDrivingLicense",data)
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
        
        input_container = MDCard(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            padding=[dp(4), dp(4)],
            spacing=dp(8),
            radius=[dp(28)],
            md_bg_color=(0.12, 0.12, 0.12, 1),
            elevation=3
        )
        
        self.message_input = MDTextField(
            hint_text="Scrie un mesaj...",
            size_hint_x=1,
            multiline=False,
            mode="fill",
            fill_color_normal=(0.2, 0.2, 0.2, 1),
            fill_color_focus=(0.25, 0.25, 0.25, 1),
            line_color_normal=(0, 0, 0, 0),
            line_color_focus=(0, 0, 0, 0),
            text_color_normal=(1, 1, 1, 1),
            text_color_focus=(1, 1, 1, 1),
            hint_text_color_normal=(1, 1, 1, 0.5),
            hint_text_color_focus=(1, 1, 1, 0.7),
            font_size=dp(16),
            radius=[dp(24)],
            pos_hint={'center_y': 0.5}
        )
        
        self.message_input.bind(on_text_validate=self.send_message)
        
        # Send button with loading state
        self.send_button = MDIconButton(
            icon="send",
            md_bg_color=(0.2, 0.6, 1, 1),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            pos_hint={'center_y': 0.5},
            on_release=self.send_message
        )
        
        input_container.add_widget(self.message_input)
        input_container.add_widget(self.send_button)
        
        main_layout.add_widget(input_container)
        self.add_widget(main_layout)
    
    def add_message(self, sender, message, is_user=True):
        """Add a message to the chat"""
        # Create container for message alignment
        message_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(80),
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
    
    def add_loading_indicator(self):
        """Add loading indicator to chat"""
        # Create container for loading alignment
        self.loading_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(70),
            spacing=dp(10),
            padding=[dp(5), dp(5)]
        )
        
        # Create loading bubble
        loading_bubble = LoadingBubble(size_hint_x=0.4)
        
        # Align loading bubble to left (assistant side)
        self.loading_container.add_widget(loading_bubble)
        spacer_right = MDLabel(size_hint_x=0.6)
        self.loading_container.add_widget(spacer_right)
        
        self.chat_layout.add_widget(self.loading_container)
        Clock.schedule_once(self.scroll_to_bottom, 0.1)
    
    def remove_loading_indicator(self):
        """Remove loading indicator from chat"""
        if self.loading_container:
            self.chat_layout.remove_widget(self.loading_container)
            self.loading_container = None
    
    def set_loading_state(self, loading):
        """Set the loading state and update UI"""
        self.is_loading = loading
        
        if loading:
            # Disable input and change button
            self.message_input.disabled = True
            self.send_button.disabled = True
            self.send_button.icon = "loading"
            self.send_button.md_bg_color = (0.5, 0.5, 0.5, 1)  # Gray out button
            
            # Add loading indicator
            self.add_loading_indicator()
        else:
            # Enable input and restore button
            self.message_input.disabled = False
            self.send_button.disabled = False
            self.send_button.icon = "send"
            self.send_button.md_bg_color = (0.2, 0.6, 1, 1)  # Restore color
            
            # Remove loading indicator
            self.remove_loading_indicator()
    
    def scroll_to_bottom(self, dt=None):
        """Scroll to the last added message"""
        self.scroll.scroll_y = 0
    
    def send_message_async(self, message_text):
        """Send message in background thread"""
        def background_task():
            try:
                # Simulate some delay to show loading (remove this in production)
                time.sleep(0.5)
                
                # Get response from server
                response = self.server.sent_chatbot_msg(message_text)
                
                # Schedule UI update on main thread
                Clock.schedule_once(
                    lambda dt: self.handle_response(response),
                    0
                )
            except Exception as e:
                # Handle errors
                Clock.schedule_once(
                    lambda dt: self.handle_response(None, str(e)),
                    0
                )
        
        # Start background thread
        thread = threading.Thread(target=background_task)
        thread.daemon = True
        thread.start()
    
    def handle_response(self, response, error=None):
        """Handle the response from server (called on main thread)"""
        # Remove loading state
        self.set_loading_state(False)
        
        if error:
            # Show error message
            self.add_message("Assistant", f"❌ Eroare: {error}", is_user=False)
        elif response is not None:
            if response.get('success', False):
                # Show successful response
                self.add_message("Assistant", response['data'], is_user=False)
            else:
                # Show error from server
                error_msg = response.get('error', 'Nu am putut procesa mesajul.')
                self.add_message("Assistant", f"{error_msg}", is_user=False)
        else:
            # Show generic error
            self.add_message("Assistant", "Nu am putut procesa mesajul. Încearcă din nou.", is_user=False)
    
    def send_message(self, instance=None):
        """Send a message and get response"""
        # Don't send if already loading
        if self.is_loading:
            return
            
        message_text = self.message_input.text.strip()
        
        if not message_text:
            return
        
        # Add user message
        self.add_message("Tu", message_text, is_user=True)
        
        # Clear input
        self.message_input.text = ""
        
        # Set loading state
        self.set_loading_state(True)
        
        # Send message in background
        self.send_message_async(message_text)


__all__ = ["ChatScreen"]