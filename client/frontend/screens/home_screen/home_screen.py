from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.uix.relativelayout import RelativeLayout
from pathlib import Path

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDFloatingActionButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.carousel import MDCarousel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView

try:
    from kivymd.uix.list import MDList, OneLineIconListItem
except ImportError:
    from kivymd.uix.list import MDList, OneLineListItem as OneLineIconListItem

# Your existing imports
from frontend.screens.widgets.custom_alignment import Alignment
from frontend.screens.widgets.custom_cards import CategoryCard, NewsCard

# Keep all your existing constants
ASSETS_DIR = Path(__file__).parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"

BG_BOTTOM = (0.12, 0.03, 0.03, 1) 
TEXT_PRIMARY = (0.92, 0.95, 1.00, 1)
TEXT_SECONDARY = (0.70, 0.76, 0.86, 1)
ACCENT = (0.25, 0.60, 1.00, 1)
ACCENT_YELLOW = get_color_from_hex("FAE629")

DEFAULT_NEWS_ITEMS = [
    {
        "Title": "Nimic nou",
        "Description": "",
        "accent": ACCENT,
    },
]

CATEGORY_TILE_CONFIG = [
    {
        "screen_name": "personal_docs",
        "title": "Personal Docs",
        "subtitle": "Carte de identitate, Permis auto, etc.",
        "icon": "card-account-details-outline"
    },
    {
        "screen_name": "vehicul_docs", 
        "title": "Vehicul",
        "subtitle": "Asigurări, ITP, Talon auto.",
        "icon": "car"
    },
    {
        "screen_name": "transport_docs",
        "title": "Transport", 
        "subtitle": "Abonamente și bilete.",
        "icon": "bus"
    },
    {
        "screen_name": "diverse_docs",
        "title": "Diverse",
        "subtitle": "Alte documente digitale.",
        "icon": "folder-multiple-outline"
    },
    {
        "screen_name": "diverse_docs",
        "title": "Programari",
        "subtitle": "Programari la ghiseu.",
        "icon": "calendar-clock"
    },
    {
        "screen_name": "diverse_docs", 
        "title": "Cere documente",
        "subtitle": "Creaza o cerere pentru copie a unui document",
        "icon": "file-document-plus-outline"
    },
]

CATEGORY_SCREEN_NAMES = [item["screen_name"] for item in CATEGORY_TILE_CONFIG]

# Menu items pentru drawer
DRAWER_MENU_ITEMS = [
    {"text": "Acasă", "icon": "home", "screen": "home"},
    {"divider": True},
    {"text": "Personal Docs", "icon": "card-account-details-outline", "screen": "personal_docs"},
    {"text": "Vehicul", "icon": "car", "screen": "vehicul_docs"},
    {"text": "Transport", "icon": "bus", "screen": "transport_docs"},
    {"text": "Diverse", "icon": "folder-multiple-outline", "screen": "diverse_docs"},
    {"divider": True},
    {"text": "Scanează Document", "icon": "camera-outline", "screen": "camera_scan"},
    {"text": "Chat Asistent", "icon": "chat-outline", "screen": "chat"},
    {"divider": True},
    {"text": "Setări", "icon": "cog-outline", "screen": "settings"},
    {"divider": True},
    {"text": "Deconectare", "icon": "logout", "screen": "login"},
]

