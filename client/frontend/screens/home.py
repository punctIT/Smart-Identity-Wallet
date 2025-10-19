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

CATEGORY_TILE_CONFIG = [
    {
        "screen_name": "personal_docs",
        "title": "Personal Docs",
        "subtitle": "Carte de identitate, Permis auto, etc.",
        "chips": [("CI", "CI"), ("Permis", "Permis"), ("RCA", "RCA")],
    },
    {
        "screen_name": "vehicul_docs",
        "title": "Vehicul",
        "subtitle": "Asigurări, ITP, Talon auto.",
        "chips": [("Asigurări", "Asigurări"), ("Talon", "Talon")],
    },
    {
        "screen_name": "transport_docs",
        "title": "Transport",
        "subtitle": "Abonamente și bilete.",
        "chips": [("Abonamente", "Abonamente"), ("Bilete", "Bilete")],
    },
    {
        "screen_name": "diverse_docs",
        "title": "Diverse",
        "subtitle": "Alte documente digitale.",
        "chips": [("Biblioteca", "Biblioteca"), (None, "Arhiva")],
    },
]

CATEGORY_SCREEN_NAMES = [item["screen_name"] for item in CATEGORY_TILE_CONFIG]

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
    # FIX: Replaced Unicode icon with text to prevent placeholder squares
    if char == "⚙":
        display_char = "SET"
    elif char == "👤":
        display_char = "USER"
    else:
        display_char = char

    root = AnchorLayout(size_hint=(None, None), size=(size, size))
    with root.canvas.before:
        Color(*bg)
        root._circle = Ellipse(size=root.size, pos=root.pos)
    def _sync(*_):
        root._circle.size = root.size
        root._circle.pos  = root.pos
    root.bind(size=_sync, pos=_sync)
    lbl = Label(text=display_char, color=fg, font_size=sp(12) if len(display_char) > 1 else sp(20))
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
        w._color_instr = Color(*col) # Store Color instruction for dynamic updates
        w._c = Ellipse(size=w.size, pos=w.pos)
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

# --- New Clickable Category Tile Class ---
class CategoryTile(ButtonBehavior, AnchorLayout):
    def __init__(self, sm, screen_name, title, subtitle, chips=None, **kwargs):
        super().__init__(**kwargs)
        self.sm = sm if hasattr(sm, "has_screen") else None
        self.screen_name = screen_name
        self.size_hint = (1, None)
        self.height = dp(190)

        # --- DRAWING / APPEARANCE LOGIC ---
        with self.canvas.before:
            Color(*CARD_BG)
            self._bg = RoundedRectangle(radius=[dp(18)]*4, pos=self.pos, size=self.size)
        with self.canvas.after:
            Color(*CARD_STROKE)
            self._stroke = RoundedRectangle(radius=[dp(18)]*4, pos=self.pos, size=self.size)
        
        def _sync(*_):
            self._bg.pos = self.pos
            self._bg.size = self.size
            self._stroke.pos = (self.x - .5, self.y - .5)
            self._stroke.size = (self.width + 1, self.height + 1)
        self.bind(pos=_sync, size=_sync)

        # --- INNER CONTENT LAYOUT ---
        inner = BoxLayout(orientation='vertical', padding=[dp(16)]*2, spacing=dp(8)) 
        
        # TOP HALF AREA (Title & Subtitle)
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(75), spacing=dp(4)) 
        
        title_label = ScalableLabel(
            text=f"[b]{title}[/b]", markup=True, color=ACCENT,
            halign='center', valign='bottom', max_font_size_sp=sp(30), padding_dp=dp(5)
        )
        header.add_widget(title_label)
        
        header.add_widget(
            Label(text=subtitle, color=TEXT_SECONDARY,
                  font_size=sp(15), halign='center', valign='top', size_hint_y=None, height=dp(20))
        )
        inner.add_widget(header)

        # BOTTOM HALF AREA (Chips)
        if chips:
            # Container for horizontal centering of the chip group (single row)
            center_anchor = AnchorLayout(anchor_x='center', size_hint_y=1, padding=[0, dp(5), 0, 0])
            chip_row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint=(None, None), height=dp(34))
            
            # Manually calculate width based on children to ensure size-to-content works
            def calculate_chip_row_width(*args):
                total_width = sum(chip.width for chip in chip_row.children)
                spacing_width = chip_row.spacing * (len(chip_row.children) - 1)
                chip_row.width = total_width + spacing_width
            
            for ic, txt in chips:
                chip = make_chip(ic, txt)
                chip.bind(size=calculate_chip_row_width)
                chip_row.add_widget(chip)
            
            calculate_chip_row_width() # Initial width calculation
            center_anchor.add_widget(chip_row)
            inner.add_widget(center_anchor)
        else:
            inner.add_widget(Widget(size_hint_y=1)) 

        self.add_widget(inner)

    # --- CLICK BEHAVIOR ---
    def on_release(self):
        manager = self._resolve_manager()
        if manager and manager.has_screen(self.screen_name):
            manager.transition.direction = 'left'
            manager.current = self.screen_name

    def _resolve_manager(self):
        if self.sm and hasattr(self.sm, "has_screen"):
            return self.sm
        app = App.get_running_app()
        if app and hasattr(app, "root"):
            return app.root
        parent = self.parent
        while parent:
            mgr = getattr(parent, "manager", None)
            if mgr:
                return mgr
            parent = getattr(parent, "parent", None)
        return None

