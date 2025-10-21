from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.metrics import dp, sp 


class Alignment:
    def __init__(self):
        pass
    def _clamp(self,val, lo, hi):
        return max(lo, min(hi, val))

    # --- Safe-area helpers -------------------------------------------------
    @staticmethod
    def _px_to_dp(px: float) -> float:
        dpi = getattr(Window, "dpi", 160) or 160
        return px / (dpi / 160.0)

    def _safe_insets(self):
        insets = getattr(Window, "insets", None)
        if not insets:
            return {"top": 0, "bottom": 0, "left": 0, "right": 0}
        return {
            "top": self._px_to_dp(getattr(insets, "top", 0)),
            "bottom": self._px_to_dp(getattr(insets, "bottom", 0)),
            "left": self._px_to_dp(getattr(insets, "left", 0)),
            "right": self._px_to_dp(getattr(insets, "right", 0)),
        }

    def _safe_top_padding(self, extra_dp: float = 0) -> float:
        return dp(self._safe_insets().get("top", 0) + extra_dp)

    def _safe_bottom_padding(self, extra_dp: float = 0) -> float:
        return dp(self._safe_insets().get("bottom", 0) + extra_dp)

    def center_row(self,child, *, rel_width=0.85, min_w=dp(260), max_w=dp(520), height=None):
        row = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, None),
                        height=height if height is not None else (child.height or dp(46)))
        child.size_hint_x = None
        def _bind_width(_row, _val):
            target = self._clamp(row.width * rel_width, min_w, max_w)
            child.width = target
        row.bind(width=_bind_width)
        row.add_widget(child)
        return row
