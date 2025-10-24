from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.logger import Logger
from kivymd.uix.label import MDLabel

from frontend.screens.widgets.qr_code import QRCodeWidget


class UserInfoField(BoxLayout):
    """Custom widget for user info field with icon, label and beautiful rounded editable input."""
    
    def __init__(self, label_text="", input_text="", **kwargs):
        super().__init__(orientation='vertical', size_hint=(1, None), height=dp(100), spacing=dp(12), **kwargs)
        
        # Parse icon and text from label_text
        parts = label_text.split(" ", 1)
        icon_symbol = parts[0] if len(parts) > 0 else "●"
        text_label = parts[1] if len(parts) > 1 else label_text
        
        # Container for icon and label
        label_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(28), spacing=dp(12))
        
        # Simple icon using regular Label with symbol
        self.icon = Label(
            text=icon_symbol,
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            color=(0.25, 0.60, 1.00, 1),
            font_size=sp(18),
            halign="center",
            valign="middle"
        )
        
        # Field label with better styling
        self.label = Label(
            text=f"[b]{text_label}[/b]",
            markup=True,
            font_size=sp(18),
            color=(0.8, 0.84, 0.92, 1),
            size_hint_x=1,
            halign="left",
            valign="middle"
        )
        self.label.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        
        label_container.add_widget(self.icon)
        label_container.add_widget(self.label)
        
        # Container for rounded input field
        self.input_container = BoxLayout(size_hint=(1, None), height=dp(60))
        
        # Custom rounded background using canvas
        with self.input_container.canvas.before:
            Color(0.15, 0.17, 0.22, 1)  # Darker background
            self.input_bg = RoundedRectangle(
                radius=[dp(16)], 
                pos=self.input_container.pos, 
                size=self.input_container.size
            )
        
        self.input_container.bind(pos=self._update_input_bg, size=self._update_input_bg)
        
        # Input field with transparent background (rounded background is handled by container)
        self.text_input = TextInput(
            text=input_text,
            font_size=sp(20),
            background_color=(0, 0, 0, 0),  # Transparent
            foreground_color=(0.95, 0.97, 1.00, 1),
            cursor_color=(0.25, 0.60, 1.00, 1),
            selection_color=(0.25, 0.60, 1.00, 0.3),
            size_hint=(1, 1),
            padding=[dp(20), dp(18)],
            multiline=False,
            border=(0, 0, 0, 0)  # Remove default border
        )
        
        self.input_container.add_widget(self.text_input)
        
        self.add_widget(label_container)
        self.add_widget(self.input_container)
    
    def _update_input_bg(self, *args):
        """Update the rounded background position and size."""
        self.input_bg.pos = self.input_container.pos
        self.input_bg.size = self.input_container.size
    
    def get_value(self):
        """Get the current value of the input field."""
        return self.text_input.text
    
    def set_value(self, value):
        """Set the value of the input field."""
        self.text_input.text = value


