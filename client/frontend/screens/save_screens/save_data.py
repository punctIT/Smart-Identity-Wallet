from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, Any
import threading
import ast

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
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.menu import MDDropdownMenu

from frontend.screens.popup_screens.pop_card import CardPopup
import base64
import json

ASSETS_DIR = Path(__file__).parent.parent / "assets"
#LOGO_PATH = ASSETS_DIR / "test.png"
LOGO_PATH = "/storage/emulated/0/Pictures/SmartID/document.jpg"

def image_to_base64(image_path: str) -> str:
    """
    Convert an image file to base64 string.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded string of the image
        
    Raises:
        FileNotFoundError: If image file is not found
    """
    try:
        # ------------------------------------
        # Here is where the image is read
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        
        # Encode to base64
        base64_string = base64.b64encode(image_data).decode('utf-8')
        
        return base64_string
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found: {image_path}")
    except Exception as e:
        raise ValueError(f"Error converting image to base64: {e}")

class SaveScreen(Screen):
  
    def __init__(self, server=None, **kwargs):
        super().__init__(name='save_data', **kwargs)
        self.server = server
        self.input_fields = {}
        self.selected_data_type = "ID Card"
        
        # OCR processing variables
        self.image_path: Optional[str] = None
        self.ocr_data: Optional[Dict[str, Any]] = None
        self.processing = False
        self.mode = "document_list"  # "document_list" or "ocr_processing"
        
        # Main layout
        self.main_layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Title
        title = MDLabel(
            text='Save Data Screen',
            font_style='H4',
            halign='center',
            size_hint_y=None,
            height=dp(60)
        )
        self.main_layout.add_widget(title)
        
        # Dropdown menu for data type selection
        dropdown_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10)
        )
        
        dropdown_label = MDLabel(
            text='Data Type:',
            size_hint_x=0.3,
            font_style='Body1'
        )
        dropdown_layout.add_widget(dropdown_label)
        
        self.dropdown_button = MDRaisedButton(
            text=self.selected_data_type,
            size_hint_x=0.7,
            on_release=self.open_dropdown_menu
        )
        dropdown_layout.add_widget(self.dropdown_button)
        
        self.main_layout.add_widget(dropdown_layout)
        
        # Create dropdown menu items
        menu_items = [
            {
                "text": "ID Card",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="ID Card": self.set_data_type(x),
            },
            {
                "text": "Passport",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Passport": self.set_data_type(x),
            },
            {
                "text": "Driver License",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Driver License": self.set_data_type(x),
            },
            {
                "text": "Other Document",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Other Document": self.set_data_type(x),
            },
        ]
        
        self.dropdown_menu = MDDropdownMenu(
            caller=self.dropdown_button,
            items=menu_items,
            width_mult=4,
        )
        
        # Loading layout (initially hidden)
        self.loading_layout = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            spacing=dp(20)
        )
        
        loading_card = MDCard(
            orientation='vertical',
            size_hint=(None, None),
            size=(dp(300), dp(200)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            padding=dp(30),
            spacing=dp(20),
            elevation=5
        )
        
        loading_label = MDLabel(
            text='Processing OCR...',
            halign='center',
            font_style='H6'
        )
        
        spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(46), dp(46)),
            pos_hint={'center_x': 0.5},
            active=True
        )
        
        loading_card.add_widget(loading_label)
        loading_card.add_widget(spinner)
        self.loading_layout.add_widget(loading_card)
        
        # Content layout
        self.content_layout = MDBoxLayout(orientation='vertical', spacing=dp(15))
        
        # Scroll view with grid layout
        scroll = MDScrollView(size_hint=(1, 1))
        self.grid_layout = MDGridLayout(
            cols=1,
            adaptive_height=True,
            spacing=dp(10),
            padding=dp(10)
        )
        scroll.add_widget(self.grid_layout)
        self.content_layout.add_widget(scroll)
        
        # Save button
        save_btn = MDRaisedButton(
            text='Save Data',
            size_hint=(1, None),
            height=dp(60),
            on_release=self.save_data
        )
        self.content_layout.add_widget(save_btn)
        
        # Start with loading screen
        self.main_layout.add_widget(self.loading_layout)
        self.add_widget(self.main_layout)
        
    def on_enter(self, *args):
        # Show loading screen
        self.show_loading(True)
        
        # Process OCR in background thread
        threading.Thread(target=self.process_ocr, daemon=True).start()
        
        return super().on_enter(*args)

    def set_image_path(self, path: str) -> None:
        """Set the path of the image to process and switch to OCR mode."""
        self.image_path = path
        self.mode = "ocr_processing"
        Logger.info(f"SaveScreen: Set image path and switching to OCR mode: {path}")
        print(f"🔄 [SaveScreen] Image path set to: {path}", flush=True)
    
    def show_loading(self, show: bool):
        """Toggle between loading and content view"""
        if show:
            if self.content_layout in self.main_layout.children:
                self.main_layout.remove_widget(self.content_layout)
            if self.loading_layout not in self.main_layout.children:
                self.main_layout.add_widget(self.loading_layout)
        else:
            if self.loading_layout in self.main_layout.children:
                self.main_layout.remove_widget(self.loading_layout)
            if self.content_layout not in self.main_layout.children:
                self.main_layout.add_widget(self.content_layout)
    
    def process_ocr(self):
        """Process OCR in background thread"""
        try:
            # Use the image path set by camera screen or fallback to LOGO_PATH
            image_path_to_use = LOGO_PATH
            
            # Check if the file exists
            if not Path(image_path_to_use).exists():
                raise FileNotFoundError(f"Image file not found: {image_path_to_use}")
            
            Logger.info(f"SaveScreen: Processing OCR for image: {image_path_to_use}")
            print(f"🔄 [SaveScreen] Processing OCR for: {image_path_to_use}", flush=True)
            
            # Convert image to base64 and send to server
            img = image_to_base64(image_path_to_use)
            data = self.server.sent_OCR_image(img)
            print(data)
            
            # Schedule UI update on main thread
            if data and data.get('success') and 'data' in data:
                result_str = data['data'].get('result', '{}')
                # Parse the string representation of dict
                result_dict = ast.literal_eval(result_str)
                Clock.schedule_once(lambda dt: self.on_ocr_complete(result_dict), 0)
            else:
                Clock.schedule_once(lambda dt: self.on_ocr_error("Invalid response format"), 0)
                
        except Exception as e:
            Logger.error(f"SaveScreen: Error in process_ocr: {e}")
            err_msg = str(e)  # ⚡ Salvează mesajul local
            Clock.schedule_once(lambda dt: self.on_ocr_error(err_msg), 0)
            
    def on_ocr_complete(self, result_dict):
        """Called when OCR processing is complete"""
        self.show_loading(False)
        self.add_elements(result_dict)
    
    def on_ocr_error(self, error_msg):
        """Called when OCR processing fails"""
        self.show_loading(False)
        Logger.error(f"SaveScreen: OCR Error: {error_msg}")
        
        # Show error message
        error_card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),
            padding=dp(15),
            elevation=2
        )
        error_label = MDLabel(
            text=f"Error: {error_msg}\nShowing empty fields...",
            theme_text_color='Error',
            halign='center'
        )
        error_card.add_widget(error_label)
        self.grid_layout.add_widget(error_card)
        
        # Add empty fields based on data type
        empty_fields = self.get_empty_fields_for_type()
        self.add_elements(empty_fields)
    
    def open_dropdown_menu(self, *args):
        """Open the dropdown menu for data type selection"""
        self.dropdown_menu.open()
    
    def set_data_type(self, data_type: str):
        """Set the selected data type"""
        self.selected_data_type = data_type
        self.dropdown_button.text = data_type
        self.dropdown_menu.dismiss()
        Logger.info(f"SaveScreen: Data type set to {data_type}")
    def get_entrypoint(self,text):
        if text=='ID Card':
            return "InsertIdenityCard"
        if text=='Passport':
            return "InsertPassport"
        if text=='Driver License':
            return "InsertDrivingLicense"
            
    def get_empty_fields_for_type(self):
        """Get empty fields template based on selected data type"""
        templates = {
            "ID Card": {
                "first_name": "",
                "last_name": "",
                "serie": "",
                "nr": "",
                "place_of_birth": "",
                "address": "",
                "cnp": "",
                "expiration_date": ""
            },
            "Passport": {
                "first_name": "",
                "last_name": "",
                "passport_number": "",
                "nationality": "",
                "date_of_birth": "",
                "place_of_birth": "",
                "issue_date": "",
                "expiration_date": ""
            },
            "Driver License": {
                "first_name": "",
                "last_name": "",
                "license_number": "",
                "category": "",
                "issue_date": "",
                "expiration_date": "",
                "address": ""
            },
            "Other Document": {
                "field_1": "",
                "field_2": "",
                "field_3": "",
                "field_4": "",
                "field_5": ""
            }
        }
        
        return templates.get(self.selected_data_type, templates["ID Card"])
    
    def clear_elements(self, *args):
        """Clear all elements from the grid layout"""
        self.grid_layout.clear_widgets()
        self.input_fields.clear()
        Logger.info("SaveScreen: Cleared all elements")
    
    def add_elements(self, data: Dict[str, Any]):
        """
        Add elements to the grid based on the provided dictionary.
        
        Args:
            data: Dictionary with key-value pairs to display
        """
        for key, value in data.items():
            # Create a card for each item
            card = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height=dp(100),
                padding=dp(10),
                spacing=dp(5),
                elevation=2
            )
            
            # Create box layout for label and input
            item_layout = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(10)
            )
            
            # Label for the key
            label = MDLabel(
                text=str(key),
                size_hint_x=0.3,
                font_style='Body1'
            )
            item_layout.add_widget(label)
            
            # Text input for the value
            text_input = MDTextField(
                text=str(value),
                hint_text=f'Enter {key}',
                size_hint_x=0.7,
                mode='rectangle'
            )
            self.input_fields[key] = text_input
            item_layout.add_widget(text_input)
            
            card.add_widget(item_layout)
            self.grid_layout.add_widget(card)
        
        Logger.info(f"SaveScreen: Added {len(data)} elements")
    
    def display_data(self, *args):
        """Display all data from input fields"""
        collected_data = {}
        for key, text_field in self.input_fields.items():
            collected_data[key] = text_field.text
        
        print("=" * 50)
        print("Collected Data:")
        for key, value in collected_data.items():
            print(f"  {key}: {value}")
        print("=" * 50)
        
        Logger.info(f"SaveScreen: Displayed data: {collected_data}")
        return collected_data
    
    def clean_data(self,data):
        # Exemplu de curățare pentru fiecare cheie
        cleaned = {}
        for key, value in data.items():
            val = value.strip() if isinstance(value, str) else value
            if key in ("nr",):  # Dacă e număr
                try:
                    val = int(val)
                except Exception:
                    pass
            if key == "expiration_date":
                # Formatare exemplu: din "120522" -> "2022-05-12"
                if len(val) == 6 and val.isdigit():
                    day, month, year = val[:2], val[2:4], "20" + val[4:]
                    val = f"{year}-{month}-{day}"
            cleaned[key] = val
        return cleaned
    def save_data(self, *args):
        """Save all data from input fields as JSON"""
        import json
        collected_data = {}
        for key, text_field in self.input_fields.items():
            collected_data[key] = text_field.text

        # Curățare date
        collected_data = self.clean_data(collected_data)

        # Convert to JSON string
        json_data = json.dumps(collected_data, indent=2, ensure_ascii=False)

        # Trimite la server
        response = self.server.sent_specific_data(self.get_entrypoint(self.selected_data_type), json_data)
        print(response)
        self.manager.current = 'home'
        print(json_data)
        print("=" * 50)
        
        Logger.info(f"SaveScreen: Saved data as JSON")
        return json_data