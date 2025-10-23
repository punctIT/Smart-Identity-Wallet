from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.logger import Logger
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.switch import Switch
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget


class SecuritySettingItem(MDCard):
    """Custom security setting item with toggle switch."""
    
    def __init__(self, icon_name="", title_text="", description_text="", switch_active=False, on_switch_callback=None, **kwargs):
        super().__init__(
            size_hint=(1, None),
            height=dp(88),
            elevation=3,
            radius=[16],
            md_bg_color=(0.12, 0.12, 0.12, 1),  # Darker background
            padding=dp(0),
            **kwargs
        )
        
        # Main container
        main_container = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, 1),
            padding=[dp(24), dp(20), dp(24), dp(20)],
            spacing=dp(20)
        )
        
        # Left side - Icon and text
        left_container = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, 1),
            spacing=dp(16)
        )
        
        # Icon
        self.icon = IconLeftWidget(
            icon=icon_name,
            theme_icon_color="Custom",
            icon_color=(0.25, 0.60, 1.00, 1),
            icon_size=dp(28)
        )
        
        # Text container
        text_container = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            spacing=dp(4)
        )
        
        # Title
        self.title = MDLabel(
            text=title_text,
            font_size=sp(19),
            theme_text_color="Custom",
            text_color=(0.98, 0.98, 0.98, 1),
            size_hint_y=None,
            height=dp(26),
            halign="left",
            bold=True
        )
        
        # Description
        self.description = MDLabel(
            text=description_text,
            font_size=sp(15),
            theme_text_color="Custom",
            text_color=(0.75, 0.75, 0.75, 1),
            size_hint_y=None,
            height=dp(22),
            halign="left"
        )
        
        text_container.add_widget(self.title)
        text_container.add_widget(self.description)
        
        left_container.add_widget(self.icon)
        left_container.add_widget(text_container)
        
        # Right side - Simple Kivy Switch
        self.switch = Switch(
            active=switch_active,
            size_hint=(None, None),
            size=(dp(48), dp(32)),
            pos_hint={'center_y': 0.5}
        )
        
        if on_switch_callback:
            self.switch.bind(active=on_switch_callback)
        
        main_container.add_widget(left_container)
        main_container.add_widget(self.switch)
        
        self.add_widget(main_container)


class SecurityScreen(Screen):
    def __init__(self, server=None, **kwargs):
        super().__init__(name='security', **kwargs)
        self.server = server

        # Main container using KivyMD
        self.main_box = MDBoxLayout(
            orientation='vertical', 
            size_hint=(1, 1), 
            spacing=dp(0), 
            padding=[dp(0), dp(0), dp(0), dp(0)],
            md_bg_color=(0.05, 0.05, 0.05, 1)  # Dark background
        )

        # Header section
        header_box = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(160),
            padding=[dp(24), dp(32), dp(24), dp(24)]
        )

        # Back button
        back_button = Label(
            font_size=sp(18),
            color=(0.25, 0.60, 1.00, 1),
            size_hint=(1, None),
            height=dp(40),
            halign="left"
        )
        header_box.add_widget(back_button)

        # Title
        title_lbl = Label(
            text="Securitate",
            font_size=sp(42),
            color=(0.25, 0.60, 1.00, 1),
            size_hint=(1, None),
            height=dp(60),
            halign="left",
            valign="middle"
        )
        title_lbl.bind(size=title_lbl.setter('text_size'))
        header_box.add_widget(title_lbl)

        # Subtitle
        subtitle_lbl = Label(
            text="Configurează opțiunile de securitate pentru cont.",
            font_size=sp(16),
            color=(0.7, 0.76, 0.86, 1),
            size_hint=(1, None),
            height=dp(24),
            halign="left",
            valign="middle"
        )
        subtitle_lbl.bind(size=subtitle_lbl.setter('text_size'))
        header_box.add_widget(subtitle_lbl)

        self.main_box.add_widget(header_box)

        # Content section
        content_section = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            spacing=dp(20),
            padding=[dp(20), dp(8), dp(20), dp(0)]
        )

        # Security settings
        content_section.add_widget(SecuritySettingItem(
            icon_name="fingerprint",
            title_text="Autentificare cu Amprenta",
            description_text="Folosește amprenta pentru a te autentifica rapid și sigur",
            switch_active=False,
            on_switch_callback=self.on_fingerprint_toggle
        ))

        # Info section
        info_container = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(110),
            padding=[dp(20), dp(32), dp(20), dp(20)]
        )

        info_card = MDCard(
            size_hint=(1, None),
            height=dp(90),
            elevation=2,
            radius=[12],
            md_bg_color=(0.08, 0.12, 0.20, 0.9),
            padding=[dp(20), dp(18), dp(20), dp(18)]
        )

        info_label = MDLabel(
            text="Activarea autentificării cu amprenta va îmbunătăți securitatea contului tău și va face accesul mai rapid.",
            font_size=sp(15),
            theme_text_color="Custom",
            text_color=(0.85, 0.85, 0.95, 1),
            halign="left",
            valign="middle",
            text_size=(None, None)
        )
        info_label.bind(size=info_label.setter('text_size'))
        
        info_card.add_widget(info_label)
        info_container.add_widget(info_card)

        content_section.add_widget(info_container)
        
        # Add flexible spacer
        content_section.add_widget(Label(size_hint=(1, 1)))

        self.main_box.add_widget(content_section)
        self.add_widget(self.main_box)

    def go_back_to_settings(self, *args):
        """Navigate back to settings screen."""
        self.manager.transition.direction = 'right'
        self.manager.current = 'settings'

    def on_fingerprint_toggle(self, switch, active):
        """Handle fingerprint authentication toggle."""
        Logger.info(f"SecurityScreen: Fingerprint authentication {'enabled' if active else 'disabled'}")
        print(f"[Security] Fingerprint login: {'ON' if active else 'OFF'}")
        
        if active:
            # Here you would implement fingerprint setup
            # For now, just show a message
            self.show_fingerprint_setup_info()
        else:
            # Disable fingerprint authentication
            self.disable_fingerprint_auth()

    def on_auto_lock_toggle(self, switch, active):
        """Handle auto-lock toggle."""
        Logger.info(f"SecurityScreen: Auto-lock {'enabled' if active else 'disabled'}")
        print(f"[Security] Auto-lock: {'ON' if active else 'OFF'}")
        # TODO: Implement auto-lock functionality

    def on_two_factor_toggle(self, switch, active):
        """Handle two-factor authentication toggle."""
        Logger.info(f"SecurityScreen: Two-factor authentication {'enabled' if active else 'disabled'}")
        print(f"[Security] Two-factor auth: {'ON' if active else 'OFF'}")
        # TODO: Implement two-factor authentication

    def show_fingerprint_setup_info(self):
        """Show information about fingerprint setup."""
        Logger.info("SecurityScreen: Fingerprint setup initiated")
        print("[Security] Fingerprint setup would be initiated here")
        # TODO: Show fingerprint enrollment dialog

    def disable_fingerprint_auth(self):
        """Disable fingerprint authentication."""
        Logger.info("SecurityScreen: Fingerprint authentication disabled")
        print("[Security] Fingerprint authentication disabled")
        # TODO: Remove stored fingerprint data

    def on_pre_enter(self, *args):
        """Called when entering the security screen."""
        try:
            Logger.info("SecurityScreen: Entered security settings")
        except Exception as e:
            Logger.warning(f"SecurityScreen: Error on enter: {e}")
        
        return super().on_pre_enter(*args)