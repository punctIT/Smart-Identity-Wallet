from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse


class AddDocumentCardMixin:
    """Mixin that injects an add-document shortcut card into document lists."""

    add_card_icon = "+"
    add_card_caption = "Adaugă document"
    add_card_target_screen = "camera_scan"
    add_card_transition_direction = "up"

    def _get_additional_cards(self):
        card = self._build_add_document_card()
        return [card] if card else []

    def _build_add_document_card(self):
        base_height = self.CARD_MIN_HEIGHT
        card = self.make_card(
            self._compute_card_width(),
            base_height,
            radius=self.CARD_RADIUS,
            bg=(0.18, 0.21, 0.28, 1),
            stroke=(1, 1, 1, 0.08),
        )

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

        icon_wrapper = AnchorLayout(size_hint=(1, None))
        badge = AnchorLayout(size_hint=(None, None))
        with badge.canvas.before:
            Color(0.27, 0.46, 0.96, 1)
            badge._circle = Ellipse(pos=badge.pos, size=badge.size)
        badge.bind(
            pos=lambda *_: setattr(badge._circle, "pos", badge.pos),
            size=lambda *_: setattr(badge._circle, "size", badge.size),
        )
        icon_label = Label(
            text=self.add_card_icon,
            color=(0.96, 0.97, 1, 1),
            font_size=self._scale_sp(42),
            halign="center",
            valign="middle",
            size_hint=(1, 1),
        )
        icon_label.bind(size=lambda lbl, size: setattr(lbl, "text_size", size))
        badge.add_widget(icon_label)
        icon_wrapper.add_widget(badge)
        content.add_widget(icon_wrapper)

        caption_label = Label(
            text=self.add_card_caption,
            color=(0.70, 0.76, 0.86, 1),
            font_size=self._scale_sp(self.SUBTITLE_CARD_FONT),
            halign="center",
            valign="middle",
            size_hint=(1, None),
        )
        caption_label.bind(size=lambda lbl, size: setattr(lbl, "text_size", (size[0], None)))
        caption_height_updater = self._bind_dynamic_height(caption_label, padding_dp=6)

        def _update_fonts(*_):
            badge_size = self._scale_dp(66)
            badge.size = (badge_size, badge_size)
            icon_wrapper.height = badge_size + self._scale_dp(12)
            icon_label.font_size = self._scale_sp(42)
            caption_label.font_size = self._scale_sp(self.SUBTITLE_CARD_FONT)

        content.add_widget(caption_label)
        card.add_widget(content)

        overlay_btn = Button(
            background_normal="",
            background_color=(0, 0, 0, 0),
            size_hint=(1, 1),
        )
        overlay_btn.bind(on_release=self._open_add_document_screen)
        card.add_widget(overlay_btn)

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
            title=None,
            meta=[],
            base_height=base_height,
            height_updaters=[_update_fonts, caption_height_updater],
        )

        _update_fonts()
        return row

    def _open_add_document_screen(self, *_):
        if not getattr(self, "manager", None):
            return
        target = self.add_card_target_screen
        if not target or not self.manager.has_screen(target):
            return
        transition = getattr(self.manager, "transition", None)
        if transition and self.add_card_transition_direction:
            transition.direction = self.add_card_transition_direction
        self.manager.current = target


__all__ = ["AddDocumentCardMixin"]
