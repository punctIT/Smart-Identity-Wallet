from kivy.core.window import Window
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

# ------------------------ THEME ------------------------
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

Window.clearcolor = BG_BOTTOM

# ------------------------ UTILITIES ------------------------
def _clamp(v, lo, hi): return max(lo, min(hi, v))

class ScalableLabel(Label):
    """A Label that scales its font size based on the widget's current width to prevent text overflow."""
    def __init__(self, max_font_size_sp=sp(30), padding_dp=dp(10), **kwargs):
        super().__init__(**kwargs)
        self.max_font_size = max_font_size_sp
        self.padding_dp = padding_dp
        self.bind(size=self._update_font_size, text=self._update_font_size)
        
    def _update_font_size(self, *args):
        if not self.text or self.width == 0:
            return

        # 1. Use the max font size for initial texture calculation
        self.font_size = self.max_font_size
        self.texture_update()
        
        # 2. Calculate the required width for the text at max size
        text_width_at_max_size = self.texture_size[0]
        
        # 3. Calculate the available width inside the container (Tile width - Inner Padding)
        available_width = self.width - (self.padding_dp * 2) 

        if text_width_at_max_size > available_width:
            # Calculate the necessary scale factor
            scale_factor = available_width / text_width_at_max_size
            
            # Apply the scale factor to the max font size
            new_size = self.max_font_size * scale_factor
            
            # Set the new font size, ensuring a minimum readable size
            self.font_size = max(sp(15), new_size)
        else:
            self.font_size = self.max_font_size
            
        # Crucial step to ensure the text wraps/aligns correctly
        self.text_size = (self.width, None) 

# --- Base Utility Classes ---

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
        h = 128
        tex = Texture.create(size=(1, h), colorfmt='rgba')
        buf = bytearray()
        r1, g1, b1, a1 = self.color_top
        r2, g2, b2, a2 = self.color_bottom
        for i in range(h):
            t = i / (h - 1)
            r = int((r1 * (1 - t) + r2 * t) * 255)
            g = int((g1 * (1 - t) + g2 * t) * 255)
            b = int((b1 * (1 - t) + b2 * t) * 255)
            a = int((a1 * (1 - t) + a2 * t) * 255)
            buf += bytes((r, g, b, a))
        tex.blit_buffer(bytes(buf), colorfmt='rgba', bufferfmt='ubyte')
        tex.wrap = 'repeat'
        self.rect.texture = tex
        self.rect.tex_coords = (0, 0, 1, 0, 1, 1, 0, 1)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


def make_round_icon_button(char="⚙", bg=CARD_BG, size=dp(44), fg=TEXT_PRIMARY):
    root = AnchorLayout(size_hint=(None, None), size=(size, size))
    with root.canvas.before:
        Color(*bg)
        root._circle = Ellipse(size=root.size, pos=root.pos)
    def _sync(*_):
        root._circle.size = root.size
        root._circle.pos  = root.pos
    root.bind(size=_sync, pos=_sync)
    lbl = Label(text=char, color=fg, font_size=sp(20))
    root.add_widget(lbl)
    return root


def make_card(width, height, radius=dp(20), bg=CARD_BG, stroke=CARD_STROKE):
    cont = AnchorLayout(size_hint=(None, None), size=(width, height))
    with cont.canvas.before:
        Color(*bg); cont._bg = RoundedRectangle(radius=[radius]*4, pos=cont.pos, size=cont.size)
    with cont.canvas.after:
        Color(*stroke); cont._stroke = RoundedRectangle(radius=[radius]*4, pos=cont.pos, size=cont.size)
    def _sync(*_):
        cont._bg.pos = cont.pos; cont._bg.size = cont.size
        cont._stroke.pos = (cont.x - .5, cont.y - .5); cont._stroke.size = (cont.width + 1, cont.height + 1)
    cont.bind(pos=_sync, size=_sync)
    return cont


def make_dot(active=False):
    s = dp(8)
    w = Widget(size_hint=(None, None), size=(s, s))
    col = (1,1,1,0.9) if active else (1,1,1,0.25)
    with w.canvas:
        Color(*col); w._c = Ellipse(size=w.size, pos=w.pos)
    w.bind(size=lambda *_: setattr(w._c, 'size', w.size),
           pos=lambda *_: setattr(w._c, 'pos',  w.pos))
    return w

