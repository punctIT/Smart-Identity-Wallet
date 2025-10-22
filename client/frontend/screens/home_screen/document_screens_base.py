from __future__ import annotations

from typing import Iterable, List, Sequence

from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView

from frontend.screens.widgets.custom_alignment import Alignment

# ---------------------------------------------------------------------------
# Shared theme values
# ---------------------------------------------------------------------------
BG_BOTTOM = (0.03, 0.05, 0.09, 1)
CARD_BG = (0.13, 0.15, 0.20, 1)
CARD_STROKE = (1, 1, 1, 0.08)

TEXT_PRIMARY = (0.92, 0.95, 1.00, 1)
TEXT_SECONDARY = (0.70, 0.76, 0.86, 1)
ACCENT = (0.25, 0.60, 1.00, 1)


class DocumentCardTemplate(MDCard):
    """Reusable card layout for wallet documents."""

    BASE_PADDING = 18
    BASE_SPACING = 8
    BASE_RADIUS = 20

    TITLE_SP = 22
    SUBTITLE_SP = 16
    META_SP = 15

    COMPACT_THRESHOLD = 0.96
    COMPACT_MIN_RATIO = 0.78
    COMPACT_PADDING_FACTOR = 0.78
    COMPACT_SPACING_FACTOR = 0.82
    COMPACT_RADIUS_FACTOR = 0.85
    COMPACT_FONT_FACTOR = 0.88

    def __init__(self, title: str, subtitle: str, meta_lines: Sequence[str], **kwargs):
        super().__init__(**kwargs)
        self.title_text = title
        self.subtitle_text = subtitle
        self.meta_lines = list(meta_lines)

        self.orientation = "vertical"
        self.size_hint = (1, None)
        self.ripple_behavior = False
        self.shadow_softness = 12
        self.shadow_offset = (0, -3)
        self.md_bg_color = CARD_BG
        self.line_color = CARD_STROKE

        self._registered_labels: List[tuple[MDLabel, float, float]] = []
        self._scale_dp_fn = lambda value: dp(value)
        self._scale_sp_fn = lambda value: sp(value)
        self._compact_strength = 0.0
        self._padding_factor = 1.0
        self._spacing_factor = 1.0
        self._radius_factor = 1.0
        self._font_factor = 1.0
        self._label_padding_factor = 1.0

        self._content_box = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            adaptive_height=True,
            spacing=self._scale_dp_fn(self.BASE_SPACING),
        )
        self._content_box.bind(minimum_height=self._content_box.setter("height"))
        self._content_box.bind(width=self._sync_label_widths)
        self._content_box.bind(height=lambda *_: self._update_card_height())

        self.add_widget(self._content_box)
        self._build_content()

    def _build_content(self) -> None:
        self._title_label = self._create_label(
            text=f"[b]{self.title_text}[/b]",
            markup=True,
            base_sp=self.TITLE_SP,
            padding_dp=4,
            text_color=TEXT_PRIMARY,
        )

        if self.subtitle_text:
            self._subtitle_label = self._create_label(
                text=self.subtitle_text,
                base_sp=self.SUBTITLE_SP,
                padding_dp=4,
                text_color=TEXT_SECONDARY,
            )
        else:
            self._subtitle_label = None

        self._meta_labels = []
        for line in self.meta_lines:
            lbl = self._create_label(
                text=line,
                base_sp=self.META_SP,
                padding_dp=2,
                text_color=TEXT_SECONDARY,
            )
            self._meta_labels.append(lbl)

    def _create_label(
        self,
        *,
        text: str,
        base_sp: float,
        padding_dp: float,
        text_color,
        markup: bool = False,
    ) -> MDLabel:
        label = MDLabel(
            text=text,
            markup=markup,
            theme_text_color="Custom",
            text_color=text_color,
            size_hint=(1, None),
            halign="left",
            valign="middle",
        )
        label.bind(texture_size=lambda *_: self._update_label_height(label, padding_dp))
        self._content_box.add_widget(label)
        self._registered_labels.append((label, base_sp, padding_dp))
        return label

    def _sync_label_widths(self, _box, width: float) -> None:
        for label, *_ in self._registered_labels:
            label.text_size = (width, None)

    def _update_label_height(self, label: MDLabel, padding_dp: float) -> None:
        if label.texture is None:
            label.texture_update()
        padding_px = self._scale_dp_fn(padding_dp * self._label_padding_factor)
        label.height = label.texture_size[1] + padding_px
        self._update_card_height()

    def _update_card_height(self) -> None:
        padding_y = sum(self.padding[1::2]) if isinstance(self.padding, (list, tuple)) else 0
        self.height = self._content_box.height + padding_y

    @staticmethod
    def _lerp(start: float, end: float, amount: float) -> float:
        return start + (end - start) * amount

    def _compute_compact_strength(self, scale_ratio: float) -> float:
        if scale_ratio >= self.COMPACT_THRESHOLD:
            return 0.0
        denom = self.COMPACT_THRESHOLD - self.COMPACT_MIN_RATIO
        if denom <= 0:
            return 1.0
        strength = (self.COMPACT_THRESHOLD - scale_ratio) / denom
        return max(0.0, min(1.0, strength))

    def apply_scale(self, scale_dp, scale_sp, scale_ratio=1.0) -> None:
        self._scale_dp_fn = scale_dp
        self._scale_sp_fn = scale_sp
        self._compact_strength = self._compute_compact_strength(scale_ratio)
        self._padding_factor = self._lerp(1.0, self.COMPACT_PADDING_FACTOR, self._compact_strength)
        self._spacing_factor = self._lerp(1.0, self.COMPACT_SPACING_FACTOR, self._compact_strength)
        self._radius_factor = self._lerp(1.0, self.COMPACT_RADIUS_FACTOR, self._compact_strength)
        self._font_factor = self._lerp(1.0, self.COMPACT_FONT_FACTOR, self._compact_strength)
        self._label_padding_factor = self._padding_factor

        padding = scale_dp(self.BASE_PADDING * self._padding_factor)
        spacing = scale_dp(self.BASE_SPACING * self._spacing_factor)
        radius = scale_dp(self.BASE_RADIUS * self._radius_factor)

        self.padding = (padding, padding, padding, padding)
        self._content_box.spacing = spacing
        self.radius = [radius] * 4

        for label, base_sp, padding_dp in self._registered_labels:
            label.font_size = scale_sp(base_sp * self._font_factor)
            self._update_label_height(label, padding_dp)

        self._update_card_height()