# Keep your existing carousel class
class HomeNewsCarousel(MDCarousel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parent_scroll = None
        self._lock_scroll = False
        self.ignore_perpendicular_swipes = True

    def on_touch_down(self, touch):
        inside = self.collide_point(*touch.pos)
        if inside:
            touch.ud["home_carousel_start"] = touch.pos
            self._lock_scroll = True
            if self.parent_scroll:
                self.parent_scroll.do_scroll_y = False
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._lock_scroll and "home_carousel_start" in touch.ud:
            start_x, start_y = touch.ud["home_carousel_start"]
            dx = abs(touch.x - start_x)
            dy = abs(touch.y - start_y)
            if dy > dx and dy > dp(6):
                if self.parent_scroll:
                    self.parent_scroll.do_scroll_y = True
                self._lock_scroll = False
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.parent_scroll:
            self.parent_scroll.do_scroll_y = True
        self._lock_scroll = False
        return super().on_touch_up(touch)

# Custom divider widget since MDDivider doesn't exist in your version
class SimpleDivider(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(1)
        with self.canvas:
            Color(0.3, 0.3, 0.3, 0.5)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
    
    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

class MenuListItem(MDBoxLayout):
    def __init__(self, text, icon, on_release_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(48)
        self.padding = [dp(16), dp(8)]
        self.spacing = dp(16)
        
        # Make it clickable
        self.on_release_callback = on_release_callback
        
        # Add icon
        icon_widget = MDIconButton(
            icon=icon,
            theme_icon_color="Custom",
            icon_color=TEXT_SECONDARY,
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            pos_hint={"center_y": 0.5}
        )
        self.add_widget(icon_widget)
        
        # Add text
        text_widget = MDLabel(
            text=text,
            theme_text_color="Custom",
            text_color=TEXT_PRIMARY,
            pos_hint={"center_y": 0.5}
        )
        text_widget.bind(width=lambda x, y: setattr(x, 'text_size', (y, None)))
        self.add_widget(text_widget)
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.on_release_callback:
                self.on_release_callback()
            return True
        return super().on_touch_down(touch)

class CustomDrawer(MDBoxLayout):
    def __init__(self, home_screen, **kwargs):
        super().__init__(**kwargs)
        self.home_screen = home_screen
        self.orientation = "vertical"
        self.md_bg_color = (0.08, 0.08, 0.10, 1)
        self.size_hint = (None, 1)
        self.width = dp(280)
        self.pos_hint = {"x": -1}  # Hidden initially
        
        # Add drawer content
        self._build_drawer_content()
        
    def _build_drawer_content(self):
        """Build the drawer content"""
        # Header
        header = self._build_header()
        self.add_widget(header)
        
        # Menu list
        scroll = MDScrollView()
        menu_container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            adaptive_height=True,
            spacing=dp(4)
        )
        
        for item in DRAWER_MENU_ITEMS:
            if item.get("divider"):
                menu_container.add_widget(SimpleDivider())
            else:
                list_item = MenuListItem(
                    text=item["text"],
                    icon=item["icon"],
                    on_release_callback=lambda screen=item["screen"]: self._navigate_to(screen)
                )
                menu_container.add_widget(list_item)
        
        scroll.add_widget(menu_container)
        self.add_widget(scroll)
    
    def _build_header(self):
        """Build drawer header"""
        header = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(150),
            padding=dp(16),
            spacing=dp(8)
        )
        
        # Background color for header
        with header.canvas.before:
            Color(0.1, 0.1, 0.12, 1)
            header.bg_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda x, y: setattr(header.bg_rect, 'size', y))
        header.bind(pos=lambda x, y: setattr(header.bg_rect, 'pos', y))
        
        # Logo și titlu
        logo_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(12)
        )
        
        logo = Image(
            source=str(LOGO_PATH),
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            pos_hint={'center_y': 0.5}
        )
        logo_row.add_widget(logo)
        
        title_box = MDBoxLayout(orientation="vertical")
        
        title = MDLabel(
            text="Smart ID Wallet",
            font_style="H6",
            theme_text_color="Custom",
            text_color=TEXT_PRIMARY,
            halign="left",
            adaptive_height=True,
            bold=True
        )
        title.bind(width=lambda x, y: setattr(x, 'text_size', (y, None)))
        
        subtitle = MDLabel(
            text="Portofel digital",
            font_style="Caption",
            theme_text_color="Custom", 
            text_color=TEXT_SECONDARY,
            halign="left",
            adaptive_height=True
        )
        subtitle.bind(width=lambda x, y: setattr(x, 'text_size', (y, None)))
        
        title_box.add_widget(title)
        title_box.add_widget(subtitle)
        logo_row.add_widget(title_box)
        
        header.add_widget(logo_row)
        return header
    
    def _navigate_to(self, screen_name):
        """Navigate to screen and close drawer"""
        self.home_screen._close_drawer()
        Clock.schedule_once(lambda dt: self.home_screen._go_to_screen(screen_name), 0.3)
    
    def open_drawer(self):
        """Animate drawer open"""
        anim = Animation(pos_hint={"x": 0}, duration=0.3, t="out_cubic")
        anim.start(self)
        
    def close_drawer(self):
        """Animate drawer close"""
        anim = Animation(pos_hint={"x": -1}, duration=0.3, t="out_cubic")
        anim.start(self)

