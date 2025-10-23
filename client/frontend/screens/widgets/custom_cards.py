
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse
from kivy.graphics.texture import Texture
from kivy.metrics import dp, sp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.carousel import Carousel
import base64
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from io import BytesIO

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

BG_TOP      = (0.06, 0.07, 0.10, 1)
BG_BOTTOM   = (0.03, 0.05, 0.09, 1)
CARD_BG     = (0.13, 0.15, 0.20, 1)
CARD_STROKE = (1, 1, 1, 0.06)

TEXT_PRIMARY   = (0.92, 0.95, 1.00, 1)
TEXT_SECONDARY = (0.70, 0.76, 0.86, 1)
ACCENT         = (0.25, 0.60, 1.00, 1)   # blue
ACCENT_SOFT    = (0.12, 0.35, 0.70, 1)
ACCENT_YELLOW  = (0.98, 0.90, 0.16, 1)   # scan button

CARD_DARKER    = (0.11, 0.13, 0.18, 1)


class CustomCards(Alignment): 
    def _scaled_dp(self, value):
        if hasattr(self, "_scale_dp"):
            return self._scale_dp(value)
        return dp(value)

    def _scaled_sp(self, value):
        if hasattr(self, "_scale_sp"):
            return self._scale_sp(value)
        return sp(value)

    
    def create_news_card(self, title_text, subtitle_text, accent_color):
        card_width = self._clamp(Window.width * 0.9, self._scaled_dp(280), self._scaled_dp(700))
        card = self.make_card(card_width, 130, radius=22, bg=CARD_DARKER)
        self._main_card = card  # Keep reference for size updates

        card_content = BoxLayout(orientation='horizontal', padding=[self._scaled_dp(16)], spacing=0)

        v = BoxLayout(orientation='vertical', spacing=10)
        title_label = Label(
            text=f"[b][color={accent_color}]{title_text}[/color][/b]",
            markup=True,
            color=TEXT_PRIMARY,
            font_size=self._scaled_sp(18),
            halign='center',
            valign='top',
            size_hint_y=0.3,
            height=self._scaled_dp(20)
        )
        subtitle_label = Label(
            text=subtitle_text,
            color=TEXT_SECONDARY,
            font_size=self._scaled_sp(14),
            halign='left',
            valign='middle',       # <-- vertical centrat
            size_hint_y=0.7,
            height=self._scaled_dp(18)
        )
        subtitle_label.bind(
            size=lambda *x: setattr(subtitle_label, 'text_size', subtitle_label.size)
        )
        title_label.bind(size=lambda *x: setattr(title_label, 'text_size', title_label.size))
        subtitle_label.bind(size=lambda *x: setattr(subtitle_label, 'text_size', subtitle_label.size))
        v.add_widget(title_label)
        v.add_widget(subtitle_label)
        card_content.add_widget(v)
        card.add_widget(card_content)

        slide = BoxLayout(orientation='vertical')
        center_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 1))
        center_anchor.add_widget(card)
        slide.add_widget(center_anchor)
        return slide

    def make_card(self,width, height, radius=20, bg=CARD_BG, stroke=CARD_STROKE):
        radius_value = self._scaled_dp(radius if isinstance(radius, (int, float)) else 20)
        cont = AnchorLayout(size_hint=(None, None), size=(width, self._scaled_dp(height if isinstance(height, (int, float)) else 20)))
        with cont.canvas.before:
            Color(*bg); cont._bg = RoundedRectangle(radius=[radius_value]*4, pos=cont.pos, size=cont.size)
        with cont.canvas.after:
            Color(*stroke); cont._stroke = RoundedRectangle(radius=[radius_value]*4, pos=cont.pos, size=cont.size)
        def _sync(*_):
            cont._bg.pos = cont.pos; cont._bg.size = cont.size
            cont._stroke.pos = (cont.x - .5, cont.y - .5); cont._stroke.size = (cont.width + 1, cont.height + 1)
        cont.bind(pos=_sync, size=_sync)
        return cont


    def make_dot(self,active=False):
        s = self._scaled_dp(8)
        w = Widget(size_hint=(None, None), size=(s, s))
        col = (1,1,1,0.9) if active else (1,1,1,0.25)
        with w.canvas:
            w._color_instr = Color(*col) 
            w._c = Ellipse(size=w.size, pos=w.pos)
        w.bind(size=lambda *_: setattr(w._c, 'size', w.size),
            pos=lambda *_: setattr(w._c, 'pos',  w.pos))
        return w

    # --- Chip Maker ---
    def make_chip(self,icon_char, text):
        # Chip size is size-to-content. size_hint=(None, None) is crucial here.
        chip = AnchorLayout(size_hint=(None, None), height=self._scaled_dp(34))
        
        lbl = Label(
            text=text, 
            color=TEXT_PRIMARY, font_size=self._scaled_sp(14),
            halign='center', valign='middle',
            padding=(self._scaled_dp(10), 0), size_hint=(None, None) 
        )
        
        def _fit(*_):
            lbl.texture_update()
            # Dynamically set chip size based on text size plus padding
            lbl.size = (lbl.texture_size[0] + self._scaled_dp(20), self._scaled_dp(28))
            chip.size = (lbl.width, self._scaled_dp(34))
        
        # Bind the size update to ensure the chip size follows the text
        lbl.bind(texture_size=_fit)
        _fit() # Initial call
        
        with chip.canvas.before:
            Color(0.22, 0.24, 0.30, 1)
            chip._bg = RoundedRectangle(radius=[self._scaled_dp(14)]*4, pos=chip.pos, size=chip.size)
        chip.bind(pos=lambda *_: setattr(chip._bg, 'pos', chip.pos),
                size=lambda *_: setattr(chip._bg, 'size', chip.size))
        chip.add_widget(lbl)
        
        return chip





