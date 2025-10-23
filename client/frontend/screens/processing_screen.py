from __future__ import annotations

from pathlib import Path
from typing import Optional, Any

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.spinner import MDSpinner

from frontend.screens.widgets.custom_alignment import Alignment


class ProcessingScreen(MDScreen, Alignment):
    """Processing screen that displays for 3 seconds after taking a photo and returns to home screen."""
    
    def __init__(self, **kwargs):
        super().__init__(name="processing", **kwargs)
        self.photo_path: Optional[Path] = None
        self._auto_return_event: Optional[Any] = None  # Clock event
        self._build_ui()
    
    def _build_ui(self) -> None:
        """Build the processing screen UI."""
        padding = [
            dp(20),
            self._safe_top_padding(20),
            dp(20),
            self._safe_bottom_padding(20),
        ]
        
        root = MDBoxLayout(
            orientation="vertical",
            padding=padding,
            spacing=dp(30),
            md_bg_color=(0.2, 0.2, 0.3, 1),  # Dark blue background
        )
        self.add_widget(root)
        
        # Add some spacing from top
        root.add_widget(MDBoxLayout(size_hint_y=0.3))
        
        # Processing card
        processing_card = MDCard(
            orientation="vertical",
            size_hint=(0.9, None),
            height=dp(350),
            pos_hint={"center_x": 0.5},
            padding=dp(30),
            spacing=dp(30),
            elevation=10,
            md_bg_color=(1, 1, 1, 0.95),
            radius=[20],
        )
        
        # Processing spinner
        spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            pos_hint={"center_x": 0.5},
            active=True,
            color=(0.2, 0.2, 0.8, 1),
        )
        processing_card.add_widget(spinner)
        
        # Processing message
        self.processing_message = MDLabel(
            text="Se procesează fotografia...",
            font_size=dp(24),
            halign="center",
            valign="center",
            size_hint_y=None,
            height=dp(60),
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1),
            bold=True,
        )
        processing_card.add_widget(self.processing_message)
        
        # File name display
        self.file_label = MDLabel(
            text="",
            font_size=dp(14),
            halign="center",
            valign="center",
            size_hint_y=None,
            height=dp(40),
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.5, 1),
        )
        processing_card.add_widget(self.file_label)
        
        # Auto return info
        auto_return_label = MDLabel(
            text="Vă rugăm să așteptați...",
            font_size=dp(12),
            halign="center",
            valign="center",
            size_hint_y=None,
            height=dp(40),
            theme_text_color="Custom",
            text_color=(0.6, 0.6, 0.6, 1),
            italic=True,
        )
        processing_card.add_widget(auto_return_label)
        
        root.add_widget(processing_card)
        
        # Add spacing at bottom
        root.add_widget(MDBoxLayout(size_hint_y=0.3))
    
    def start_processing(self, photo_path: Path) -> None:
        """
        Start the processing screen with photo info and set up auto return to home.
        
        Args:
            photo_path: Path to the saved photo
        """
        def _update_ui(*args):
            self.photo_path = photo_path
            
            # Update file name display
            if self.file_label:
                self.file_label.text = f"Procesare: {photo_path.name}"
            
            Logger.info(f"ProcessingScreen: Processing {photo_path.name}, returning to home in 3 seconds")
            
            # Schedule auto return after 3 seconds
            if self._auto_return_event:
                self._auto_return_event.cancel()
            self._auto_return_event = Clock.schedule_once(self._auto_return, 3.0)
        
        # Ensure UI updates happen on main thread
        Clock.schedule_once(_update_ui, 0)
    
    def _auto_return(self, *args) -> None:
        """Automatically return to home screen after timeout."""
        self._auto_return_event = None
        # Use Clock.schedule_once to ensure navigation happens on main thread
        Clock.schedule_once(lambda dt: self._go_to_home(), 0)
    
    def _go_to_home(self) -> None:
        """Navigate back to the home screen."""
        manager = getattr(self, "manager", None)
        if not manager:
            Logger.warning("ProcessingScreen: No screen manager available")
            return
        
        if manager.has_screen("home"):
            # Set transition direction
            tr = getattr(manager, "transition", None)
            prev_dir = getattr(tr, "direction", None)
            if tr:
                tr.direction = "down"
            
            Logger.info("ProcessingScreen: Returning to home")
            manager.current = "home"
            
            # Restore previous transition direction
            if tr and prev_dir:
                tr.direction = prev_dir
        else:
            Logger.warning("ProcessingScreen: Home screen not found")
    
    def on_pre_leave(self, *args) -> None:
        """Clean up when leaving the screen."""
        super().on_pre_leave(*args)
        # Cancel auto return if user navigates away manually
        if self._auto_return_event:
            self._auto_return_event.cancel()
            self._auto_return_event = None


__all__ = ["ProcessingScreen"]