# --- Chip Maker ---
def make_chip(icon_char, text):
    # Chip size is size-to-content. size_hint=(None, None) is crucial here.
    chip = AnchorLayout(size_hint=(None, None), height=dp(34))
    
    lbl = Label(
        text=text, 
        color=TEXT_PRIMARY, font_size=sp(14),
        halign='center', valign='middle',
        padding=(dp(10), 0), size_hint=(None, None) 
    )
    
    def _fit(*_):
        lbl.texture_update()
        # Dynamically set chip size based on text size plus padding
        lbl.size = (lbl.texture_size[0] + dp(20), dp(28))
        chip.size = (lbl.width, dp(34))
    
    # Bind the size update to ensure the chip size follows the text
    lbl.bind(texture_size=_fit)
    _fit() # Initial call
    
    with chip.canvas.before:
        Color(0.22, 0.24, 0.30, 1)
        chip._bg = RoundedRectangle(radius=[dp(14)]*4, pos=chip.pos, size=chip.size)
    chip.bind(pos=lambda *_: setattr(chip._bg, 'pos', chip.pos),
              size=lambda *_: setattr(chip._bg, 'size', chip.size))
    chip.add_widget(lbl)
    
    return chip

# --- Category Tile Maker ---
def make_category_tile(title, subtitle, chips=None):
    # Increased height slightly to accommodate the new vertical centering of chips
    tile = AnchorLayout(size_hint=(1, None), height=dp(190)) 
    with tile.canvas.before:
        Color(*CARD_BG)
        tile._bg = RoundedRectangle(radius=[dp(18)]*4, pos=tile.pos, size=tile.size)
    tile.bind(pos=lambda *_: setattr(tile._bg, 'pos', tile.pos),
              size=lambda *_: setattr(tile._bg, 'size', tile.size))

    inner = BoxLayout(orientation='vertical', padding=[dp(16)]*2, spacing=dp(8)) 
    
    # --- TOP HALF AREA (Title & Subtitle) ---
    header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(75), spacing=dp(4)) 
    
    # Title Label (Centered)
    title_label = ScalableLabel(
        text=f"[b]{title}[/b]", markup=True, color=ACCENT,
        halign='center', valign='bottom', max_font_size_sp=sp(30), padding_dp=dp(5)
    )
    
    header.add_widget(title_label)
    
    # Subtitle Label (Centered)
    header.add_widget(
        Label(text=subtitle, color=TEXT_SECONDARY,
              font_size=sp(15), halign='center', valign='top', size_hint_y=None, height=dp(20))
    )
    inner.add_widget(header)

    # --- BOTTOM HALF AREA (Chips) ---
    if chips:
        
        # Container for horizontal centering of the chip group (single row)
        center_anchor = AnchorLayout(anchor_x='center', size_hint_y=1, padding=[0, dp(5), 0, 0])
        
        # Chip Group: All chips in one horizontal BoxLayout
        chip_row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint=(None, None), height=dp(34))
        
        # Manually calculate width based on children to ensure size_hint=(None, None) works
        def calculate_chip_row_width(*args):
            total_width = sum(chip.width for chip in chip_row.children)
            spacing_width = chip_row.spacing * (len(chip_row.children) - 1)
            chip_row.width = total_width + spacing_width
            chip_row.height = dp(34) # Height remains constant
            
        # Add chips and track them
        for ic, txt in chips:
            chip = make_chip(ic, txt)
            # Bind chip size changes to update the row width
            chip.bind(size=calculate_chip_row_width)
            chip_row.add_widget(chip)
        
        # Initial width calculation (necessary because we rely on chip sizes)
        # Note: Kivy's timing makes perfect auto-sizing hard, but this is the best approach.
        calculate_chip_row_width()

        center_anchor.add_widget(chip_row)
        inner.add_widget(center_anchor)
    else:
        inner.add_widget(Widget(size_hint_y=1)) 

    tile.add_widget(inner)
    return tile


