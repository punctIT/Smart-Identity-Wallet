from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDFloatingActionButton
from kivymd.uix.card import MDCard
from kivymd.uix.carousel import MDCarousel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from kivy.clock import Clock

from frontend.screens.widgets.custom_alignment import Alignment
from frontend.screens.widgets.custom_cards import CategoryCard,NewsCard
# ------------------------ THEME ------------------------
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
    },
    {
        "screen_name": "vehicul_docs",
        "title": "Vehicul",
        "subtitle": "Asigurări, ITP, Talon auto.",
    },
    {
        "screen_name": "transport_docs",
        "title": "Transport",
        "subtitle": "Abonamente și bilete.",
    },
    {
        "screen_name": "diverse_docs",
        "title": "Diverse",
        "subtitle": "Alte documente digitale.",
    },
    {
        "screen_name": "diverse_docs",
        "title": "Programari",
        "subtitle": "Programari la ghiseu.",
    },
    {
        "screen_name": "diverse_docs",
        "title": "Cere documente",
        "subtitle": "Creaza o cerere pentru copie a unui document",
    },
]

CATEGORY_SCREEN_NAMES = [item["screen_name"] for item in CATEGORY_TILE_CONFIG]



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

class NewsCard(MDCard):
    def __init__(self, title: str, body: str, accent_color=None, **kwargs):
        super().__init__(**kwargs)
        
        # Salvează textul complet
        self.full_title = title
        self.full_body = body
        # Accent gri modern în loc de albastru
        self.accent_color = accent_color or (0.9, 0.9, 0.9, 1)  # Gri deschis pentru accent
        
        self.orientation = "vertical"
        self.padding = dp(16)
        self.spacing = dp(8)
        self.size_hint = (None, None)
        self.height = dp(120)
        self.radius = [dp(20)]
        self.ripple_behavior = True
        # Design dark modern
        self.md_bg_color = (0.08, 0.08, 0.08, 1)  # Aproape negru
        self.line_color = (0.2, 0.2, 0.2, 1)     # Gri foarte închis pentru border
        self.shadow_softness = 12
        self.shadow_offset = (0, -2)
        self.elevation = 4
        
        # Bind click event
        self.bind(on_release=self.show_full_content_dialog)
        
        self.build_content()

    def build_content(self):
        """Construiește conținutul card-ului"""
        # Spacer top mic
        self.add_widget(MDLabel(size_hint_y=0.15))

        # Truncate titlul dacă e prea lung
        truncated_title = self._truncate_text(self.full_title, 35)
        self._title = MDLabel(
            text=truncated_title,
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.95, 0.95, 0.95, 1),  # Alb-gri pentru titlu
            halign="left",
            valign="top",
            adaptive_height=True,
            bold=True,
        )
        self._title.bind(width=self._sync_text_width)

        # Truncate body-ul dacă e prea lung
        truncated_body = self._truncate_text(self.full_body, 80)
        self._body = MDLabel(
            text=truncated_body,
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.6, 0.6, 0.6, 1),  # Gri mediu pentru text secundar
            halign="left",
            valign="top",
            adaptive_height=True,
        )
        self._body.bind(width=self._sync_text_width)

        self.add_widget(self._title)
        self.add_widget(self._body)
        
        # Spacer bottom mic
        self.add_widget(MDLabel(size_hint_y=0.15))

    def show_full_content_dialog(self, *args):
        """Afișează dialogul cu conținutul complet"""
        # Creează layout-ul pentru conținutul dialogului
        content_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint_y=None,
            padding=[0, dp(8)]
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Titlu complet
        full_title_label = MDLabel(
            text=self.full_title,
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.95, 0.95, 0.95, 1),  # Alb-gri pentru titlu
            size_hint_y=None,
            markup=True,
            bold=True
        )
        full_title_label.bind(texture_size=full_title_label.setter('size'))
        
        # Body complet în ScrollView pentru texte lungi
        scroll_view = MDScrollView(
            size_hint=(1, None),
            height=dp(200),
            do_scroll_x=False,
            do_scroll_y=True,
            # Scrollbar gri modern
            bar_width=dp(3),
            bar_color=(0.4, 0.4, 0.4, 0.8)
        )
        
        full_body_label = MDLabel(
            text=self.full_body,
            font_style="Body1",
            theme_text_color="Custom",
            text_color=(0.85, 0.85, 0.85, 1),  # Gri deschis pentru textul principal
            size_hint_y=None,
            text_size=(None, None),
            markup=True
        )
        full_body_label.bind(texture_size=full_body_label.setter('size'))
        
        scroll_view.add_widget(full_body_label)
        
        content_layout.add_widget(full_title_label)
        content_layout.add_widget(scroll_view)
        
        # Creează dialogul cu temă dark
        self.dialog = MDDialog(
            title="Detalii Complete",
            type="custom",
            content_cls=content_layout,
            buttons=[
                MDFlatButton(
                    text="ÎNCHIDE",
                    theme_text_color="Custom",
                    text_color=(0.7, 0.7, 0.7, 1),  # Gri pentru buton
                    on_release=self.close_dialog
                ),
            ],
            size_hint=(0.9, None),
            height=dp(400),
            # Dialog dark
            md_bg_color=(0.1, 0.1, 0.1, 1),
            elevation=8
        )
        
        # Ajustează text_size după ce dialogul este creat
        def adjust_text_size(*args):
            available_width = self.dialog.width * 0.85
            full_title_label.text_size = (available_width, None)
            full_body_label.text_size = (available_width, None)
        
        self.dialog.bind(width=adjust_text_size)
        Clock.schedule_once(adjust_text_size, 0.1)
        
        self.dialog.open()

    def close_dialog(self, *args):
        """Închide dialogul"""
        if hasattr(self, 'dialog'):
            self.dialog.dismiss()

    @staticmethod
    def _truncate_text(text: str, max_length: int) -> str:
        """Truncate text și adaugă ... dacă e prea lung"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    @staticmethod
    def _sync_text_width(label, value):
        label.text_size = (value, None)

    def update_width(self, width: float) -> None:
        self.width = width



class HomeScreen(MDScreen, Alignment):
    def __init__(self, sm=None, server=None, **kwargs):
        super().__init__(name="home", **kwargs)
        self.server = server
        self.sm = sm if hasattr(sm, "has_screen") else None
        self._back_binding = False
        self.news_carousel = None
        self.dot_container = None
        self._news_cards = []

        app = App.get_running_app()
        if app and hasattr(app, "theme_cls"):
            app.theme_cls.theme_style = "Dark"
            app.theme_cls.primary_palette = "Blue"

        Window.clearcolor = (0.12, 0.03, 0.03, 1) 

        # Container principal care va conține tot
        main_container = AnchorLayout()
        
        # Layout-ul principal cu conținutul
        root = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            padding=[
                dp(16),
                self._safe_top_padding(16),
                dp(16),
                self._safe_bottom_padding(16),
            ],
        )

        root.add_widget(self._build_header())
        root.add_widget(self._build_news_section())
        root.add_widget(self._build_scroll_area())
        #root.add_widget(self._build_bottom_bar())

        # Adaugă layout-ul principal la container
        main_container.add_widget(root)
        
        # Adaugă butonul floating chat deasupra tuturor
        floating_chat = self._build_floating_chat_button()
        main_container.add_widget(floating_chat)
        
        # Adaugă containerul principal la screen
        self.add_widget(main_container)

        if self.news_carousel:
            self.news_carousel.bind(index=self._refresh_dots)

        Window.bind(size=self._update_news_card_widths)
        self._populate_news([])
        self._update_news_card_widths()
    def _build_floating_chat_button(self):
        """Creează butonul floating pentru chat care plutește deasupra tuturor elementelor"""
        floating_container = AnchorLayout(
            anchor_x="right",
            anchor_y="bottom",
            size_hint=(1, 1),
            padding=(0, 0, dp(24), dp(40))  # right, top, left, bottom
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
    def _build_header(self):
        container = MDBoxLayout(orientation="vertical", spacing=dp(4), adaptive_height=True)

        title = MDLabel(
            text="Smart ID Wallet",
            font_style="H4",
            theme_text_color="Custom",
            text_color=TEXT_PRIMARY,
            halign="left",
            adaptive_height=True,
            bold=True,
        )
        title.bind(width=self._sync_text_width)

        subtitle = MDLabel(
            text="Portofel digital pentru documentele tale esențiale.",
            font_style="Body1",
            theme_text_color="Custom",
            text_color=TEXT_SECONDARY,
            halign="left",
            adaptive_height=True,
        )
        subtitle.bind(width=self._sync_text_width)

        container.add_widget(title)
        container.add_widget(subtitle)
        return container

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
        self.dot_container = MDBoxLayout(orientation="horizontal", spacing=dp(3), padding=(0, 0, 0, 0), adaptive_size=True)
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

    def _build_bottom_bar(self):
        bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(76),
            padding=(dp(12), dp(12)),
            spacing=dp(12),
        )

        fab_column = MDBoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            width=dp(80),
            adaptive_height=True,
            spacing=dp(6),
        )

        fab = MDFloatingActionButton(
            icon="camera",
            md_bg_color=ACCENT_YELLOW,
            text_color=(0, 0, 0, 1),
            elevation=12,
        )
        fab.bind(on_release=lambda *_: self._go_to_screen("camera_scan"))

        fab_label = MDLabel(
            text="Scanează",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=TEXT_SECONDARY,
            halign="center",
            adaptive_height=True,
        )

        fab_column.add_widget(fab)
        fab_column.add_widget(fab_label)
        bar.add_widget(fab_column)

        return bar

    @staticmethod
    def _sync_text_width(label, value):
        label.text_size = (value, None)

    # ------------------------------------------------------------------
    # News feed helpers
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Navigation & lifecycle
    # ------------------------------------------------------------------
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
        if key in (27, 1001):
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
        if not self.sm or not self.sm.has_screen(name):
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
        except Exception as exc:  # noqa: BLE001
            Logger.warning(f"HomeScreen: failed to fetch news ({exc})")
            return

        if not data or not data.get("success"):
            return

        news_items = data.get("data", {}).get("news") or []
        self._populate_news(news_items)

    def set_server(self, server):
        self.server = server


__all__ = ["CATEGORY_TILE_CONFIG", "CATEGORY_SCREEN_NAMES", "HomeScreen"]
