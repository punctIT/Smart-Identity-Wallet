
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

    def create_news_card(self,title_text, subtitle_text, accent_color):
        card_width = self._clamp(Window.width * 0.9,
                                 self._scaled_dp(280),
                                 self._scaled_dp(700))
        card = self.make_card(card_width, 130, radius=22, bg=CARD_DARKER)
        self._main_card = card # Keep reference for size updates
        
        card_content = BoxLayout(orientation='horizontal',
                                 padding=[self._scaled_dp(16)]*2,
                                 spacing=self._scaled_dp(12))
        
        # Left side (Placeholder for image/icon)
        logo = AnchorLayout(size_hint=(None, 1), width=self._scaled_dp(90))
        with logo.canvas.before:
            Color(1,1,1,1)
            logo._lg_bg = RoundedRectangle(radius=[self._scaled_dp(16)]*4, pos=logo.pos, size=logo.size)
        logo.bind(pos=lambda *_: setattr(logo._lg_bg, 'pos', logo.pos),
                size=lambda *_: setattr(logo._lg_bg, 'size', logo.size))
        card_content.add_widget(logo)

        # Right side (Text content)
        v = BoxLayout(orientation='vertical', spacing=self._scaled_dp(4))
        
        # Set text_size for proper alignment
        subtitle_label = Label(text=subtitle_text, color=TEXT_SECONDARY, font_size=self._scaled_sp(14), 
                            halign='left', valign='bottom')
        subtitle_label.bind(size=lambda *x: setattr(subtitle_label, 'text_size', subtitle_label.size))
        v.add_widget(subtitle_label)
        
        title_label = Label(text=f"[b][color={accent_color}]{title_text}[/color][/b]", markup=True, 
                        color=TEXT_PRIMARY, font_size=self._scaled_sp(18), halign='left', valign='middle')
        title_label.bind(size=lambda *x: setattr(title_label, 'text_size', title_label.size))
        v.add_widget(title_label)
        
        details_label = Label(text="Apăsați pentru detalii", color=TEXT_SECONDARY, font_size=self._scaled_sp(14), 
                            halign='left', valign='top')
        details_label.bind(size=lambda *x: setattr(details_label, 'text_size', details_label.size))
        v.add_widget(details_label)
        
        card_content.add_widget(v)
        card.add_widget(card_content)
        
        # Add card content to a BoxLayout to hold it inside the Carousel
        slide = BoxLayout(orientation='vertical')
        # FIX: Ensure card widget is centered in the slide
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
            w._color_instr = Color(*col) # Store Color instruction for dynamic updates
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