# ------------------------ HOME SCREEN ------------------------
class HomeScreen(Screen):
    def __init__(self, server=None, **kwargs):
        super().__init__(name="home", **kwargs)
        self.server = server
        self.user_info = {}

        self.add_widget(GradientBackground())
        root = BoxLayout(orientation='vertical', padding=[dp(16), dp(8), dp(16), dp(8)], spacing=dp(12))
        self.root_layout = root
        self.add_widget(root)

        # TOP BAR
        topbar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(56))
        title = Label(text='[b][color=#33A3FF]smart id[/color][/b]', markup=True,
                      halign='left', valign='middle', color=TEXT_PRIMARY, font_size=sp(32))
        title.bind(size=lambda l, s: setattr(l, 'text_size', s))
        right = BoxLayout(size_hint_x=0.3, spacing=dp(10)) 
        right.add_widget(make_round_icon_button("⚙"))
        right.add_widget(make_round_icon_button("👤"))
        topbar.add_widget(title)
        topbar.add_widget(right)
        root.add_widget(topbar)

        self.welcome_label = Label(
            text='',
            markup=True,
            color=TEXT_SECONDARY,
            font_size=sp(16),
            size_hint=(1, None),
            height=0,
            halign='left',
            valign='middle'
        )
        self.welcome_label.bind(size=lambda lbl, size: setattr(lbl, 'text_size', (size[0], None)))
        root.add_widget(self.welcome_label)

        # HEADER
        head = BoxLayout(size_hint_y=None, height=dp(32))
        head.add_widget(Label(text="Portofel", color=TEXT_PRIMARY, font_size=sp(20), halign='left', valign='middle'))
        head.add_widget(Label(text="[color=#E5DB29]Intră în portofel[/color]", markup=True,
                              font_size=sp(15), size_hint_x=0.4,
                              halign='right', valign='middle', color=TEXT_SECONDARY))
        root.add_widget(head)

        # TRANSPORT CARD
        carousel_row = AnchorLayout(size_hint_y=None, height=dp(150))
        card = make_card(_clamp(Window.width * 0.9, dp(280), dp(700)), dp(130), radius=dp(22), bg=CARD_DARKER)
        self._main_card = card
        card_content = BoxLayout(orientation='horizontal', padding=[dp(16)]*2, spacing=dp(12))
        logo = AnchorLayout(size_hint=(None, 1), width=dp(90))
        with logo.canvas.before:
            Color(1,1,1,1)
            logo._lg_bg = RoundedRectangle(radius=[dp(16)]*4, pos=logo.pos, size=logo.size)
        logo.bind(pos=lambda *_: setattr(logo._lg_bg, 'pos', logo.pos),
                  size=lambda *_: setattr(logo._lg_bg, 'size', logo.size))
        card_content.add_widget(logo)

        v = BoxLayout(orientation='vertical', spacing=dp(4))
        v.add_widget(Label(text="Compania de Transport Public Iași S...", color=TEXT_SECONDARY, font_size=sp(14)))
        v.add_widget(Label(text="[b]Valabil până la 31.10.25 11:59[/b]", markup=True, color=TEXT_PRIMARY, font_size=sp(18)))
        v.add_widget(Label(text="Abonament o zonă", color=TEXT_SECONDARY, font_size=sp(14)))
        card_content.add_widget(v)
        card.add_widget(card_content)
        carousel_row.add_widget(card)
        root.add_widget(carousel_row)

        dots = BoxLayout(size_hint_y=None, height=dp(14), spacing=dp(6), padding=[0, 0, 0, dp(4)])
        dots.add_widget(Widget())
        dots.add_widget(make_dot(True))
        dots.add_widget(make_dot(False))
        dots.add_widget(Widget())
        root.add_widget(dots)

        # SCROLL GRID
        sv = ScrollView(size_hint=(1, 1))
        grid_wrap = BoxLayout(orientation='vertical', size_hint_y=None, padding=[0, dp(6), 0, dp(80)])
        grid_wrap.bind(minimum_height=grid_wrap.setter("height"))
        grid = GridLayout(cols=2, padding=[dp(8), dp(8)], spacing=dp(14), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        # CATEGORY CARDS (using the fixed tile maker)
        grid.add_widget(make_category_tile(
            "Personal Docs", "Carte de identitate, Permis auto, etc.",
            [("CI", "CI"), ("Permis", "Permis"), ("RCA", "RCA")] 
        ))
        grid.add_widget(make_category_tile(
            "Vehicul", "Asigurări, ITP, Talon auto.",
            [("Asigurări", "Asigurări"), ("Talon", "Talon")]
        ))
        grid.add_widget(make_category_tile(
            "Transport", "Abonamente și bilete.",
            [("Abonamente", "Abonamente"), ("Bilete", "Bilete")]
        ))
        grid.add_widget(make_category_tile(
            "Diverse", "Alte documente digitale.", 
            [("Biblioteca", "Biblioteca"), (None, "Arhiva")] 
        ))

        grid_wrap.add_widget(grid)
        sv.add_widget(grid_wrap)
        root.add_widget(sv) # <-- CORRECTED LINE
        # root.add_widget(root) <-- REMOVED ERROR LINE

        # BOTTOM BAR
        self._build_bottom_nav()

        def _update_card(*_):
            if self._main_card:
                self._main_card.size = (_clamp(Window.width * 0.9, dp(280), dp(700)), dp(130))

        _update_card()
        Window.bind(size=lambda *_: _update_card())

    def _build_bottom_nav(self):
        layer = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, None), height=dp(96))
        self.add_widget(layer)

        bar = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(64),
                        padding=[dp(16), 0, dp(16), 0], spacing=dp(12))
        with bar.canvas.before:
            Color(*(0.08, 0.10, 0.15, 1))
            bar._bg = Rectangle(pos=bar.pos, size=bar.size)
        bar.bind(pos=lambda *_: setattr(bar._bg, 'pos', bar.pos),
                 size=lambda *_: setattr(bar._bg, 'size', bar.size))

        left = BoxLayout(orientation='vertical', size_hint_x=0.25, padding=[0, dp(6), 0, dp(6)])
        left.add_widget(Label(text="🏠", font_size=sp(18), color=TEXT_SECONDARY))
        left.add_widget(Label(text="Acasă", font_size=sp(13), color=ACCENT_YELLOW))
        bar.add_widget(left)

        bar.add_widget(Widget()) 

        right = AnchorLayout(size_hint_x=0.4)
        right.add_widget(Label(text="[b][color=#33A3FF]AI CHAT BOT[/color][/b]", markup=True,
                               font_size=sp(18), color=ACCENT))
        bar.add_widget(right)

        layer.add_widget(bar)

        fab = AnchorLayout(size_hint=(None, None), size=(dp(72), dp(72)), anchor_x='center', anchor_y='center')
        with fab.canvas.before:
            Color(*ACCENT_YELLOW)
            fab._circle = Ellipse(size=fab.size, pos=fab.pos)
        fab.bind(pos=lambda *_: setattr(fab._circle, 'pos', fab.pos),
                 size=lambda *_: setattr(fab._circle, 'size', fab.size))
        fab.add_widget(Label(text="[b]Scanează[/b]", markup=True, color=(0,0,0,1), font_size=sp(14)))
        fab_container = AnchorLayout(anchor_x='center', anchor_y='bottom',
                                     size_hint=(1, None), height=dp(90), padding=[0, dp(8), 0, dp(8)])
        fab_container.add_widget(fab)
        layer.add_widget(fab_container)

    def set_server(self, server):
        self.server = server

    def set_user_info(self, user_info):
        self.user_info = user_info or {}
        username = self.user_info.get("username") or ""
        if username:
            self._set_welcome_text(
                f"[color=#9FB4D9]Welcome back,[/color] [b]{username}[/b]"
            )
        else:
            self._set_welcome_text("")

    def _set_welcome_text(self, text: str):
        if text:
            self.welcome_label.text = text
            self.welcome_label.texture_update()
            self.welcome_label.height = max(dp(24), self.welcome_label.texture_size[1] + dp(4))
        else:
            self.welcome_label.text = ""
            self.welcome_label.height = 0