class AddDocumentCardTemplate(MDCard):
    """Prominent card inviting the user to add a new document."""

    BASE_PADDING = 18
    BASE_SPACING = 10
    BASE_RADIUS = 20
    ICON_SP = 44
    CAPTION_SP = 16
    COMPACT_THRESHOLD = 0.96
    COMPACT_MIN_RATIO = 0.78
    COMPACT_PADDING_FACTOR = 0.78
    COMPACT_SPACING_FACTOR = 0.82
    COMPACT_RADIUS_FACTOR = 0.85
    COMPACT_ICON_FACTOR = 0.82
    COMPACT_CAPTION_FACTOR = 0.9

    def __init__(self, caption: str, on_request_add, **kwargs):
        super().__init__(**kwargs)
        self.caption = caption
        self.on_request_add = on_request_add

        self.orientation = "vertical"
        self.size_hint = (1, None)
        self.ripple_behavior = True
        self.shadow_softness = 14
        self.shadow_offset = (0, -3)
        self.md_bg_color = CARD_BG
        self.line_color = CARD_STROKE
        self._scale_dp_fn = lambda value: dp(value)
        self._scale_sp_fn = lambda value: sp(value)
        self._compact_strength = 0.0
        self._padding_factor = 1.0
        self._spacing_factor = 1.0
        self._radius_factor = 1.0
        self._icon_factor = 1.0
        self._caption_factor = 1.0
        self._icon_padding_factor = 1.0
        self._caption_padding_factor = 1.0

        self._content_box = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            adaptive_height=True,
            spacing=self._scale_dp_fn(self.BASE_SPACING),
        )
        self._content_box.bind(minimum_height=self._content_box.setter("height"))
        self._content_box.bind(width=self._sync_label_width)
        self._content_box.bind(height=lambda *_: self._update_card_height())
        self.add_widget(self._content_box)

        self._icon_label = MDLabel(
            text="+",
            theme_text_color="Custom",
            text_color=ACCENT,
            halign="center",
            valign="middle",
            size_hint=(1, None),
        )
        self._icon_label.bind(texture_size=lambda *_: self._update_icon_height())
        self._content_box.add_widget(self._icon_label)

        self._caption_label = MDLabel(
            text=self.caption,
            theme_text_color="Custom",
            text_color=TEXT_SECONDARY,
            halign="center",
            valign="middle",
            size_hint=(1, None),
        )
        self._caption_label.bind(texture_size=lambda *_: self._update_caption_height())
        self._content_box.add_widget(self._caption_label)

        self.bind(on_release=lambda *_: self._handle_request())

    def _sync_label_width(self, _box, width: float) -> None:
        self._icon_label.text_size = (width, None)
        self._caption_label.text_size = (width, None)

    def _update_icon_height(self) -> None:
        if self._icon_label.texture is None:
            self._icon_label.texture_update()
        extra = self._scale_dp_fn(12 * self._icon_padding_factor)
        self._icon_label.height = self._icon_label.texture_size[1] + extra
        self._update_card_height()

    def _update_caption_height(self) -> None:
        if self._caption_label.texture is None:
            self._caption_label.texture_update()
        extra = self._scale_dp_fn(8 * self._caption_padding_factor)
        self._caption_label.height = self._caption_label.texture_size[1] + extra
        self._update_card_height()

    def _update_card_height(self) -> None:
        padding_y = sum(self.padding[1::2]) if isinstance(self.padding, (list, tuple)) else 0
        self.height = self._content_box.height + padding_y

    def _handle_request(self) -> None:
        if callable(self.on_request_add):
            self.on_request_add()

    @staticmethod
    def _lerp(start: float, end: float, amount: float) -> float:
        return start + (end - start) * amount

    def _compute_compact_strength(self, scale_ratio: float) -> float:
        if scale_ratio >= self.COMPACT_THRESHOLD:
            return 0.0
        denom = self.COMPACT_THRESHOLD - self.COMPACT_MIN_RATIO
        if denom <= 0:
            return 1.0
        strength = (self.COMPACT_THRESHOLD - scale_ratio) / denom
        return max(0.0, min(1.0, strength))

    def apply_scale(self, scale_dp, scale_sp, scale_ratio=1.0) -> None:
        self._scale_dp_fn = scale_dp
        self._scale_sp_fn = scale_sp
        self._compact_strength = self._compute_compact_strength(scale_ratio)
        self._padding_factor = self._lerp(1.0, self.COMPACT_PADDING_FACTOR, self._compact_strength)
        self._spacing_factor = self._lerp(1.0, self.COMPACT_SPACING_FACTOR, self._compact_strength)
        self._radius_factor = self._lerp(1.0, self.COMPACT_RADIUS_FACTOR, self._compact_strength)
        self._icon_factor = self._lerp(1.0, self.COMPACT_ICON_FACTOR, self._compact_strength)
        self._caption_factor = self._lerp(1.0, self.COMPACT_CAPTION_FACTOR, self._compact_strength)
        self._icon_padding_factor = self._padding_factor
        self._caption_padding_factor = self._padding_factor

        padding = scale_dp(self.BASE_PADDING * self._padding_factor)
        spacing = scale_dp(self.BASE_SPACING * self._spacing_factor)
        radius = scale_dp(self.BASE_RADIUS * self._radius_factor)

        self.padding = (padding, padding, padding, padding)
        self._content_box.spacing = spacing
        self.radius = [radius] * 4

        self._icon_label.font_size = scale_sp(self.ICON_SP * self._icon_factor)
        self._caption_label.font_size = scale_sp(self.CAPTION_SP * self._caption_factor)

        self._update_icon_height()
        self._update_caption_height()