class HomeScreen(MDScreen, Alignment):
    def __init__(self, sm=None, server=None, **kwargs):
        super().__init__(name="home", **kwargs)
        
        # Initialize ALL attributes first
        self.server = server
        self.sm = sm if hasattr(sm, "has_screen") else None
        self._back_binding = False
        self.news_carousel = None
        self.dot_container = None
        self._news_cards = []
        self.drawer = None
        self.overlay = None
        self.is_drawer_open = False
        
        # Background setup
        with self.canvas.before:
            Color(0.13, 0.14, 0.16, 1)
            self.bg_rect = Rectangle(size=Window.size, pos=(0, 0))
        self.bind(size=self._update_bg, pos=self._update_bg)
        Window.bind(size=self._update_window_bg)

        # Create main layout with drawer
        self._build_screen_with_drawer()

        # Setup news carousel
        if self.news_carousel:
            self.news_carousel.bind(index=self._refresh_dots)

        Window.bind(size=self._update_news_card_widths)
        self._populate_news([])
        self._update_news_card_widths()

    def _build_screen_with_drawer(self):
        """Build screen with drawer functionality"""
        # Main relative layout
        root = RelativeLayout()
        
        # Main content
        main_content = self._build_main_content()
        root.add_widget(main_content)
        
        # Overlay pentru drawer - FIX: Simplificat complet
        self.overlay = Widget(
            size_hint=(1, 1),
            opacity=0  # Folosim opacity în loc de canvas
        )
        # Culoare de fundal permanentă
        with self.overlay.canvas.before:
            Color(0, 0, 0, 1)
            self.overlay_rect = Rectangle(size=self.overlay.size, pos=self.overlay.pos)
        
        self.overlay.bind(size=self._update_overlay_rect, pos=self._update_overlay_rect)
        self.overlay.bind(on_touch_down=self._on_overlay_touch)
        root.add_widget(self.overlay)
        
        # Custom drawer
        self.drawer = CustomDrawer(self)
        root.add_widget(self.drawer)
        
        # Floating chat button
        floating_chat = self._build_floating_chat_button()
        root.add_widget(floating_chat)
        
        self.add_widget(root)
    def _update_overlay_rect(self, *args):
        """Update overlay rectangle"""
        if hasattr(self, 'overlay_rect'):
            self.overlay_rect.size = self.overlay.size
            self.overlay_rect.pos = self.overlay.pos
            
    def _build_main_content(self):
        """Build main content with header"""
        main_container = MDBoxLayout(orientation="vertical")
        
        # Header with menu button
        header = self._build_header_with_menu()
        main_container.add_widget(header)
        
        # Content
        content = self._build_content()
        main_container.add_widget(content)
        
        return main_container

    def _build_header_with_menu(self):
        """Header with precisely positioned menu button"""
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            padding=[dp(16), dp(4), dp(16), dp(4)],  # Padding mai mic sus/jos
            spacing=dp(16)
        )
        
        # Container pentru butonul de meniu cu poziție custom
        menu_container = MDBoxLayout(
            orientation="vertical",
            size_hint=(None, 1),
            width=dp(40)
        )
        
        # Spațiu de sus (pentru a împinge butonul mai jos)
        top_spacer = Widget(
            size_hint_y=None,
            height=dp(12)  # Ajustează această valoare pentru poziția dorită
        )
        menu_container.add_widget(top_spacer)
        
        # Menu button
        menu_btn = MDIconButton(
            icon="menu",
            theme_icon_color="Custom",
            icon_color=TEXT_PRIMARY,
            on_release=self._toggle_drawer,
            size_hint_y=None,
            height=dp(32)
        )
        menu_container.add_widget(menu_btn)
        
        # Spațiu de jos (pentru a completa înălțimea)
        menu_container.add_widget(Widget())  # Se extinde automat
        
        header.add_widget(menu_container)
        
        # Title section
        title_container = AnchorLayout(
            anchor_y="center"  # Menține titlul centrat vertical
        )
        
        title_box = MDBoxLayout(
            orientation="horizontal", 
            spacing=dp(12),
            adaptive_height=True
        )
        
        # Title text
        title = MDLabel(
            text="Smart ID Wallet",
            font_style="H6",
            theme_text_color="Custom",
            text_color=TEXT_PRIMARY,
            halign="left",
            adaptive_height=True,
            bold=True,
        )
        title.bind(width=self._sync_text_width)
        title_box.add_widget(title)
        
        title_container.add_widget(title_box)
        header.add_widget(title_container)
        
        return header

    def _build_content(self):
        """Build main content"""
        root = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            padding=[
                dp(16),
                dp(8),
                dp(16),
                self._safe_bottom_padding(16),
            ],
        )

        root.add_widget(self._build_news_section())
        root.add_widget(self._build_scroll_area())
        return root

    def _toggle_drawer(self, *args):
        """Toggle drawer open/close"""
        if self.is_drawer_open:
            self._close_drawer()
        else:
            self._open_drawer()

    def _open_drawer(self):
        """Open drawer with animation"""
        if self.drawer and not self.is_drawer_open:
            self.drawer.open_drawer()
            # FIX: Folosește animație pentru opacity
            anim = Animation(opacity=0.5, duration=0.3)
            anim.start(self.overlay)
            self.is_drawer_open = True

    def _close_drawer(self):
        """Close drawer with animation"""
        if self.drawer and self.is_drawer_open:
            self.drawer.close_drawer()
            # FIX: Animație pentru a face overlay-ul transparent
            anim = Animation(opacity=0, duration=0.3)
            anim.start(self.overlay)
            self.is_drawer_open = False

    def _on_overlay_touch(self, instance, touch):
        """Close drawer when touching overlay"""
        if self.is_drawer_open and self.overlay.opacity > 0:
            self._close_drawer()
            return True
        return False

    # Keep ALL your existing methods exactly as they are
    def _build_floating_chat_button(self):
        floating_container = AnchorLayout(
            anchor_x="right",
            anchor_y="bottom",
            size_hint=(1, 1),
            padding=(0, 0, dp(24), dp(40))
        )
        
        chat_fab = MDFloatingActionButton(
            icon="chat",
            md_bg_color=ACCENT,
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            elevation=16,
            on_release=lambda *_: self._go_to_chat()
        )
        
        floating_container.add_widget(chat_fab)
        return floating_container

    def _build_news_section(self):
        section = MDBoxLayout(orientation="vertical", spacing=dp(6), size_hint_y=None, adaptive_height=True)

        carousel_holder = AnchorLayout(size_hint=(1, None), height=dp(180))
        self.news_carousel = HomeNewsCarousel(
            direction="right",
            anim_move_duration=0.12,
            anim_cancel_duration=0.12,
            loop=True,
        )
        self.news_carousel.scroll_distance = dp(40)
        self.news_carousel.scroll_timeout = 180
        carousel_holder.add_widget(self.news_carousel)
        section.add_widget(carousel_holder)

        dots_holder = AnchorLayout(size_hint=(1, None), height=dp(20))
        self.dot_container = MDBoxLayout(orientation="horizontal", spacing=dp(1), padding=(0, 0, 0, 0), adaptive_size=True)
        dots_holder.add_widget(self.dot_container)
        section.add_widget(dots_holder)
        return section

    def _build_scroll_area(self):
        scroll = MDScrollView(size_hint=(1, 1))
        content = MDBoxLayout(orientation="vertical", spacing=dp(16), size_hint_y=None, adaptive_height=True)
        scroll.add_widget(content)

        grid_section = MDBoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None, adaptive_height=True)
        grid = MDGridLayout(cols=2, spacing=dp(12), padding=(0, 0, 0, dp(12)), size_hint_y=None, adaptive_height=True)
        for tile in CATEGORY_TILE_CONFIG:
            grid.add_widget(CategoryCard(
                title=tile["title"],
                subtitle=tile["subtitle"],
                screen_name=tile["screen_name"],
                on_navigate=self._go_to_screen,
            ))
        grid_section.add_widget(grid)

        content.add_widget(grid_section)
        content.add_widget(Widget(size_hint_y=None, height=dp(48)))
        return scroll

    # All your existing methods remain the same
    def _update_bg(self, *args):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.size = self.size
            self.bg_rect.pos = self.pos

    def _update_window_bg(self, instance, size):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.size = size
            self.bg_rect.pos = (0, 0)

    @staticmethod
    def _sync_text_width(label, value):
        label.text_size = (value, None)

    def _populate_news(self, items):
        if not self.news_carousel:
            return

        self.news_carousel.clear_widgets()
        self._news_cards = []

        data_source = items if items else DEFAULT_NEWS_ITEMS

        for entry in data_source:
            title = entry.get("Title") or "Noutate"
            description = entry.get("Description") or ""
            accent = entry.get("accent", ACCENT)
            self.news_carousel.add_widget(self._build_news_slide(title, description, accent))

        self._refresh_dots()

    def _build_news_slide(self, title, description, accent_color):
        slide = AnchorLayout(anchor_x="center", anchor_y="center")
        card = NewsCard(title, description, accent_color=accent_color)
        card.update_width(self._news_card_width())
        self._news_cards.append(card)
        slide.add_widget(card)
        return slide

    def _refresh_dots(self, *_):
        if not self.dot_container or not self.news_carousel:
            return

        self.dot_container.clear_widgets()
        slides = getattr(self.news_carousel, "slides", [])
        if not slides:
            return

        current_index = self.news_carousel.index
        for idx in range(len(slides)):
            active = idx == current_index
            self.dot_container.add_widget(self._build_dot(active))

    def _build_dot(self, active):
        color = ACCENT if active else (1, 1, 1, 0.25)
        dot = MDLabel(
            text="•",
            font_style="H6",
            theme_text_color="Custom",
            text_color=color,
            halign="center",
        )
        dot.size_hint = (None, None)

        def _sync_size(instance, _value):
            instance.size = instance.texture_size

        dot.bind(texture_size=_sync_size)
        return dot

    def _news_card_width(self):
        return self._clamp(Window.width * 0.82, dp(260), dp(420))

    def _update_news_card_widths(self, *_):
        width = self._news_card_width()
        for card in self._news_cards:
            card.update_width(width)

    def on_pre_enter(self, *_):
        if not self._back_binding:
            Window.bind(on_keyboard=self._handle_back_gesture)
            self._back_binding = True
        self._fetch_news()

    def on_leave(self, *_):
        if self._back_binding:
            Window.unbind(on_keyboard=self._handle_back_gesture)
            self._back_binding = False

    def _handle_back_gesture(self, window, key, scancode, codepoint, modifiers):
        # If drawer is open, close it first
        if key in (27, 1001) and self.is_drawer_open:
            self._close_drawer()
            return True
        # Otherwise exit app
        elif key in (27, 1001):
            app = App.get_running_app()
            if app:
                app.stop()
            return True
        return False

    def _go_to_chat(self):
        from kivy.uix.screenmanager import FadeTransition
        old_transition = self.sm.transition
        self.sm.transition = FadeTransition(duration=0.4)
        self.sm.current = 'chat'
        self.sm.transition = old_transition 

    def _go_to_screen(self, name):
        # Close drawer if open
        if self.is_drawer_open:
            self._close_drawer()
            
        if not self.sm or not self.sm.has_screen(name):
            Logger.warning(f"HomeScreen: Screen '{name}' not found")
            return
            
        direction_map = {
            "camera_scan": "up",
            "chat": "left",
        }
        transition = getattr(self.sm, "transition", None)
        previous_direction = getattr(transition, "direction", None)
        if transition:
            transition.direction = direction_map.get(name, "left")
        self.sm.current = name
        if transition and previous_direction:
            transition.direction = previous_direction

    def _fetch_news(self):
        if not self.server:
            return
        try:
            data = self.server.get_specific_data("News")
        except Exception as exc:
            Logger.warning(f"HomeScreen: failed to fetch news ({exc})")
            return

        if not data or not data.get("success"):
            return

        news_items = data.get("data", {}).get("news") or []
        self._populate_news(news_items)

    def set_server(self, server):
        self.server = server

__all__ = ["CATEGORY_TILE_CONFIG", "CATEGORY_SCREEN_NAMES", "HomeScreen"]