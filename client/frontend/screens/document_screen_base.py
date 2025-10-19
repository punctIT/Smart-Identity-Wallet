from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from .ui_components import ACCENT, TEXT_PRIMARY, TEXT_SECONDARY, GradientBackground


class BaseDocumentScreen(Screen):
    def __init__(self, *, name: str, title: str, description: str, server=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.server = server
        self._title = title
        self._description = description

        self.add_widget(GradientBackground())
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(20))
        self.add_widget(root)

        header = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(10))
        back_button = Button(
            text="< Acasă",
            size_hint=(None, None),
            size=(dp(120), dp(40)),
            font_size=sp(16),
            color=ACCENT,
            background_normal="",
            background_color=(0, 0, 0, 0),
        )
        back_button.bind(on_release=lambda *_: self._go_home())
        header.add_widget(back_button)

        title_label = Label(
            text=f"[b]{self._title}[/b]",
            markup=True,
            font_size=sp(30),
            color=TEXT_PRIMARY,
            halign="left",
            valign="middle",
        )
        title_label.bind(size=lambda label, size: setattr(label, "text_size", size))
        header.add_widget(title_label)
        root.add_widget(header)

        if self._description:
            scroll = ScrollView(size_hint=(1, 1))
            content = Label(
                text=self._description,
                markup=True,
                color=TEXT_SECONDARY,
                font_size=sp(18),
                valign="top",
                halign="left",
                size_hint_y=None,
            )
            content.bind(texture_size=lambda lbl, size: setattr(lbl, "height", size[1]))
            content.bind(size=lambda lbl, size: setattr(lbl, "text_size", (size[0], None)))
            scroll.add_widget(content)
            root.add_widget(scroll)
        else:
            root.add_widget(Widget())

    def set_server(self, server):
        self.server = server

    def _go_home(self):
        if self.manager:
            self.manager.transition.direction = "right"
            self.manager.current = "home"


__all__ = ["BaseDocumentScreen"]
