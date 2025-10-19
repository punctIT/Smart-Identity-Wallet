from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse
from kivy.graphics.texture import Texture
from kivy.metrics import dp, sp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

# ------------------------ THEME ------------------------
BG_TOP = (0.06, 0.07, 0.10, 1)
BG_BOTTOM = (0.03, 0.05, 0.09, 1)
CARD_BG = (0.13, 0.15, 0.20, 1)
CARD_STROKE = (1, 1, 1, 0.06)

TEXT_PRIMARY = (0.92, 0.95, 1.00, 1)
TEXT_SECONDARY = (0.70, 0.76, 0.86, 1)
ACCENT = (0.25, 0.60, 1.00, 1)
ACCENT_SOFT = (0.12, 0.35, 0.70, 1)
ACCENT_YELLOW = (0.98, 0.90, 0.16, 1)

CARD_DARKER = (0.11, 0.13, 0.18, 1)

Window.clearcolor = BG_BOTTOM


class GradientBackground(BoxLayout):
    def __init__(self, color_top=BG_TOP, color_bottom=BG_BOTTOM, **kwargs):
        super().__init__(**kwargs)
        self.color_top = color_top
        self.color_bottom = color_bottom
        with self.canvas:
            self.rect = Rectangle()
        self._build_texture()
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _build_texture(self):
        height = 128
        texture = Texture.create(size=(1, height), colorfmt="rgba")
        buffer = bytearray()
        r1, g1, b1, a1 = self.color_top
        r2, g2, b2, a2 = self.color_bottom
        for i in range(height):
            t = i / (height - 1)
            r = int((r1 * (1 - t) + r2 * t) * 255)
            g = int((g1 * (1 - t) + g2 * t) * 255)
            b = int((b1 * (1 - t) + b2 * t) * 255)
            a = int((a1 * (1 - t) + a2 * t) * 255)
            buffer += bytes((r, g, b, a))
        texture.blit_buffer(bytes(buffer), colorfmt="rgba", bufferfmt="ubyte")
        texture.wrap = "repeat"
        self.rect.texture = texture
        self.rect.tex_coords = (0, 0, 1, 0, 1, 1, 0, 1)

    def _update_rect(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size


def make_round_icon_button(char="⚙", bg=CARD_BG, size=dp(44), fg=TEXT_PRIMARY):
    root = AnchorLayout(size_hint=(None, None), size=(size, size))
    with root.canvas.before:
        Color(*bg)
        root._circle = Ellipse(size=root.size, pos=root.pos)

    def _sync(*_):
        root._circle.size = root.size
        root._circle.pos = root.pos

    root.bind(size=_sync, pos=_sync)
    label = Label(text=char, color=fg, font_size=sp(20))
    root.add_widget(label)
    return root


def make_card(width, height, radius=dp(20), bg=CARD_BG, stroke=CARD_STROKE):
    container = AnchorLayout(size_hint=(None, None), size=(width, height))
    with container.canvas.before:
        Color(*bg)
        container._bg = RoundedRectangle(radius=[radius] * 4, pos=container.pos, size=container.size)
    with container.canvas.after:
        Color(*stroke)
        container._stroke = RoundedRectangle(radius=[radius] * 4, pos=container.pos, size=container.size)

    def _sync(*_):
        container._bg.pos = container.pos
        container._bg.size = container.size
        container._stroke.pos = (container.x - 0.5, container.y - 0.5)
        container._stroke.size = (container.width + 1, container.height + 1)

    container.bind(pos=_sync, size=_sync)
    return container


def make_dot(active=False):
    size_px = dp(8)
    widget = Widget(size_hint=(None, None), size=(size_px, size_px))
    colour = (1, 1, 1, 0.9) if active else (1, 1, 1, 0.25)
    with widget.canvas:
        Color(*colour)
        widget._circle = Ellipse(size=widget.size, pos=widget.pos)

    widget.bind(size=lambda *_: setattr(widget._circle, "size", widget.size))
    widget.bind(pos=lambda *_: setattr(widget._circle, "pos", widget.pos))
    return widget


__all__ = [
    "ACCENT",
    "ACCENT_SOFT",
    "ACCENT_YELLOW",
    "BG_BOTTOM",
    "BG_TOP",
    "CARD_BG",
    "CARD_DARKER",
    "CARD_STROKE",
    "GradientBackground",
    "make_card",
    "make_dot",
    "make_round_icon_button",
    "TEXT_PRIMARY",
    "TEXT_SECONDARY",
]
