from __future__ import annotations

from pathlib import Path

from kivy.app import App
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.utils import platform

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

from kivy_garden.xcamera.xcamera import XCamera

from frontend.screens.widgets.custom_alignment import Alignment

try:  # pragma: no cover - Android specific imports
    if platform == "android":
        from android.permissions import (  # type: ignore
            Permission,
            check_permission,
            request_permissions,
        )
    else:  # pragma: no cover
        Permission = None
        check_permission = None
        request_permissions = None
except ImportError:  # pragma: no cover
    Permission = None
    check_permission = None
    request_permissions = None


class CameraScanScreen(MDScreen, Alignment):
    """Minimal camera view that requests runtime permissions when needed."""

    def __init__(self, server=None, **kwargs):
        super().__init__(name="camera_scan", **kwargs)
        self.server = server
        self.camera_view: XCamera | None = None
        self.camera_holder: MDBoxLayout | None = None
        self._awaiting_permission = False

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        padding = [
            dp(12),
            self._safe_top_padding(12),
            dp(12),
            self._safe_bottom_padding(12),
        ]

        root = MDBoxLayout(
            orientation="vertical",
            padding=padding,
            spacing=dp(12),
        )
        self.add_widget(root)

        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
        )
        back_btn = MDIconButton(
            icon="arrow-left",
            theme_icon_color="Custom",
            icon_color=(1, 1, 1, 0.92),
            on_release=lambda *_: self._go_back(),
        )
        header.add_widget(back_btn)
        header.add_widget(MDLabel())
        root.add_widget(header)

        self.camera_holder = MDBoxLayout()
        root.add_widget(self.camera_holder)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self._ensure_camera_ready()
        if self.camera_view:
            self.camera_view.play = True

    def on_leave(self, *args):
        super().on_leave(*args)
        if self.camera_view:
            self.camera_view.play = False

    # ------------------------------------------------------------------
    # Permissions + camera setup
    # ------------------------------------------------------------------
    def _ensure_camera_ready(self) -> None:
        if platform == "android" and Permission and request_permissions and check_permission:
            if not check_permission(Permission.CAMERA):
                if not self._awaiting_permission:
                    self._awaiting_permission = True
                    request_permissions([Permission.CAMERA], self._on_permission_result)
                return

        self._awaiting_permission = False
        self._init_camera_widget()

    def _on_permission_result(self, permissions, grants):
        if not permissions:
            return
        granted = all(grants)
        if granted:
            self._awaiting_permission = False
            self._init_camera_widget()
            if self.camera_view:
                self.camera_view.play = True
        else:
            Logger.warning("CameraScanScreen: Camera permission denied by user.")

    def _init_camera_widget(self) -> None:
        if not self.camera_holder or self.camera_view:
            return

        capture_dir = self._build_capture_dir()
        camera = XCamera(
            play=False,
            directory=str(capture_dir),
        )

        self.camera_view = camera
        self.camera_holder.add_widget(self.camera_view)

    # ------------------------------------------------------------------
    # Navigation & filesystem helpers
    # ------------------------------------------------------------------
    def _build_capture_dir(self) -> Path:
        app = App.get_running_app()
        if app and hasattr(app, "user_data_dir"):
            base = Path(app.user_data_dir)
        else:
            base = Path.home() / "SmartIDWallet"
        target = base / "captures"
        target.mkdir(parents=True, exist_ok=True)
        return target

    def _go_back(self) -> None:
        manager = getattr(self, "manager", None)
        if not manager:
            return
        if manager.has_screen("home"):
            transition = getattr(manager, "transition", None)
            previous = getattr(transition, "direction", None)
            if transition:
                transition.direction = "down"
            manager.current = "home"
            if transition and previous:
                transition.direction = previous
        else:
            manager.current = manager.previous()


__all__ = ["CameraScanScreen"]
