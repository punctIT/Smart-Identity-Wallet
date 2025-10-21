from kivy.metrics import dp, sp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label


class LinkLabel(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_text = kwargs.get("text", "")
        self.bind(on_press=self._on_press_effect, on_release=self._on_release_effect)

    def _on_press_effect(self, *_):
        darker = (
            self.original_text.replace("#9FB4D9", "#7C97C8").replace("#3F86FF", "#2E66CC")
        )
        self.text = darker

    def _on_release_effect(self, *_):
        self.text = self.original_text


class CustomLabels:
    def make_error_label(self):
        lbl = Label(
            text="",
            color=(1, 0.35, 0.4, 1),
            size_hint=(1, None),
            height=0,
            font_size=sp(13),
            halign="left",
            valign="middle",
        )
        lbl.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        return lbl


class ScalableLabel(Label):
    """Label that shrinks to avoid overflow and can enforce single-line layout."""

    def __init__(
        self,
        *,
        max_font_size_sp=sp(30),
        min_font_size_sp=sp(15),
        padding_dp=dp(10),
        enforce_single_line=False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.max_font_size = max_font_size_sp
        self.min_font_size = min_font_size_sp
        self.padding_dp = padding_dp
        self.enforce_single_line = enforce_single_line
        self.bind(size=self._update_font_size, text=self._update_font_size)

    def _update_font_size(self, *_):
        if not self.text or self.width <= 0:
            return

        available_width = self.width - (self.padding_dp * 2)
        if available_width <= 0:
            return

        # Start from the maximum size and shrink until it fits.
        target_size = self.max_font_size
        self.font_size = target_size
        self.texture_update()

        if self.texture_size[0] > available_width:
            scale_factor = available_width / max(self.texture_size[0], 1)
            target_size = max(self.min_font_size, self.max_font_size * scale_factor)
            self.font_size = target_size
            self.texture_update()

        step = sp(1)
        while self.font_size > self.min_font_size and self.texture_size[0] > available_width:
            self.font_size = max(self.min_font_size, self.font_size - step)
            self.texture_update()

        if self.enforce_single_line:
            desired_height = self.font_size * 1.35
            while self.font_size > self.min_font_size and self.texture_size[1] > desired_height:
                self.font_size = max(self.min_font_size, self.font_size - step)
                self.texture_update()

        self.text_size = (self.width - self.padding_dp * 2, None)
