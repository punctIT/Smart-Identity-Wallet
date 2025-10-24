from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, Any
import threading

from kivy.logger import Logger
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.widget import Widget

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.card import MDCard

from frontend.screens.widgets.custom_alignment import Alignment


class OCRProcessingScreen(MDScreen, Alignment):
    """Screen that processes OCR and allows editing of extracted data."""

    def __init__(self, server=None, **kwargs):
        super().__init__(name="ocr_processing", **kwargs)
        self.server = server
        self.image_path: Optional[str] = None
        self.ocr_data: Optional[Dict[str, Any]] = None
        self.processing = False
        
        # UI elements
        self.progress_bar: Optional[MDProgressBar] = None
        self.status_label: Optional[MDLabel] = None
        self.fields_container: Optional[MDBoxLayout] = None
        self.save_button: Optional[MDRaisedButton] = None
        self.text_fields: Dict[str, MDTextField] = {}
        
        self._build_ui()

    def set_image_path(self, path: str) -> None:
        """Set the path of the image to process."""
        self.image_path = path
        Logger.info(f"OCRProcessingScreen: Set image path: {path}")

    def _build_ui(self) -> None:
        """Build the UI layout."""
        padding = [
            dp(16),
            self._safe_top_padding(16),
            dp(16),
            self._safe_bottom_padding(16),
        ]

        root = MDBoxLayout(
            orientation="vertical",
            padding=padding,
            spacing=dp(16),
        )
        self.add_widget(root)

        # Header
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            spacing=dp(12),
        )
        
        back_btn = MDIconButton(
            icon="arrow-left",
            theme_icon_color="Primary",
            on_release=self._go_back,
        )
        header.add_widget(back_btn)
        
        title = MDLabel(
            text="Procesare Document OCR",
            theme_text_color="Primary",
            font_style="H6",
            halign="left",
            valign="center",
        )
        header.add_widget(title)
        root.add_widget(header)

        # Processing section
        processing_card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(120),
            elevation=2,
        )
        
        self.status_label = MDLabel(
            text="Pregătire pentru procesare...",
            theme_text_color="Primary",
            halign="center",
            font_style="Body1",
        )
        processing_card.add_widget(self.status_label)
        
        self.progress_bar = MDProgressBar(
            size_hint_y=None,
            height=dp(4),
        )
        processing_card.add_widget(self.progress_bar)
        root.add_widget(processing_card)

        # Fields container (initially hidden)
        self.fields_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
        )
        self.fields_container.bind(minimum_height=self.fields_container.setter('height'))
        root.add_widget(self.fields_container)

        # Save button (initially hidden)
        self.save_button = MDRaisedButton(
            text="Salvează Date",
            size_hint_y=None,
            height=dp(40),
            disabled=True,
            on_release=self._save_data,
        )
        root.add_widget(self.save_button)

    def on_enter(self, *args):
        """Called when screen becomes active - start OCR processing."""
        super().on_enter()
        if self.image_path and not self.processing:
            Logger.info("OCRProcessingScreen: Starting OCR processing")
            self._start_ocr_processing()

    def on_leave(self, *args):
        """Called when leaving the screen - ensure cleanup."""
        super().on_leave()
        # Ensure image is cleaned up when leaving screen
        if not self.processing:  # Don't delete if still processing
            self._delete_image_file()

    def _start_ocr_processing(self) -> None:
        """Start OCR processing in background thread."""
        if self.processing:
            return
            
        self.processing = True
        self.progress_bar.start()
        self.status_label.text = "Procesez documentul..."
        
        # Hide fields and save button during processing
        self.fields_container.clear_widgets()
        self.text_fields.clear()
        self.save_button.disabled = True
        
        # Start processing in background thread
        thread = threading.Thread(target=self._process_ocr)
        thread.daemon = True
        thread.start()

    def _process_ocr(self) -> None:
        """Process OCR in background thread."""
        try:
            if not self.server or not hasattr(self.server, 'sent_OCR_image'):
                raise Exception("Server connection not available")
                
            Logger.info(f"OCRProcessingScreen: Sending image for OCR: {self.image_path}")
            # Don't delete the file automatically - we'll handle it after UI update
            ocr_result = self.server.sent_OCR_image(self.image_path, delete_after=False)
            
            if ocr_result:
                Logger.info("OCRProcessingScreen: OCR processing successful")
                # Schedule UI update on main thread
                Clock.schedule_once(lambda dt: self._on_ocr_success(ocr_result), 0)
            else:
                Logger.error("OCRProcessingScreen: OCR processing failed")
                Clock.schedule_once(lambda dt: self._on_ocr_error("OCR processing failed"), 0)
                
        except Exception as e:
            Logger.error(f"OCRProcessingScreen: OCR error: {e}")
            Clock.schedule_once(lambda dt: self._on_ocr_error(str(e)), 0)

    def _on_ocr_success(self, result: Dict[str, Any]) -> None:
        """Handle successful OCR result on main thread."""
        self.processing = False
        self.progress_bar.stop()
        self.status_label.text = "Procesare completă! Verificați și editați datele:"
        
        self.ocr_data = result
        self._build_editable_fields(result)
        self.save_button.disabled = False
        
        # Delete the original image file after successful processing
        self._delete_image_file()

    def _on_ocr_error(self, error_msg: str) -> None:
        """Handle OCR error on main thread."""
        self.processing = False
        self.progress_bar.stop()
        self.status_label.text = f"Eroare la procesare: {error_msg}"
        
        # Add retry button
        retry_btn = MDRaisedButton(
            text="Încearcă din nou",
            size_hint_y=None,
            height=dp(40),
            on_release=lambda *_: self._start_ocr_processing(),
        )
        self.fields_container.add_widget(retry_btn)
        
        # Delete the image file on error as well to clean up
        self._delete_image_file()

    def _build_editable_fields(self, data: Dict[str, Any]) -> None:
        """Build editable text fields from OCR data."""
        self.fields_container.clear_widgets()
        self.text_fields.clear()
        
        # Extract relevant data from OCR response
        ocr_content = data.get('content', {})
        if isinstance(ocr_content, str):
            # If content is a string, create a simple text area
            field = MDTextField(
                hint_text="Text Extras",
                text=ocr_content,
                multiline=True,
                size_hint_y=None,
                height=dp(120),
            )
            self.text_fields['extracted_text'] = field
            self.fields_container.add_widget(field)
        elif isinstance(ocr_content, dict):
            # If content is structured data, create fields for each key
            for key, value in ocr_content.items():
                if isinstance(value, (str, int, float)):
                    field_name = key.replace('_', ' ').title()
                    field = MDTextField(
                        hint_text=field_name,
                        text=str(value),
                        size_hint_y=None,
                        height=dp(56),
                    )
                    self.text_fields[key] = field
                    self.fields_container.add_widget(field)
        else:
            # Fallback: create a general text field
            field = MDTextField(
                hint_text="Date Extrase",
                text=str(data),
                multiline=True,
                size_hint_y=None,
                height=dp(120),
            )
            self.text_fields['raw_data'] = field
            self.fields_container.add_widget(field)
        
        # Add common document fields if not present
        common_fields = [
            ("nume", "Nume"),
            ("prenume", "Prenume"), 
            ("cnp", "CNP"),
            ("serie_numar", "Serie și Număr"),
            ("data_nasterii", "Data Nașterii"),
            ("data_expirarii", "Data Expirării"),
        ]
        
        for field_key, field_label in common_fields:
            if field_key not in self.text_fields:
                field = MDTextField(
                    hint_text=field_label,
                    text="",
                    size_hint_y=None,
                    height=dp(56),
                )
                self.text_fields[field_key] = field
                self.fields_container.add_widget(field)

    def _save_data(self) -> None:
        """Save the edited data."""
        if not self.text_fields:
            return
            
        # Collect data from all fields
        edited_data = {}
        for key, field in self.text_fields.items():
            edited_data[key] = field.text.strip()
        
        Logger.info(f"OCRProcessingScreen: Saving edited data: {edited_data}")
        print(f"💾 Date salvate: {edited_data}")
        
        # TODO: Here you can add code to save the data to database, 
        # send to server, or store locally as needed
        
        # Show success and go back
        self.status_label.text = "Date salvate cu succes!"
        Clock.schedule_once(lambda dt: self._go_back(), 1.5)

    def _delete_image_file(self) -> None:
        """Delete the original image file."""
        if not self.image_path:
            return
            
        try:
            image_path = Path(self.image_path)
            if image_path.exists():
                image_path.unlink()
                Logger.info(f"OCRProcessingScreen: Deleted original image: {self.image_path}")
                print(f"🗑️ Imagine ștearsă: {image_path.name}")
        except Exception as e:
            Logger.warning(f"OCRProcessingScreen: Failed to delete image: {e}")
            print(f"⚠️ Nu s-a putut șterge imaginea: {e}")

    def _go_back(self, *args) -> None:
        """Navigate back to previous screen."""
        manager = getattr(self, "manager", None)
        if not manager:
            return
            
        if manager.has_screen("home"):
            manager.current = "home"
        else:
            manager.current = manager.previous()


__all__ = ["OCRProcessingScreen"]