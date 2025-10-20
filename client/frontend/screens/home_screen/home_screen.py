from kivy.core.window import Window
from kivy.clock import Clock
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



from frontend.screens.widgets.custom_label import ScalableLabel
from frontend.screens.widgets.custom_background import GradientBackground
from frontend.screens.widgets.custom_buttons import CustomButton
from frontend.screens.widgets.custom_alignment import Alignment
from frontend.screens.widgets.custom_cards import CustomCards


# ------------------------ THEME ------------------------
BG_TOP      = (0.06, 0.07, 0.10, 1)
BG_BOTTOM   = (0.03, 0.05, 0.09, 1)
CARD_BG     = (0.13, 0.15, 0.20, 1)
CARD_STROKE = (1, 1, 1, 0.06)

TEXT_PRIMARY   = (0.92, 0.95, 1.00, 1)
TEXT_SECONDARY = (0.70, 0.76, 0.86, 1)
ACCENT         = (0.25, 0.60, 1.00, 1)   # blue
ACCENT_SOFT    = (0.12, 0.35, 0.70, 1)
ACCENT_YELLOW  = "#FAE629"  

CARD_DARKER    = (0.11, 0.13, 0.18, 1)

Window.clearcolor = BG_BOTTOM

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
]

CATEGORY_SCREEN_NAMES = [item["screen_name"] for item in CATEGORY_TILE_CONFIG]





# --- New Clickable Category Tile Class ---
class CategoryTile(ButtonBehavior, AnchorLayout):
    def __init__(self, sm, screen_name, title, subtitle, **kwargs):
        super().__init__(**kwargs)
        self.sm = sm if hasattr(sm, "has_screen") else None
        self.screen_name = screen_name
        self.size_hint = (1, None)
        self.height = dp(210)
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

        inner = BoxLayout(orientation='vertical', padding=[dp(16)]*2, spacing=dp(8)) 

        header = BoxLayout(orientation='vertical', size_hint=(1, None), spacing=dp(4))
        header.bind(minimum_height=header.setter("height"))

        self.title_label = ScalableLabel(
            text=f"[b]{title}[/b]",
            markup=True,
            color=ACCENT,
            halign='center',
            valign='middle',
            max_font_size_sp=sp(26),
            padding_dp=dp(6),
            size_hint=(1, None)
        )
        self.title_label.bind(size=lambda lbl, size: setattr(lbl, "text_size", (size[0], None)))
        self.title_label.bind(texture_size=lambda *_: self._update_height())
        header.add_widget(self.title_label)

        self.subtitle_label = Label(
            text=subtitle,
            color=TEXT_SECONDARY,
            font_size=sp(14),
            halign='center',
            valign='middle',
            size_hint=(1, None),
            height=dp(20)
        )
        def _update_subtitle(_lbl, *_):
            _lbl.height = max(_lbl.texture_size[1], dp(20))
            self._update_height()

        self.subtitle_label.bind(
            size=lambda lbl, size: setattr(lbl, "text_size", (size[0], None)),
            texture_size=_update_subtitle
        )
        header.add_widget(self.subtitle_label)

        inner.add_widget(Widget(size_hint_y=1))
        inner.add_widget(header)
        inner.add_widget(Widget(size_hint_y=1))

        self.add_widget(inner)
        self.bind(width=lambda *_: self._update_height())
        Clock.schedule_once(lambda *_: self._update_height(), 0)

    # --- CLICK BEHAVIOR ---
    def on_release(self):
        print(self.screen_name)
        self.sm.current=self.screen_name

    def _update_height(self, *_):
        self.title_label.texture_update()
        self.subtitle_label.texture_update()
        inner_height = (
            dp(32) + self.title_label.texture_size[1] + self.subtitle_label.texture_size[1]
        )
        target = max(dp(190), inner_height)
        self.height = target


class FloatingScanButton(ButtonBehavior, AnchorLayout):
    def __init__(self, text, text_color, bg_color, on_activate, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(72), dp(72))
        self._on_activate = on_activate
        with self.canvas.before:
            Color(*bg_color)
            self._circle = Ellipse(size=self.size, pos=self.pos)

        def _sync(*_):
            self._circle.size = self.size
            self._circle.pos = self.pos

        self.bind(size=_sync, pos=_sync)
        self.add_widget(Label(text=text, markup=True, color=text_color, font_size=sp(14)))

    def on_release(self):
        if callable(self._on_activate):
            self._on_activate()
    
