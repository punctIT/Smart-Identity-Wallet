from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp, sp 

class LinkLabel(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_text = kwargs.get("text", "")
        self.bind(on_press=self.on_press_effect, on_release=self.on_release_effect)

    def on_press_effect(self, *_):
        darker = (self.original_text
                  .replace("#9FB4D9", "#7C97C8")
                  .replace("#3F86FF", "#2E66CC"))
        self.text = darker

    def on_release_effect(self, *_):
        self.text = self.original_text
        
class CustomLabels:
    def make_error_label(self):
        lbl = Label(text='',
                    color=(1, 0.35, 0.4, 1),
                    size_hint=(1, None),
                    height=0,
                    font_size=sp(13),
                    halign='left',
                    valign='middle')
        lbl.bind(size=lambda l, s: setattr(l, 'text_size', (s[0], None)))
        return lbl
    

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