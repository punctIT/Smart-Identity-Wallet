from typing import Iterable, List, Optional, Sequence

from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from frontend.screens.widgets.custom_alignment import Alignment
from frontend.screens.widgets.custom_background import GradientBackground
from frontend.screens.widgets.custom_cards import CustomCards
from frontend.screens.widgets.custom_label import ScalableLabel


class DocumentListMixin(CustomCards, Alignment):
    """Reusable mixin that renders a responsive list of document cards."""

    BASE_WIDTH = 412
    BASE_HEIGHT = 915
    MIN_SCALE = 0.75
    MAX_SCALE = 1.6

    TITLE_FONT = 30
    SUBTITLE_FONT = 17
    TITLE_CARD_FONT = 21
    SUBTITLE_CARD_FONT = 13
    META_FONT = 12

    ROOT_PADDING = (16, 10, 16, 16)
    ROOT_SPACING = 12
    CARDS_SPACING = 14
    CARD_PADDING = (18, 16)
    CARD_RADIUS = 22
    CARD_MIN_HEIGHT = 132
    CARD_EXTRA_HEIGHT = 22
    EMPTY_HEIGHT = 220

    TITLE_COLOR = "#33A3FF"
    TITLE_TEXT = "Documente"
    SUBTITLE_TEXT = ""
    EMPTY_TEXT = "Nu există documente disponibile momentan."

    def setup_document_screen(
        self,
        *,
        server=None,
        title_text: Optional[str] = None,
        subtitle_text: Optional[str] = None,
        empty_text: Optional[str] = None,
    ) -> None:
        self.server = server

        self._title_text = title_text or self.TITLE_TEXT
        self._subtitle_text = subtitle_text or self.SUBTITLE_TEXT
        self._empty_text = empty_text or self.EMPTY_TEXT

        self.scale_ratio = self._compute_scale()
        self.documents: List[dict] = []
        self._doc_widgets = []

        Window.bind(size=self._on_window_resize)

        self.bg = GradientBackground()
        self.add_widget(self.bg)

        self._build_ui()
        self._apply_scale()

    def set_documents(self, documents: Optional[Iterable[dict]]) -> None:
        self.documents = list(documents or [])
        self._refresh_documents()

    def append_document(self, document: dict) -> None:
        self.documents.append(document)
        self._refresh_documents()

    # ---------------------------------------------------------------------
    # Layout construction helpers
    # ---------------------------------------------------------------------
    def _build_ui(self) -> None:
        base_padding = [self._scale_dp(v) for v in self.ROOT_PADDING]
        if hasattr(self, "_safe_top_padding"):
            base_padding[1] = self._safe_top_padding(self.ROOT_PADDING[1])
            base_padding[3] = self._safe_bottom_padding(self.ROOT_PADDING[3])

        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=base_padding,
            spacing=self._scale_dp(self.ROOT_SPACING),
        )
        self.add_widget(self.root_layout)

        self.header_box = BoxLayout(orientation="vertical", size_hint_y=None)
        self.header_box.bind(minimum_height=self.header_box.setter("height"))

        self.title_label = Label(
            text=f"[b][color={self.TITLE_COLOR}]{self._title_text}[/color][/b]",
            markup=True,
            color=(1, 1, 1, 1),
            halign="left",
            valign="middle",
            size_hint=(1, None),
        )
        self.title_label.bind(size=lambda lbl, size: setattr(lbl, "text_size", size))
        self.header_box.add_widget(self.title_label)

        self.subtitle_label = Label(
            text=self._subtitle_text,
            color=(0.70, 0.76, 0.86, 1),
            halign="left",
            valign="top",
            size_hint=(1, None),
        )
        self.subtitle_label.bind(size=lambda lbl, size: setattr(lbl, "text_size", size))
        self.header_box.add_widget(self.subtitle_label)

        self.root_layout.add_widget(self.header_box)

        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.root_layout.add_widget(self.scroll_view)

        bottom_padding = self._scale_dp(self.CARDS_SPACING * 2) + self._safe_bottom_padding(24)

        self.cards_container = BoxLayout(
            orientation="vertical",
            spacing=self._scale_dp(self.CARDS_SPACING),
            padding=[0, self._scale_dp(6), 0, bottom_padding],
            size_hint_y=None,
        )
        self.cards_container.bind(minimum_height=self.cards_container.setter("height"))
        self.scroll_view.add_widget(self.cards_container)

        self.empty_state_anchor = AnchorLayout(size_hint=(1, None))
        self.empty_state_label = Label(
            text=self._empty_text,
            color=(0.70, 0.76, 0.86, 1),
            halign="center",
            valign="middle",
            size_hint=(0.9, None),
        )
        self.empty_state_label.bind(size=lambda lbl, size: setattr(lbl, "text_size", size))
        self.empty_state_anchor.add_widget(self.empty_state_label)

        self.bottom_spacer = Widget(size_hint_y=None)

        self._refresh_documents()

    def _refresh_documents(self) -> None:
        self.cards_container.clear_widgets()
        self._doc_widgets.clear()

        if not self.documents:
            self.empty_state_anchor.height = self._scale_dp(self.EMPTY_HEIGHT)
            self.cards_container.add_widget(self.empty_state_anchor)
            for extra_row in self._get_additional_cards():
                if extra_row:
                    self.cards_container.add_widget(extra_row)
            self.cards_container.add_widget(self.bottom_spacer)
            self._apply_scale()
            return

        for doc in self.documents:
            card_row = self._create_document_card(doc)
            self.cards_container.add_widget(card_row)

        for extra_row in self._get_additional_cards():
            if extra_row:
                self.cards_container.add_widget(extra_row)

        self.cards_container.add_widget(self.bottom_spacer)
        self._apply_scale()

    def _create_document_card(self, doc: dict) -> AnchorLayout:
        title = (
            doc.get("title")
            or doc.get("name")
            or doc.get("document_name")
            or "Document"
        )
        meta_lines = self._collect_meta_lines(doc)

        base_height = self.CARD_MIN_HEIGHT + self.CARD_EXTRA_HEIGHT * max(len(meta_lines), 0)
        base_width = self._compute_card_width()

        card = self.make_card(base_width, base_height, radius=self.CARD_RADIUS)

        content = BoxLayout(
            orientation="vertical",
            padding=[
                self._scale_dp(self.CARD_PADDING[0]),
                self._scale_dp(self.CARD_PADDING[1]),
                self._scale_dp(self.CARD_PADDING[0]),
                self._scale_dp(self.CARD_PADDING[1]),
            ],
            spacing=self._scale_dp(8),
        )

        title_label = ScalableLabel(
            text=f"[b]{title}[/b]",
            markup=True,
            color=(0.92, 0.95, 1.00, 1),
            halign="left",
            valign="middle",
            max_font_size_sp=self._scale_sp(self.TITLE_CARD_FONT),
            padding_dp=self._scale_dp(4),
            size_hint=(1, None),
        )
        title_label.bind(size=lambda lbl, size: setattr(lbl, "text_size", (size[0], None)))
        title_updater = self._bind_dynamic_height(title_label, padding_dp=6)
        content.add_widget(title_label)

        meta_labels = []
        meta_updaters = []
        for line in meta_lines:
            lbl = Label(
                text=line,
                color=(0.70, 0.76, 0.86, 1),
                font_size=self._scale_sp(self.META_FONT),
                halign="left",
                valign="middle",
                size_hint=(1, None),
            )
            lbl.bind(size=lambda label, size: setattr(label, "text_size", (size[0], None)))
            meta_updaters.append(self._bind_dynamic_height(lbl, padding_dp=2))
            content.add_widget(lbl)
            meta_labels.append(lbl)

        card.add_widget(content)

        row = self.center_row(
            card,
            rel_width=0.92,
            min_w=self._scale_dp(260),
            max_w=self._scale_dp(560),
        )
        row.padding = [0, self._scale_dp(4), 0, self._scale_dp(4)]
        card.bind(height=lambda *_: setattr(row, "height", card.height + self._scale_dp(8)))

        self._register_card_entry(
            row=row,
            card=card,
            content=content,
            title=title_label,
            meta=meta_labels,
            base_height=base_height,
            height_updaters=[
                updater
                for updater in (title_updater, *meta_updaters)
                if updater
            ],
        )

        return row

    def _get_additional_cards(self) -> Sequence[AnchorLayout]:
        return []

    def _register_card_entry(
        self,
        *,
        row: AnchorLayout,
        card: AnchorLayout,
        content: Optional[Widget] = None,
        title: Optional[Widget] = None,
        meta: Optional[Sequence[Widget]] = None,
        base_height: float = 0,
        height_updaters: Optional[Sequence] = None,
    ) -> None:
        self._doc_widgets.append(
            {
                "row": row,
                "card": card,
                "content": content,
                "title": title,
                "meta": list(meta or []),
                "base_height": base_height,
                "height_updaters": list(height_updaters or []),
            }
        )

    def _collect_meta_lines(self, doc: dict) -> Sequence[str]:
        """Return only expiry-related meta info."""
        expiry_value = (
            doc.get("expiry")
            or doc.get("expires_at")
            or doc.get("expiration_date")
        )
        expiry_label = "Expiră"

        meta = doc.get("meta") or doc.get("details") or doc.get("metadata")

        if not expiry_value and isinstance(meta, dict):
            for key, value in meta.items():
                if "expir" in key.lower():
                    expiry_value = value
                    expiry_label = key
                    break

        if not expiry_value and isinstance(meta, (list, tuple)):
            for item in meta:
                item_str = str(item)
                if "expir" in item_str.lower():
                    return [item_str]

        if not expiry_value and isinstance(meta, str):
            if "expir" in meta.lower():
                return [meta]

        if expiry_value:
            return [f"{expiry_label}: {expiry_value}"]

        return []

    def _bind_dynamic_height(self, label: Label, padding_dp: int):
        def _update_height(*_):
            if getattr(label, "_auto_height_lock", False):
                return
            label._auto_height_lock = True
            try:
                if label.texture is None:
                    label.texture_update()
                label.height = label.texture_size[1] + self._scale_dp(padding_dp)
            finally:
                label._auto_height_lock = False

        label.bind(texture_size=_update_height)
        _update_height()
        return _update_height

    # ------------------------------------------------------------------
    # Scaling helpers
    # ------------------------------------------------------------------
    def _apply_scale(self) -> None:
        base_padding = [self._scale_dp(v) for v in self.ROOT_PADDING]
        if hasattr(self, "_safe_top_padding"):
            base_padding[1] = self._safe_top_padding(self.ROOT_PADDING[1])
            base_padding[3] = self._safe_bottom_padding(self.ROOT_PADDING[3])
        self.root_layout.padding = base_padding
        self.root_layout.spacing = self._scale_dp(self.ROOT_SPACING)

        self.title_label.font_size = self._scale_sp(self.TITLE_FONT)
        self.subtitle_label.font_size = self._scale_sp(self.SUBTITLE_FONT)
        self.title_label.text = f"[b][color={self.TITLE_COLOR}]{self._title_text}[/color][/b]"
        self.subtitle_label.text = self._subtitle_text

        safe_bottom = getattr(self, "_safe_bottom_padding", lambda *_: dp(0))(24)
        bottom_padding = self._scale_dp(self.CARDS_SPACING * 2) + safe_bottom
        self.cards_container.spacing = self._scale_dp(self.CARDS_SPACING)
        self.cards_container.padding = [0, self._scale_dp(6), 0, bottom_padding]

        self.empty_state_anchor.height = self._scale_dp(self.EMPTY_HEIGHT)
        self.empty_state_label.font_size = self._scale_sp(self.SUBTITLE_FONT)
        self.empty_state_label.text = self._empty_text

        self.bottom_spacer.height = self._scale_dp(24)

        for entry in self._doc_widgets:
            card = entry["card"]
            base_height = entry["base_height"]
            card.height = self._scale_dp(base_height)
            card.width = self._compute_card_width()

            entry["row"].padding = [0, self._scale_dp(4), 0, self._scale_dp(4)]
            entry["row"].height = card.height + self._scale_dp(8)

            content = entry["content"]
            content.padding = [
                self._scale_dp(self.CARD_PADDING[0]),
                self._scale_dp(self.CARD_PADDING[1]),
                self._scale_dp(self.CARD_PADDING[0]),
                self._scale_dp(self.CARD_PADDING[1]),
            ]
            content.spacing = self._scale_dp(8)

            title_label = entry["title"]
            if title_label:
                if hasattr(title_label, "max_font_size"):
                    title_label.max_font_size = self._scale_sp(self.TITLE_CARD_FONT)
                if hasattr(title_label, "padding_dp"):
                    title_label.padding_dp = self._scale_dp(4)
                update_fn = getattr(title_label, "_update_font_size", None)
                if callable(update_fn):
                    update_fn()

            for meta_label in entry["meta"]:
                meta_label.font_size = self._scale_sp(self.META_FONT)

            for updater in entry["height_updaters"]:
                updater()

    def _compute_card_width(self) -> float:
        return self._clamp(Window.width * 0.88, self._scale_dp(260), self._scale_dp(580))

    def _scale_dp(self, value: float) -> float:
        return dp(value * self.scale_ratio)

    def _scale_sp(self, value: float) -> float:
        return sp(value * self.scale_ratio)

    def _compute_scale(self) -> float:
        width_ratio = Window.width / self.BASE_WIDTH
        height_ratio = Window.height / self.BASE_HEIGHT
        scale = min(width_ratio, height_ratio)
        return max(self.MIN_SCALE, min(self.MAX_SCALE, scale))

    def _on_window_resize(self, *_):
        self.scale_ratio = self._compute_scale()
        self._apply_scale()


__all__ = ["DocumentListMixin"]