class HomeScreen(Screen, CustomButton, CustomCards, Alignment):
    def on_enter(self, *args):
        data=self.server.get_specific_data("News")
        if data['success']==True:
            
            news = data['data']['news']
            if len(news) !=0:
                self.main_carousel.clear_widgets()
                self.dots.clear_widgets()
                self.dots.add_widget(Widget())
            for new in news:
                self.dots.add_widget(self.make_dot(0))
                self.main_carousel.add_widget(self.create_news_card(
                    new['Title'], new['Description'], "#FFFFFF"
                ))
            self.dots.add_widget(Widget())
       
        
       
    def __init__(self, sm=None, server=None, **kwargs):
        super().__init__(name="home", **kwargs)
        self.server = server
        self.user_info = {}
        self.sm = sm if hasattr(sm, "has_screen") else None 
        self._back_binding = False
        self.add_widget(GradientBackground())
        root = BoxLayout(orientation='vertical', padding=[dp(16), dp(4), dp(16), dp(4)], spacing=dp(8))

        self.add_widget(root)

        # TOP BAR
        topbar = BoxLayout(
            orientation='vertical', 
            size_hint_y=0.25,  # 25% pentru main content
            spacing=dp(2)
        )
        title = Label(text='[b][color=#33A3FF]smart id[/color][/b]', markup=True,
                      halign='left', valign='middle', color=TEXT_PRIMARY, font_size=sp(32))
        title.bind(size=lambda l, s: setattr(l, 'text_size', s))
        
        self.main_container = BoxLayout(
            orientation='vertical', 
            size_hint_y=0.25,  # 25% pentru main content
            spacing=dp(10)
        )
        
        sv = ScrollView(size_hint=(1, 0.75))
        
        topbar.add_widget(title)
    
        root.add_widget(topbar)

     
      
        self.main_container.bind(minimum_height=self.main_container.setter('height'))


       
        carousel_row = AnchorLayout(size_hint_y=None, height=dp(150))

        self.main_carousel = Carousel(
            direction='right',
            anim_move_duration=0.2,
            size_hint=(1, 1)
        )

        self.main_carousel.add_widget(self.create_news_card(
                "Nimic nou", "nu exista noutati", "#FFFFFF"
        ))

        carousel_row.add_widget(self.main_carousel)
        self.main_container.add_widget(carousel_row)  # Adaugă în container

        self.dots = BoxLayout(size_hint_y=None, height=dp(14), spacing=dp(6), padding=[0, 0, 0, dp(4)])
        self.dot_widgets = [self.make_dot(i == 0) for i in range(len(self.main_carousel.children)+1)]

        self.dots.add_widget(Widget())
        for dot in self.dot_widgets:
            self.dots.add_widget(dot)
        self.dots.add_widget(Widget())

        self.main_container.add_widget(self.dots) 

        def update_dots(instance, value):
            current_index = self.main_carousel.index
            for i, dot in enumerate(self.dot_widgets):
                target_color = (1,1,1,0.9) if i == current_index else (1,1,1,0.25)
                dot._color_instr.rgba = target_color

        self.main_carousel.bind(index=update_dots)
        self.main_container.size_hint_y = 0.2 
        root.add_widget(self.main_container)

       
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
            ))

        grid_wrap.add_widget(grid)
        sv.add_widget(grid_wrap)
        root.add_widget(sv)

        # BOTTOM BAR
        self._build_bottom_nav()

        def _update_card(*_):
            # Update size for card based on window size
            new_width = self._clamp(Window.width * 0.9, dp(280), dp(700))
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

    def on_pre_enter(self, *_):
        if not self._back_binding:
            Window.bind(on_keyboard=self._handle_back_gesture)
            self._back_binding = True

    def on_leave(self, *_):
        if self._back_binding:
            Window.unbind(on_keyboard=self._handle_back_gesture)
            self._back_binding = False

    def _handle_back_gesture(self, window, key, scancode, codepoint, modifier):
        if key in (27, 1001):  # Android back button or gesture
            app = App.get_running_app()
            if app:
                app.stop()
            return True
        return False

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

        def _go_to_scan():
            manager = self.manager
            if manager and manager.has_screen('camera_scan'):
                transition = getattr(manager, "transition", None)
                previous_direction = getattr(transition, "direction", None)
                if transition:
                    transition.direction = 'up'
                manager.current = 'camera_scan'
                if transition and previous_direction:
                    transition.direction = previous_direction

        fab = FloatingScanButton(
            text="[b]Scanează[/b]",
            text_color=(0, 0, 0, 1),
            bg_color=ACCENT_YELLOW,
            on_activate=_go_to_scan,
            anchor_x='center',
            anchor_y='center'
        )
        fab_container = AnchorLayout(anchor_x='center', anchor_y='bottom',
                                     size_hint=(1, None), height=dp(90), padding=[0, dp(8), 0, dp(8)])
        fab_container.add_widget(fab)
        layer.add_widget(fab_container)

    def set_server(self, server):
        self.server = server


__all__ = ["CATEGORY_TILE_CONFIG", "CATEGORY_SCREEN_NAMES", "HomeScreen"]