class BaseDocumentsScreen(MDScreen, Alignment):
    """Base implementation for document-category screens using KivyMD widgets."""

    BASE_WIDTH = 412
    BASE_HEIGHT = 915
    MIN_SCALE = 0.78
    MAX_SCALE = 1.55

    ROOT_PADDING = (16, 12, 16, 16)
    ROOT_SPACING = 16
    CARD_SPACING = 14

    TITLE_SP = 30
    SUBTITLE_SP = 17

    screen_name: str = ""
    title_text: str = "Documente"
    subtitle_text: str = ""
    empty_text: str = "Nu există documente disponibile momentan."
    add_card_caption: str = "Adaugă document"

    add_target_screen: str = "camera_scan"
    add_transition_direction: str = "up"

    document_request_type: str = "GetWalletCards"
    document_data_keys: Sequence[str] = ("cards", "documents")
    document_mock_attr: str = "_MOCK_WALLET_CARDS"
    document_category_field: str = "category"
    document_categories: Sequence[str] | None = None
    require_category_match: bool = False

    def __init__(self, server=None, **kwargs):
        if not self.screen_name:
            raise ValueError("BaseDocumentsScreen subclasses must define `screen_name`.")

        super().__init__(name=self.screen_name, **kwargs)
        self.server = server

        self.scale_ratio = self._compute_scale()
        self.documents: List[dict] = []
        self._card_rows: List[AnchorLayout] = []

        Window.bind(size=self._on_window_resize)

        self._build_ui()
        self._apply_scale()
        self._load_documents()

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #
    def _build_ui(self) -> None:
        self.md_bg_color = BG_BOTTOM

        padding = [self._scale_dp(v) for v in self.ROOT_PADDING]
        padding[1] = self._safe_top_padding(self.ROOT_PADDING[1])
        padding[3] = self._safe_bottom_padding(self.ROOT_PADDING[3])

        self.root_layout = MDBoxLayout(
            orientation="vertical",
            spacing=self._scale_dp(self.ROOT_SPACING),
            padding=padding,
        )
        self.add_widget(self.root_layout)

        self.header_box = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            adaptive_height=True,
            spacing=self._scale_dp(4),
        )
        self.header_box.bind(minimum_height=self.header_box.setter("height"))
        self.header_box.bind(width=lambda _, width: self._sync_header_width(width))
        self.root_layout.add_widget(self.header_box)

        self.title_label = MDLabel(
            text=self.title_text,
            theme_text_color="Custom",
            text_color=ACCENT,
            halign="left",
            size_hint=(1, None),
        )
        self.title_label.bind(texture_size=lambda *_: self._update_label_height(self.title_label, 6))
        self.header_box.add_widget(self.title_label)

        self.subtitle_label = MDLabel(
            text=self.subtitle_text,
            theme_text_color="Custom",
            text_color=TEXT_SECONDARY,
            halign="left",
            size_hint=(1, None),
        )
        self.subtitle_label.bind(texture_size=lambda *_: self._update_label_height(self.subtitle_label, 6))
        self.header_box.add_widget(self.subtitle_label)

        self.scroll_view = MDScrollView()
        self.root_layout.add_widget(self.scroll_view)

        bottom_padding = self._scale_dp(self.CARD_SPACING * 2) + self._safe_bottom_padding(24)
        self.cards_container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            adaptive_height=True,
            padding=(0, self._scale_dp(6), 0, bottom_padding),
            spacing=self._scale_dp(self.CARD_SPACING),
        )
        self.cards_container.bind(minimum_height=self.cards_container.setter("height"))
        self.cards_container.bind(width=lambda _, width: self._sync_empty_width(width))
        self.scroll_view.add_widget(self.cards_container)

        self.empty_state = MDLabel(
            text=self.empty_text,
            theme_text_color="Custom",
            text_color=TEXT_SECONDARY,
            halign="center",
            size_hint=(1, None),
        )
        self.empty_state.bind(texture_size=lambda *_: self._update_empty_state_height())
        self.empty_holder = AnchorLayout(size_hint=(1, None))
        self.empty_holder.add_widget(self.empty_state)

        self.bottom_spacer = Widget(size_hint_y=None)

    def _sync_header_width(self, width: float) -> None:
        self.title_label.text_size = (width, None)
        self.subtitle_label.text_size = (width, None)

    def _sync_empty_width(self, width: float) -> None:
        self.empty_state.text_size = (width * 0.9, None)

    def _update_label_height(self, label: MDLabel, padding_dp: float) -> None:
        if label.texture is None:
            label.texture_update()
        label.height = label.texture_size[1] + self._scale_dp(padding_dp)

    def _update_empty_state_height(self) -> None:
        if self.empty_state.texture is None:
            self.empty_state.texture_update()
        self.empty_state.height = self.empty_state.texture_size[1] + self._scale_dp(24)
        self.empty_holder.height = self.empty_state.height + self._scale_dp(16)

    # ------------------------------------------------------------------ #
    # Document pipeline
    # ------------------------------------------------------------------ #
    def set_documents(self, documents: Iterable[dict]) -> None:
        self.documents = list(documents or [])
        self._refresh_cards()

    def append_document(self, document: dict) -> None:
        self.documents.append(document)
        self._refresh_cards()

    def _refresh_cards(self) -> None:
        self.cards_container.clear_widgets()
        self._card_rows.clear()

        if not self.documents:
            self.cards_container.add_widget(self.empty_holder)
            self.cards_container.add_widget(self._build_add_card())
            self.cards_container.add_widget(self.bottom_spacer)
            self._apply_scale()
            return

        for document in self.documents:
            card = self._build_document_card(document)
            self.cards_container.add_widget(card)

        self.cards_container.add_widget(self._build_add_card())
        self.cards_container.add_widget(self.bottom_spacer)
        self._apply_scale()

    def _build_document_card(self, document: dict) -> AnchorLayout:
        card = DocumentCardTemplate(
            title=self._extract_title(document),
            subtitle=self._extract_subtitle(document),
            meta_lines=self._extract_meta(document),
        )
        return self._wrap_row(card)

    def _build_add_card(self) -> AnchorLayout:
        card = AddDocumentCardTemplate(
            caption=self.add_card_caption,
            on_request_add=self._open_add_document_screen,
        )
        return self._wrap_row(card)

    def _wrap_row(self, card: MDCard) -> AnchorLayout:
        row = self.center_row(
            card,
            rel_width=0.92,
            min_w=self._scale_dp(260),
            max_w=self._scale_dp(560),
        )
        row.padding = [0, self._scale_dp(4), 0, self._scale_dp(4)]
        card.bind(
            height=lambda *_: setattr(row, "height", card.height + self._scale_dp(8))
        )
        self._card_rows.append(row)
        return row

    @staticmethod
    def _extract_title(document: dict) -> str:
        return (
            document.get("title")
            or document.get("name")
            or document.get("document_name")
            or "Document"
        )

    @staticmethod
    def _extract_subtitle(document: dict) -> str:
        return (
            document.get("subtitle")
            or document.get("description")
            or document.get("type")
            or ""
        )

    @staticmethod
    def _extract_meta(document: dict) -> Sequence[str]:
        meta = document.get("meta") or document.get("details") or document.get("metadata")
        if meta:
            if isinstance(meta, dict):
                return [f"{key}: {value}" for key, value in meta.items()]
            if isinstance(meta, (list, tuple)):
                return [str(item) for item in meta]
            return [str(meta)]

        lines = []
        status = document.get("status")
        number = document.get("number")
        expiry = document.get("expiry") or document.get("expires_at")

        if status:
            lines.append(f"Status: {status}")
        if number:
            lines.append(f"Număr: {number}")
        if expiry:
            lines.append(f"Expiră: {expiry}")
        return lines

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #
    def _open_add_document_screen(self) -> None:
        manager = getattr(self, "manager", None)
        if not manager:
            return
        target = self.add_target_screen
        if not target or not manager.has_screen(target):
            return
        transition = getattr(manager, "transition", None)
        previous_direction = getattr(transition, "direction", None)
        if transition and self.add_transition_direction:
            transition.direction = self.add_transition_direction
        manager.current = target
        if transition and previous_direction:
            transition.direction = previous_direction

    # ------------------------------------------------------------------ #
    # Scaling helpers
    # ------------------------------------------------------------------ #
    def _scale_dp(self, value: float) -> float:
        return dp(value * self.scale_ratio)

    def _scale_sp(self, value: float) -> float:
        return sp(value * self.scale_ratio)

    def _compute_scale(self) -> float:
        width_ratio = Window.width / self.BASE_WIDTH
        height_ratio = Window.height / self.BASE_HEIGHT
        scale = min(width_ratio, height_ratio)
        return max(self.MIN_SCALE, min(self.MAX_SCALE, scale))

    def _apply_scale(self) -> None:
        padding = [self._scale_dp(v) for v in self.ROOT_PADDING]
        padding[1] = self._safe_top_padding(self.ROOT_PADDING[1])
        padding[3] = self._safe_bottom_padding(self.ROOT_PADDING[3])
        self.root_layout.padding = padding
        self.root_layout.spacing = self._scale_dp(self.ROOT_SPACING)

        self.header_box.spacing = self._scale_dp(4)

        self.title_label.font_size = self._scale_sp(self.TITLE_SP)
        self.subtitle_label.font_size = self._scale_sp(self.SUBTITLE_SP)
        self._update_label_height(self.title_label, 6)
        self._update_label_height(self.subtitle_label, 6)

        bottom_padding = self._scale_dp(self.CARD_SPACING * 2) + self._safe_bottom_padding(24)
        self.cards_container.spacing = self._scale_dp(self.CARD_SPACING)
        self.cards_container.padding = (0, self._scale_dp(6), 0, bottom_padding)

        self.empty_state.font_size = self._scale_sp(self.SUBTITLE_SP)
        self._update_empty_state_height()

        self.bottom_spacer.height = self._scale_dp(32)
        if hasattr(self, "empty_holder"):
            self.empty_holder.height = self.empty_state.height + self._scale_dp(16)

        for row in self._card_rows:
            row.padding = [0, self._scale_dp(4), 0, self._scale_dp(4)]

        for row in self._card_rows:
            card = row.children[0]
            if hasattr(card, "apply_scale"):
                card.apply_scale(self._scale_dp, self._scale_sp, self.scale_ratio)

    def _on_window_resize(self, *_):
        self.scale_ratio = self._compute_scale()
        self._apply_scale()

    # ------------------------------------------------------------------ #
    # Backend integration
    # ------------------------------------------------------------------ #
    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self._load_documents()

    def _load_documents(self) -> None:
        documents = []
        if getattr(self, "server", None):
            try:
                response = self.server.get_specific_data(self.document_request_type)
            except Exception:
                response = None
            if response and response.get("success"):
                payload = response.get("data") or {}
                for key in self.document_data_keys:
                    cards = payload.get(key)
                    if cards:
                        if isinstance(cards, dict):
                            cards = list(cards.values())
                        if isinstance(cards, list):
                            documents = list(cards)
                            break
            if not documents and hasattr(self.server, self.document_mock_attr):
                mock_cards = getattr(self.server, self.document_mock_attr)
                documents = list(mock_cards)
        else:
            from server_requests.data_requester import DataRequester

            documents = list(getattr(DataRequester, self.document_mock_attr, []))

        filtered = self._filter_documents(documents)
        self.set_documents(filtered)

    def _filter_documents(self, documents: Sequence[dict]) -> List[dict]:
        """Subclass hook to filter documents per category."""
        docs = list(documents or [])
        categories = self.document_categories
        if not categories:
            return docs

        field = self.document_category_field
        normalized = {str(cat).lower() for cat in categories}
        filtered = []
        matched_any = False

        for doc in docs:
            value = doc.get(field)
            if value is None:
                continue
            matched_any = True
            if str(value).lower() in normalized:
                filtered.append(doc)

        if matched_any:
            return filtered
        return filtered if self.require_category_match else docs

    def set_server(self, server) -> None:
        self.server = server
        self._load_documents()


__all__ = [
    "ACCENT",
    "AddDocumentCardTemplate",
    "BaseDocumentsScreen",
    "BG_BOTTOM",
    "CARD_BG",
    "CARD_STROKE",
    "DocumentCardTemplate",
    "TEXT_PRIMARY",
    "TEXT_SECONDARY",
]