# ------------------------ HOME SCREEN ------------------------
class HomeScreen(Screen):
    # Added sm (ScreenManager) argument
    def __init__(self, sm=None, server=None, **kwargs):
        super().__init__(name="home", **kwargs)
        self.server = server
        self.user_info = {}
        self.sm = sm if hasattr(sm, "has_screen") else None  # Store ScreenManager reference

        self.add_widget(GradientBackground())
        root = BoxLayout(orientation='vertical', padding=[dp(16), dp(8), dp(16), dp(8)], spacing=dp(12))
        self.root_layout = root
        self.add_widget(root)

        # TOP BAR
        topbar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(56))
        title = Label(text='[b][color=#33A3FF]smart id[/color][/b]', markup=True,
                      halign='left', valign='middle', color=TEXT_PRIMARY, font_size=sp(32))
        title.bind(size=lambda l, s: setattr(l, 'text_size', s))
        # Icons are handled by make_round_icon_button (Displays "SET" and "USER")
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

        # --- CONVERTED AREA: TRANSPORT CARD TO SLIDEABLE CAROUSEL ---
        
        # 1. Carousel Container: AnchorLayout for size management
        carousel_row = AnchorLayout(size_hint_y=None, height=dp(150))
        
        # 2. Carousel Widget
        self.main_carousel = Carousel(
            direction='right',
            anim_move_duration=0.2,
            size_hint=(1.0, 1.0)
        )
        
        # Helper function to create a slide card
        def create_news_card(title_text, subtitle_text, accent_color):
            card_width = _clamp(Window.width * 0.9, dp(280), dp(700))
            card = make_card(card_width, dp(130), radius=dp(22), bg=CARD_DARKER)
            self._main_card = card # Keep reference for size updates
            
            card_content = BoxLayout(orientation='horizontal', padding=[dp(16)]*2, spacing=dp(12))
            
            # Left side (Placeholder for image/icon)
            logo = AnchorLayout(size_hint=(None, 1), width=dp(90))
            with logo.canvas.before:
                Color(1,1,1,1)
                logo._lg_bg = RoundedRectangle(radius=[dp(16)]*4, pos=logo.pos, size=logo.size)
            logo.bind(pos=lambda *_: setattr(logo._lg_bg, 'pos', logo.pos),
                      size=lambda *_: setattr(logo._lg_bg, 'size', logo.size))
            card_content.add_widget(logo)

            # Right side (Text content)
            v = BoxLayout(orientation='vertical', spacing=dp(4))
            v.add_widget(Label(text=subtitle_text, color=TEXT_SECONDARY, font_size=sp(14), halign='left', valign='bottom'))
            v.add_widget(Label(text=f"[b][color={accent_color}]{title_text}[/color][/b]", markup=True, color=TEXT_PRIMARY, font_size=sp(18), halign='left', valign='middle'))
            v.add_widget(Label(text="Apăsați pentru detalii", color=TEXT_SECONDARY, font_size=sp(14), halign='left', valign='top'))
            card_content.add_widget(v)
            card.add_widget(card_content)
            
            # Add card content to a BoxLayout to hold it inside the Carousel
            slide = BoxLayout(orientation='vertical')
            # FIX: Ensure card widget is centered in the slide
            center_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 1))
            center_anchor.add_widget(card)
            slide.add_widget(center_anchor)
            return slide

        # Add multiple slides to the carousel
        self.main_carousel.add_widget(create_news_card(
            "Noutăți Zone ITP", "Verificați reglementările noi de azi.", "#FFFFFF"
        ))
        self.main_carousel.add_widget(create_news_card(
            "Abonament Zonal (Exp)", "Valabil până la 31.10.25 11:59", ACCENT_YELLOW
        ))
        self.main_carousel.add_widget(create_news_card(
            "Anunțuri Trafic", "Restricții de circulație și devieri.", "#FF6666"
        ))

        carousel_row.add_widget(self.main_carousel)
        root.add_widget(carousel_row)

        # 3. Dots indicator (connected to the carousel)
        dots = BoxLayout(size_hint_y=None, height=dp(14), spacing=dp(6), padding=[0, 0, 0, dp(4)])
        self.dot_widgets = [make_dot(i == 0) for i in range(len(self.main_carousel.children))]
        
        dots.add_widget(Widget())
        for dot in self.dot_widgets:
            dots.add_widget(dot)
        dots.add_widget(Widget())
        root.add_widget(dots)
        
        # Link dots to carousel index
        def update_dots(instance, value):
            current_index = self.main_carousel.index
            for i, dot in enumerate(self.dot_widgets):
                target_color = (1,1,1,0.9) if i == current_index else (1,1,1,0.25)
                # FIX: Access the stored Color instruction to update the dot color
                dot._color_instr.rgba = target_color
        self.main_carousel.bind(index=update_dots)

        # SCROLL GRID
        sv = ScrollView(size_hint=(1, 1))
        grid_wrap = BoxLayout(orientation='vertical', size_hint_y=None, padding=[0, dp(6), 0, dp(80)])
        grid_wrap.bind(minimum_height=grid_wrap.setter("height"))
        grid = GridLayout(cols=2, padding=[dp(8), dp(8)], spacing=dp(14), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        # CATEGORY CARDS (Now using the clickable CategoryTile class)
        for tile in CATEGORY_TILE_CONFIG:
            grid.add_widget(CategoryTile(
                sm=self.sm,
                screen_name=tile["screen_name"],
                title=tile["title"],
                subtitle=tile["subtitle"],
                chips=tile.get("chips"),
            ))

        grid_wrap.add_widget(grid)
        sv.add_widget(grid_wrap)
        root.add_widget(sv)

        # BOTTOM BAR
        self._build_bottom_nav()

        def _update_card(*_):
            # Update size for card based on window size
            new_width = _clamp(Window.width * 0.9, dp(280), dp(700))
            if self.main_carousel:
                # Iterate through all slides and update the size of the inner card
                for slide in self.main_carousel.slides:
                    # Logic to find the inner card within the AnchorLayout
                    if slide.children and slide.children[0].children:
                        card_container = slide.children[0]
                        if card_container.children:
                            card_widget = card_container.children[0] 
                            # If card_widget is indeed the card from make_card
                            if isinstance(card_widget, AnchorLayout):
                                card_widget.size = (new_width, dp(130))


        Window.bind(size=lambda *_: _update_card())
        _update_card() # Initial call
        self.bind(manager=self._bind_manager)

    def _bind_manager(self, *_):
        if hasattr(self, "manager") and hasattr(self.manager, "has_screen"):
            self.sm = self.manager

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


__all__ = ["CATEGORY_TILE_CONFIG", "CATEGORY_SCREEN_NAMES", "HomeScreen"]
