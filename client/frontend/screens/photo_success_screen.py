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

from frontend.screens.widgets.custom_alignment import Alignment


class PhotoSuccessScreen(MDScreen, Alignment):
    """Success screen that displays for 3 seconds after taking a photo and returns to previous screen."""
    
    def __init__(self, **kwargs):
        super().__init__(name="photo_success", **kwargs)
        self.previous_screen: Optional[str] = None
        self.photo_path: Optional[Path] = None
        self._auto_return_event: Optional[Any] = None  # Clock event
        self._build_ui()
    
    def _build_ui(self) -> None:
        """Build the success screen UI."""
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
            md_bg_color=(0.1, 0.7, 0.3, 1),  # Green background
        )
        self.add_widget(root)
        
        # Add some spacing from top
        root.add_widget(MDBoxLayout(size_hint_y=0.3))
        
        # Success card
        success_card = MDCard(
            orientation="vertical",
            size_hint=(0.9, None),
            height=dp(300),
            pos_hint={"center_x": 0.5},
            padding=dp(30),
            spacing=dp(20),
            elevation=10,
            md_bg_color=(1, 1, 1, 0.95),
            radius=[20],
        )
        
        # Success icon (using text for now)
        icon_label = MDLabel(
            text="✓",
            font_size=dp(80),
            halign="center",
            valign="center",
            size_hint_y=None,
            height=dp(100),
            theme_text_color="Custom",
            text_color=(0.1, 0.7, 0.3, 1),
            bold=True,
        )
        success_card.add_widget(icon_label)
        
        # Success message
        self.success_message = MDLabel(
            text="Fotografie salvată cu succes!",
            font_size=dp(20),
            halign="center",
            valign="center",
            size_hint_y=None,
            height=dp(60),
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1),
            bold=True,
        )
        success_card.add_widget(self.success_message)
        
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
        success_card.add_widget(self.file_label)
        
        # Auto return info
        auto_return_label = MDLabel(
            text="Se întoarce automat în 3 secunde...",
            font_size=dp(12),
            halign="center",
            valign="center",
            size_hint_y=None,
            height=dp(40),
            theme_text_color="Custom",
            text_color=(0.6, 0.6, 0.6, 1),
            italic=True,
        )
        success_card.add_widget(auto_return_label)
        
        root.add_widget(success_card)
        
        # Add spacing at bottom
        root.add_widget(MDBoxLayout(size_hint_y=0.3))
    
    def show_success(self, photo_path: Path, previous_screen: str = "home") -> None:
        """
        Show the success screen with photo info and set up auto return.
        
        Args:
            photo_path: Path to the saved photo
            previous_screen: Name of screen to return to
        """
        def _update_ui(*args):
            self.photo_path = photo_path
            self.previous_screen = previous_screen
            
            # Update file name display
            if self.file_label:
                self.file_label.text = f"Salvat ca: {photo_path.name}"
            
            Logger.info(f"PhotoSuccessScreen: Showing success for {photo_path.name}, returning to {previous_screen}")
            
            # Schedule auto return after 3 seconds
            if self._auto_return_event:
                self._auto_return_event.cancel()
            self._auto_return_event = Clock.schedule_once(self._auto_return, 3.0)
        
        # Ensure UI updates happen on main thread
        Clock.schedule_once(_update_ui, 0)
    
    def _auto_return(self, *args) -> None:
        """Automatically return to previous screen after timeout."""
        self._auto_return_event = None
        # Use Clock.schedule_once to ensure navigation happens on main thread
        Clock.schedule_once(lambda dt: self._go_back(), 0)
    
    def _go_back(self) -> None:
        """Navigate back to the previous screen."""
        manager = getattr(self, "manager", None)
        if not manager:
            Logger.warning("PhotoSuccessScreen: No screen manager available")
            return
        
        target_screen = self.previous_screen or "home"
        
        if manager.has_screen(target_screen):
            # Set transition direction
            tr = getattr(manager, "transition", None)
            prev_dir = getattr(tr, "direction", None)
            if tr:
                tr.direction = "down"
            
            Logger.info(f"PhotoSuccessScreen: Returning to {target_screen}")
            manager.current = target_screen
            
            # Restore previous transition direction
            if tr and prev_dir:
                tr.direction = prev_dir
        else:
            Logger.warning(f"PhotoSuccessScreen: Target screen '{target_screen}' not found")
            # Fallback to home or previous screen
            if manager.has_screen("home"):
                manager.current = "home"
            else:
                manager.current = manager.previous()
    
    def on_pre_leave(self, *args) -> None:
        """Clean up when leaving the screen."""
        super().on_pre_leave(*args)
        # Cancel auto return if user navigates away manually
        if self._auto_return_event:
            self._auto_return_event.cancel()
            self._auto_return_event = None


__all__ = ["PhotoSuccessScreen"]