class AccountInfoScreen(Screen):
    def __init__(self, server=None, **kwargs):
        super().__init__(name='account_info', **kwargs)
        self.server = server
        self._touch_in_input = False  # Track if touch is in input field

        # Default user data (will be replaced with server data when available)
        self.user_data = {
            "nume": "",
            "email": "",
            "telefon": ""
        }

        self.main_box = BoxLayout(orientation='vertical', size_hint_y=1, spacing=dp(16), padding=[dp(24), dp(24), dp(24), dp(24)])

        # Back button and swipe indicator at the top
        back_indicator = Button(
            font_size=sp(16),
            color=(0.25, 0.60, 1.00, 1),
            size_hint_y=None,
            height=dp(40),
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
            halign="left"
        )
        back_indicator.bind(on_press=self.go_back_to_settings)
        self.main_box.add_widget(back_indicator)

        # Title
        title_lbl = Label(
            text="[color=#2696FF][b]Informații Cont[/b][/color]",
            markup=True,
            font_size=sp(28),
            color=(0.25, 0.60, 1.00, 1),
            size_hint_y=None,
            height=dp(50),
            halign="left",
            valign="middle"
        )
        title_lbl.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        self.main_box.add_widget(title_lbl)

        # Subtitle
        subtitle_lbl = Label(
            text="Vizualizează și actualizează informațiile tale personale.",
            font_size=sp(16),
            color=(0.7, 0.76, 0.86, 1),
            size_hint_y=None,
            height=dp(28),
            halign="left",
            valign="middle"
        )
        subtitle_lbl.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        self.main_box.add_widget(subtitle_lbl)
        
        # Spacer
        self.main_box.add_widget(Label(size_hint_y=None, height=dp(20)))

        # Scrollable form container
        self.scroll = ScrollView(size_hint=(1, 1))
        self.form_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(16))
        self.form_container.bind(minimum_height=self.form_container.setter('height'))

        # Create input fields for user data (initially empty)
        self.input_fields = {}
        
        # Create only the 3 essential fields with beautiful styling and simple icons
        self.input_fields['nume'] = UserInfoField("* Nume complet", "")
        self.input_fields['email'] = UserInfoField("@ Email", "")
        self.input_fields['telefon'] = UserInfoField("# Telefon", "")

        # Add all fields to form container
        for field in self.input_fields.values():
            self.form_container.add_widget(field)

        # Add some spacing before button
        self.form_container.add_widget(Label(size_hint_y=None, height=dp(40)))

        # Beautiful rounded update button container
        button_container = BoxLayout(size_hint=(1, None), height=dp(64), padding=[dp(20), 0])
        
        # Create rounded button with custom background
        self.update_button = Button(
            text="[b]Salvează Modificările[/b]",
            markup=True,
            font_size=sp(20),
            size_hint=(1, 1),
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),  # Transparent
            color=(1, 1, 1, 1)
        )
        
        # Add rounded background to button
        with self.update_button.canvas.before:
            Color(0.25, 0.60, 1.00, 1)  # Blue background
            self.button_bg = RoundedRectangle(
                radius=[dp(20)], 
                pos=self.update_button.pos, 
                size=self.update_button.size
            )
        
        self.update_button.bind(pos=self._update_button_bg, size=self._update_button_bg)
        self.update_button.bind(on_press=self.update_user_info)
        
        button_container.add_widget(self.update_button)
        self.form_container.add_widget(button_container)

        # Add some bottom spacing
        self.form_container.add_widget(Label(size_hint_y=None, height=dp(20)))

        self.scroll.add_widget(self.form_container)
        self.main_box.add_widget(self.scroll)
        self.add_widget(self.main_box)

    def on_enter(self, *args):
        """Called every time the screen is entered. Load fresh data from server."""
        Logger.info("AccountInfoScreen: Entering screen, loading user data...")
        
        try:
            # Load data from server
            if self.server:
                data = self.server.get_specific_data("UserInfo")
                if data is not None and data.get('success') == True:
                    user_info = data.get('data', {}).get('user', [])
                    
                    # Update user_data with server response
                    # Assuming user_info is [email, nume, telefon] based on your original code
                    if len(user_info) >= 3:
                        self.user_data = {
                            "email": user_info[0] if user_info[0] else "",
                            "nume": user_info[1] if user_info[1] else "",
                            "telefon": user_info[2] if user_info[2] else ""
                        }
                        Logger.info(f"AccountInfoScreen: Loaded user data: {self.user_data}")
                    else:
                        Logger.warning("AccountInfoScreen: Server response format unexpected")
                        self.user_data = {"nume": "", "email": "", "telefon": ""}
                else:
                    Logger.warning("AccountInfoScreen: Failed to load user data from server")
                    self.user_data = {"nume": "", "email": "", "telefon": ""}
            else:
                Logger.warning("AccountInfoScreen: No server connection available")
                self.user_data = {"nume": "", "email": "", "telefon": ""}
                
        except Exception as e:
            Logger.error(f"AccountInfoScreen: Error loading user data: {e}")
            self.user_data = {"nume": "", "email": "", "telefon": ""}
        
        # Update form fields with loaded data
        self.refresh_form_data()
        
        return super().on_enter(*args)
    
    def refresh_form_data(self):
        """Refresh all form fields with current user data."""
        Logger.info("AccountInfoScreen: Refreshing form data...")
        
        for field_name, field_widget in self.input_fields.items():
            if field_name in self.user_data:
                value = self.user_data[field_name]
                field_widget.set_value(value)
                Logger.info(f"AccountInfoScreen: Set {field_name} = '{value}'")
    
    def _update_button_bg(self, *args):
        """Update the rounded button background position and size."""
        self.button_bg.pos = self.update_button.pos
        self.button_bg.size = self.update_button.size

    def go_back_to_settings(self, *args):
        """Navigate back to settings screen."""
        self.manager.transition.direction = 'right'
        self.manager.current = 'settings'

    def update_user_info(self, *args):
        """Handle the update button press - collect data from input fields and send to server."""
        try:
            # Collect updated data from input fields
            updated_data = {}
            for field_name, field_widget in self.input_fields.items():
                updated_data[field_name] = field_widget.get_value()
            
            Logger.info(f"AccountInfoScreen: Updating user data: {updated_data}")
            
            # Update local data
            self.user_data.update(updated_data)
            
            # Send data to server if available
            if self.server:
                try:
                    # Here you would implement the server update call
                    # result = self.server.update_user_info(updated_data)
                    Logger.info("AccountInfoScreen: Data sent to server successfully")
                    self.show_update_feedback("Informațiile au fost actualizate cu succes!")
                except Exception as server_error:
                    Logger.error(f"AccountInfoScreen: Server update failed: {server_error}")
                    self.show_update_feedback("Eroare la salvarea pe server!", is_error=True)
            else:
                Logger.warning("AccountInfoScreen: No server connection, data saved locally")
                self.show_update_feedback("Date salvate local (fără conexiune server)", is_error=False)
            
        except Exception as e:
            Logger.error(f"AccountInfoScreen: Error updating user info: {e}")
            self.show_update_feedback("Eroare la actualizarea informațiilor!", is_error=True)
    
    def show_update_feedback(self, message, is_error=False):
        """Show feedback message after update attempt."""
        # Temporarily change button text and color to show feedback
        original_text = self.update_button.text
        original_font_size = self.update_button.font_size
        original_color = (0.25, 0.60, 1.00, 1)
        feedback_color = (0.8, 0.2, 0.2, 1) if is_error else (0.2, 0.8, 0.2, 1)
        
        # Set text with proper wrapping and smaller font size
        self.update_button.text = f"[b]{message}[/b]"
        self.update_button.font_size = sp(16)  # Smaller font for longer text
        self.update_button.text_size = (self.update_button.width - dp(40), None)  # Enable text wrapping
        self.update_button.halign = "center"
        self.update_button.valign = "middle"
        
        # Update the rounded background color
        self.update_button.canvas.before.clear()
        with self.update_button.canvas.before:
            Color(*feedback_color)
            self.button_bg = RoundedRectangle(
                radius=[dp(20)], 
                pos=self.update_button.pos, 
                size=self.update_button.size
            )
        
        # Reset button after 2 seconds
        from kivy.clock import Clock
        def reset_button(*args):
            self.update_button.text = original_text
            self.update_button.font_size = original_font_size
            self.update_button.text_size = (None, None)  # Disable wrapping
            self.update_button.canvas.before.clear()
            with self.update_button.canvas.before:
                Color(*original_color)
                self.button_bg = RoundedRectangle(
                    radius=[dp(20)], 
                    pos=self.update_button.pos, 
                    size=self.update_button.size
                )
            self.update_button.bind(pos=self._update_button_bg, size=self._update_button_bg)
        
        Clock.schedule_once(reset_button, 2.0)
    
    def on_touch_down(self, touch):
        """Handle touch down events - check if touch is in input field."""
        # Check if touch is in any input field
        self._touch_in_input = False
        for field_widget in self.input_fields.values():
            if field_widget.text_input.collide_point(*touch.pos):
                self._touch_in_input = True
                break
        
        # Also check if touch is in the update button
        if self.update_button.collide_point(*touch.pos):
            self._touch_in_input = True
            
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        """Handle touch up events - allow swipe gestures if not interacting with inputs."""
        # If touch was in input field or button, don't propagate to screen manager
        if self._touch_in_input:
            self._touch_in_input = False
            return super().on_touch_up(touch)
        
        # Otherwise, let the screen manager handle swipe gestures
        return super().on_touch_up(touch)

    def on_pre_enter(self, *args):
        """Called before entering the screen."""
        Logger.info("AccountInfoScreen: Preparing to enter screen...")
        return super().on_pre_enter(*args)