class CategoryCard(MDCard):
    def __init__(self, title: str, subtitle: str, screen_name: str, on_navigate, **kwargs):
        super().__init__(**kwargs)
        self.screen_name = screen_name
        self._on_navigate = on_navigate
        self.orientation = "vertical"
        self.padding = dp(18)
        self.spacing = dp(8)
        self.size_hint = (1, None)
        self.height = dp(160)
        self.radius = [dp(20)]
        self.ripple_behavior = True
        
        # Design gri modern dark
        self.md_bg_color = (0.08, 0.08, 0.08, 1)  # Aproape negru
        self.line_color = (0.2, 0.2, 0.2, 1)     # Gri închis pentru border
        self.shadow_softness = 12
        self.shadow_offset = (0, -2)
        self.elevation = 4

        spacer_top = Widget(size_hint_y=1)
        spacer_bottom = Widget(size_hint_y=1)

        title_label = MDLabel(
            text=title,
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.95, 0.95, 0.95, 1),  # Alb-gri pentru titlu
            halign="center",
            adaptive_height=True,
            bold=True,
        )
        title_label.bind(width=self._sync_text_width)

        subtitle_label = MDLabel(
            text=subtitle,
            font_style="Body2",
            theme_text_color="Custom",
            text_color=(0.6, 0.6, 0.6, 1),  # Gri mediu pentru subtitle
            halign="center",
            adaptive_height=True,
        )
        subtitle_label.bind(width=self._sync_text_width)

        self.add_widget(spacer_top)
        self.add_widget(title_label)
        self.add_widget(subtitle_label)
        self.add_widget(spacer_bottom)

    @staticmethod
    def _sync_text_width(label, value):
        label.text_size = (value, None)

    def on_release(self, *args):
        if callable(self._on_navigate):
            self._on_navigate(self.screen_name)


class NewsCard(MDCard):
    def __init__(self, title: str, body: str, accent_color=None, **kwargs):
        super().__init__(**kwargs)
        
        # Salvează textul complet
        self.full_title = title
        self.full_body = body
        self.accent_color = accent_color or (0.2, 0.6, 1, 1)  # Default accent
        
        self.orientation = "vertical"
        self.padding = dp(16)
        self.spacing = dp(8)
        self.size_hint = (None, None)
        self.height = dp(120)
        self.radius = [dp(20)]
        self.ripple_behavior = True  # Activat pentru efect de buton
        self.md_bg_color = (0.1, 0.1, 0.1, 1)  # CARD_BG
        self.line_color = (0.3, 0.3, 0.3, 1)   # CARD_STROKE
        self.shadow_softness = 10
        self.shadow_offset = (0, -4)
        
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
            text_color=self.accent_color,
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
            text_color=(0.7, 0.7, 0.7, 1),  # TEXT_SECONDARY
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
            text_color=self.accent_color,
            size_hint_y=None,
            markup=True,
            bold=True
        )
        full_title_label.bind(texture_size=full_title_label.setter('size'))
        
        # Body complet în ScrollView pentru texte lungi
        scroll_view = MDScrollView(
            size_hint=(1, None),
            height=dp(200),  # Înălțime maximă pentru scroll
            do_scroll_x=False,
            do_scroll_y=True
        )
        
        full_body_label = MDLabel(
            text=self.full_body,
            font_style="Body1",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.87),
            size_hint_y=None,
            text_size=(None, None),
            markup=True
        )
        full_body_label.bind(texture_size=full_body_label.setter('size'))
        
        scroll_view.add_widget(full_body_label)
        
        content_layout.add_widget(full_title_label)
        content_layout.add_widget(scroll_view)
        
        # Creează dialogul
        self.dialog = MDDialog(
            title="Detalii Complete",
            type="custom",
            content_cls=content_layout,
            buttons=[
                MDFlatButton(
                    text="ÎNCHIDE",
                    theme_text_color="Custom",
                    text_color=self.accent_color,
                    on_release=self.close_dialog
                ),
            ],
            size_hint=(0.9, None),
            height=dp(400)
        )
        
        # Ajustează text_size după ce dialogul este creat
        def adjust_text_size(*args):
            # Calculează lățimea disponibilă (90% din lățimea ecranului - padding)
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
