from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, Any
import threading

from kivy.logger import Logger
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.card import MDCard

from frontend.screens.popup_screens.pop_card import CardPopup

class Card(BoxLayout):
    def __init__(self, height=dp(80), radius=dp(22), bg_color=(0.18, 0.20, 0.25, 1), **kwargs):
        super().__init__(orientation='horizontal', size_hint=(1, None), height=height, padding=[dp(24), 0, dp(24), 0], **kwargs)
        with self.canvas.before:
            Color(*bg_color)
            self.bg = RoundedRectangle(radius=[radius], pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


def match_name(name)->str:
    if name=='bus_pass':
        return "Abonament autobus"
    if name=='train_ticket':
        return "Bilet tren"
    if name=='metro_card':
        return "Card metrou"
    else :
        return name


class SaveScreen(Screen):
    """Screen that processes OCR for scanned documents and allows editing of extracted data."""

    def __init__(self, server=None, **kwargs):
        super().__init__(name='save_data', **kwargs)
        self.server = server
        self.image_path: Optional[str] = None
        self.ocr_data: Optional[Dict[str, Any]] = None
        self.processing = False
        
        # UI elements
        self.progress_bar: Optional[MDProgressBar] = None
        self.status_label: Optional[MDLabel] = None
        self.fields_container: Optional[MDBoxLayout] = None
        self.save_button: Optional[MDRaisedButton] = None
        self.back_button: Optional[MDIconButton] = None
        self.text_fields: Dict[str, MDTextField] = {}
        
        # Container for original document view mode
        self.doc_container: Optional[BoxLayout] = None
        self.scroll: Optional[ScrollView] = None
        
        # Track current mode
        self.mode = "document_list"  # "document_list" or "ocr_processing"
        
        self._build_ui()

    def set_image_path(self, path: str) -> None:
        """Set the path of the image to process and switch to OCR mode."""
        self.image_path = path
        self.mode = "ocr_processing"
        Logger.info(f"SaveScreen: Set image path and switching to OCR mode: {path}")
        self._switch_to_ocr_mode()

    def _build_ui(self) -> None:
        """Build the UI layout."""
        self.main_box = BoxLayout(orientation='vertical', size_hint_y=1, spacing=dp(16), padding=[dp(24), dp(24), dp(24), 0])

        # Header with back button and title
        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            spacing=dp(12),
        )
        
        self.back_button = MDIconButton(
            icon="arrow-left",
            theme_icon_color="Primary",
            on_release=self._go_back,
        )
        header.add_widget(self.back_button)
        
        self.title_lbl = Label(
            text="[color=#2696FF][b]SALVEAZA[/b][/color]",
            markup=True,
            font_size=sp(28),
            color=(0.25, 0.60, 1.00, 1),
            halign="left",
            valign="middle"
        )
        self.title_lbl.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        header.add_widget(self.title_lbl)
        self.main_box.add_widget(header)

        # Subtitle
        self.subtitle_lbl = Label(
            text="Vizualizezi toate actele de transport încărcate în portofel.",
            font_size=sp(16),
            color=(0.7, 0.76, 0.86, 1),
            size_hint_y=None,
            height=dp(28),
            halign="left",
            valign="middle"
        )
        self.subtitle_lbl.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        self.main_box.add_widget(self.subtitle_lbl)
        
        self.main_box.add_widget(Label(size_hint_y=None, height=dp(28)))

        # Processing section (initially hidden)
        self.processing_card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(120),
            elevation=2,
            opacity=0,  # Hidden initially
        )
        
        self.status_label = MDLabel(
            text="Pregătire pentru procesare...",
            theme_text_color="Primary",
            halign="center",
            font_style="Body1",
        )
        self.processing_card.add_widget(self.status_label)
        
        self.progress_bar = MDProgressBar(
            size_hint_y=None,
            height=dp(4),
        )
        self.processing_card.add_widget(self.progress_bar)
        self.main_box.add_widget(self.processing_card)

        # Fields container for OCR results (initially hidden)
        self.fields_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
            opacity=0,  # Hidden initially
        )
        self.fields_container.bind(minimum_height=self.fields_container.setter('height'))
        
        # Wrap fields in scroll view
        fields_scroll = ScrollView()
        fields_scroll.add_widget(self.fields_container)
        self.main_box.add_widget(fields_scroll)

        # Save button (initially hidden)
        self.save_button = MDRaisedButton(
            text="Salvează Date",
            size_hint_y=None,
            height=dp(40),
            disabled=True,
            opacity=0,  # Hidden initially
            on_release=self._save_data,
        )
        self.main_box.add_widget(self.save_button)

        # Original document list container
        self.scroll = ScrollView(size_hint=(1, 0.6))
        self.doc_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(18))
        self.doc_container.bind(minimum_height=self.doc_container.setter('height'))
        self.scroll.add_widget(self.doc_container)
        self.main_box.add_widget(self.scroll)
        
        self.add_widget(self.main_box)

    def _switch_to_ocr_mode(self) -> None:
        """Switch UI to OCR processing mode."""
        # Hide document list
        self.scroll.opacity = 0
        self.scroll.size_hint_y = 0
        
        # Show OCR processing elements
        self.processing_card.opacity = 1
        self.fields_container.opacity = 1
        
        # Update title and subtitle
        self.title_lbl.text = "[color=#2696FF][b]PROCESARE DOCUMENT[/b][/color]"
        self.subtitle_lbl.text = "Verificați și editați datele extrase din document."

    def _switch_to_document_mode(self) -> None:
        """Switch UI back to document list mode."""
        # Show document list
        self.scroll.opacity = 1
        self.scroll.size_hint_y = 0.6
        
        # Hide OCR processing elements
        self.processing_card.opacity = 0
        self.fields_container.opacity = 0
        self.save_button.opacity = 0
        
        # Reset title and subtitle
        self.title_lbl.text = "[color=#2696FF][b]SALVEAZA[/b][/color]"
        self.subtitle_lbl.text = "Vizualizezi toate actele de transport încărcate în portofel."
        
        # Reset mode
        self.mode = "document_list"
        self.image_path = None
        self.processing = False

    def on_pre_enter(self, *args):
        """Called when screen is about to be entered."""
        if self.mode == "ocr_processing" and self.image_path and not self.processing:
            Logger.info("SaveScreen: Starting OCR processing")
            self._start_ocr_processing()
        elif self.mode == "document_list":
            # Load document list as before
            data = self.server.get_specific_data("GetWalletCards") if self.server else None
            if data is not None:
                self.clear_docs()
                print(data['data']['cards'])
                self.add_docs(data['data']['cards'])
            else:
                self.add_docs({})
        return super().on_pre_enter(*args)

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
        self.save_button.opacity = 0
        
        # Start processing in background thread
        thread = threading.Thread(target=self._process_ocr)
        thread.daemon = True
        thread.start()

    def _process_ocr(self) -> None:
        """Process OCR in background thread."""
        try:
            if not self.server or not hasattr(self.server, 'sent_OCR_image'):
                raise Exception("Server connection not available")
                
            Logger.info(f"SaveScreen: Sending image for OCR: {self.image_path}")
            # Don't delete the file automatically - we'll handle it after UI update
            ocr_result = self.server.sent_OCR_image(self.image_path, delete_after=False)
            
            if ocr_result:
                Logger.info("SaveScreen: OCR processing successful")
                # Schedule UI update on main thread
                Clock.schedule_once(lambda dt: self._on_ocr_success(ocr_result), 0)
            else:
                Logger.error("SaveScreen: OCR processing failed")
                Clock.schedule_once(lambda dt: self._on_ocr_error("OCR processing failed"), 0)
                
        except Exception as e:
            Logger.error(f"SaveScreen: OCR error: {e}")
            Clock.schedule_once(lambda dt: self._on_ocr_error(str(e)), 0)

    def _on_ocr_success(self, result: Dict[str, Any]) -> None:
        """Handle successful OCR result on main thread."""
        self.processing = False
        self.progress_bar.stop()
        self.status_label.text = "Procesare completă! Verificați și editați datele:"
        
        self.ocr_data = result
        self._build_editable_fields(result)
        self.save_button.disabled = False
        self.save_button.opacity = 1
        
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
            ("tip_document", "Tip Document"),
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
        
        Logger.info(f"SaveScreen: Saving edited data: {edited_data}")
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
                Logger.info(f"SaveScreen: Deleted original image: {self.image_path}")
                print(f"🗑️ Imagine ștearsă: {image_path.name}")
        except Exception as e:
            Logger.warning(f"SaveScreen: Failed to delete image: {e}")
            print(f"⚠️ Nu s-a putut șterge imaginea: {e}")

    def _go_back(self, *args) -> None:
        """Navigate back to previous screen."""
        if self.mode == "ocr_processing":
            # Switch back to document list mode
            self._switch_to_document_mode()
        else:
            # Navigate to previous screen
            manager = getattr(self, "manager", None)
            if not manager:
                return
                
            if manager.has_screen("home"):
                manager.current = "home"
            else:
                manager.current = manager.previous()

    # Original document list methods (preserved for backward compatibility)
    def clear_docs(self):
        if self.doc_container:
            self.doc_container.clear_widgets()

    def add_docs(self, doc_names):
        self.clear_docs()
        for doc_name in doc_names:
            card = Card()
            # Acceptă fie dict cu 'title', fie string
            title = doc_name['title'] if isinstance(doc_name, dict) and 'title' in doc_name else str(doc_name)
            btn = Button(
                text=f"[b]{match_name(title)}[/b]",
                markup=True,
                font_size=sp(22),
                color=(0.92, 0.95, 1.00, 1),
                background_normal='',
                background_color=(0,0,0,0),
                halign="left",
                valign="middle"
            )
            btn.bind(size=lambda instance, value: setattr(instance, "text_size", value))
            # Print the name when button is pressed
            def go_card(name):
                popup = CardPopup(self.server, name, match_name(name))
                popup.show_popup()
            btn.bind(on_press=lambda instance, name=title: go_card(name))
            card.add_widget(btn)
            self.doc_container.add_widget(card)

        # Card pentru "Adaugă document"
        add_card = Card(height=dp(110))
        add_box = BoxLayout(orientation="vertical", size_hint=(1, 1), spacing=dp(4), padding=[0, dp(22), 0, dp(22)])
        plus_btn = Button(
            text="[b]+[/b]",
            markup=True,
            font_size=sp(38),
            color=(0.25, 0.60, 1.00, 1),
            background_normal='',
            background_color=(0,0,0,0),
            size_hint_y=None,
            height=dp(44)
        )
        add_label = Label(
            text="Adaugă document",
            font_size=sp(18),
            color=(0.7, 0.76, 0.86, 1),
            size_hint_y=None,
            height=dp(28),
            halign="center",
            valign="middle"
        )
        add_label.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        def go_cam(*args):
            self.manager.current = 'camera_scan' 
        plus_btn.bind(on_press= go_cam)
        add_box.add_widget(plus_btn)
        add_box.add_widget(add_label)
        add_card.clear_widgets()
        add_card.add_widget(add_box)
        self.doc_container.add_widget(add_card)