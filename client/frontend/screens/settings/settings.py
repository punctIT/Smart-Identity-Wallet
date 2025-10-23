from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp, sp
from kivy.logger import Logger
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, IconLeftWidget, IconRightWidget


class SettingsMenuItem(MDCard):
    """Custom menu item widget using KivyMD components."""
    
    def __init__(self, icon_name="", title_text="", on_press_callback=None, **kwargs):
        super().__init__(
            size_hint=(1, None),
            height=dp(64),
            elevation=2,
            radius=[12],
            md_bg_color=(0.15, 0.15, 0.15, 1),  # Dark background
            padding=dp(0),
            **kwargs
        )
        
        # Create the list item
        self.list_item = OneLineAvatarIconListItem(
            text=title_text,
            theme_text_color="Custom",
            text_color=(0.95, 0.95, 0.95, 1),
            size_hint_y=None,
            height=dp(64)
        )
        
        # Left icon
        self.left_icon = IconLeftWidget(
            icon=icon_name,
            theme_icon_color="Custom",
            icon_color=(0.25, 0.60, 1.00, 1)
        )
        self.list_item.add_widget(self.left_icon)
        
        # Right arrow icon
        self.right_icon = IconRightWidget(
            icon="chevron-right",
            theme_icon_color="Custom", 
            icon_color=(0.6, 0.6, 0.6, 1)
        )
        self.list_item.add_widget(self.right_icon)
        
        # Bind press callback
        if on_press_callback:
            self.list_item.bind(on_press=on_press_callback)
        
        self.add_widget(self.list_item)


class SettingsScreen(Screen):
    def __init__(self, server=None, **kwargs):
        super().__init__(name='settings', **kwargs)
        self.server = server

        # Main container using KivyMD
        self.main_box = MDBoxLayout(
            orientation='vertical', 
            size_hint=(1, 1), 
            spacing=dp(0), 
            padding=[dp(0), dp(0), dp(0), dp(0)],
            md_bg_color=(0.05, 0.05, 0.05, 1)  # Dark background
        )

        # Header section - properly sized for regular Labels
        header_box = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(180),  # Adjusted from 250 to fit scaled text
            padding=[dp(24), dp(32), dp(24), dp(24)]
        )

        # Swipe indicator at the top - using regular Kivy Label
        swipe_indicator = Label(
            font_size=sp(20),  # Scaled appropriately with title
            color=(0.7, 0.7, 0.7, 1),  # Direct color instead of theme_text_color
            size_hint=(1, None),
            height=dp(40),  # Scaled height
            halign="left",
            valign="middle"
        )
        swipe_indicator.bind(size=swipe_indicator.setter('text_size'))  # Enable text wrapping
        header_box.add_widget(swipe_indicator)

        # Title - LARGE (using regular Kivy Label)
        title_lbl = Label(
            text="Setări",
            font_size=sp(48),  # Increased from 35 to 48 for better proportion
            color=(0.25, 0.60, 1.00, 1),  # Direct color instead of theme_text_color
            size_hint=(1, None),
            height=dp(80),  # Adjusted height
            halign="left",
            valign="middle"
        )
        title_lbl.bind(size=title_lbl.setter('text_size'))  # Enable text wrapping
        header_box.add_widget(title_lbl)

        # Spacer - using regular Label for consistency
        header_box.add_widget(Label(size_hint=(1, None), height=dp(16)))

        self.main_box.add_widget(header_box)

        # Menu section with proper KivyMD components
        menu_section = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(350),  # Reduced from 400 to accommodate larger header
            spacing=dp(8),
            padding=[dp(16), dp(0), dp(16), dp(0)]
        )

        # Add menu items with Material Design icons
        menu_section.add_widget(SettingsMenuItem(
            icon_name="account-circle", 
            title_text="Informații Cont", 
            on_press_callback=self.open_account_info
        ))
        
        menu_section.add_widget(SettingsMenuItem(
            icon_name="bell", 
            title_text="Notificări", 
            on_press_callback=self.open_notifications
        ))
        
        menu_section.add_widget(SettingsMenuItem(
            icon_name="shield-check", 
            title_text="Securitate", 
            on_press_callback=self.open_security
        ))
        
        menu_section.add_widget(SettingsMenuItem(
            icon_name="translate", 
            title_text="Limba", 
            on_press_callback=self.open_language
        ))
        
        menu_section.add_widget(SettingsMenuItem(
            icon_name="information", 
            title_text="Despre Aplicație", 
            on_press_callback=self.open_about
        ))

        self.main_box.add_widget(menu_section)
        
        # Add flexible bottom spacer
        self.main_box.add_widget(MDLabel(size_hint=(1, 1)))
        self.add_widget(self.main_box)
    
    def open_account_info(self, *args):
        """Navigate to account information screen."""
        Logger.info("SettingsScreen: Opening account information screen")
        self.manager.transition.direction = 'left'
        self.manager.current = 'account_info'
    
    def open_notifications(self, *args):
        """Navigate to notifications settings (placeholder)."""
        Logger.info("SettingsScreen: Notifications settings not implemented yet")
        # TODO: Implement notifications screen
        pass
    
    def open_security(self, *args):
        """Navigate to security settings screen.""" 
        try:
            Logger.info("SettingsScreen: Navigating to security settings")
            self.manager.transition.direction = 'left'
            self.manager.current = 'security'
        except Exception as e:
            Logger.warning(f"SettingsScreen: Error navigating to security: {e}")
            print(f"[Settings] Error: Could not navigate to security screen - {e}")
    
    def open_language(self, *args):
        """Navigate to language settings (placeholder)."""
        Logger.info("SettingsScreen: Language settings not implemented yet")
        # TODO: Implement language screen
        pass
    
    def open_about(self, *args):
        """Navigate to about screen (placeholder)."""
        Logger.info("SettingsScreen: About screen not implemented yet")
        # TODO: Implement about screen
        pass

    def on_pre_enter(self, *args):
        """Called when entering the settings screen."""
        try:
            Logger.info("SettingsScreen: Entered settings menu")
        except Exception as e:
            Logger.warning(f"SettingsScreen: Error on enter: {e}")
        
        return super().on_pre_enter(*args)