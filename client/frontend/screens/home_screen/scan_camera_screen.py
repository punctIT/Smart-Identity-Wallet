from __future__ import annotations

from pathlib import Path

from kivy.app import App
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.utils import platform
from kivy.graphics import PushMatrix, PopMatrix, Rotate  # ✅ added for rotation

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
        from android.storage import primary_external_storage_path
        from jnius import autoclass

        # MediaScannerConnection helps refresh Gallery immediately
        MediaScannerConnection = autoclass('android.media.MediaScannerConnection')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
    else:
        Permission = None
        check_permission = None
        request_permissions = None
        primary_external_storage_path = None
        MediaScannerConnection = None
        PythonActivity = None
except ImportError:  # pragma: no cover
    Permission = None
    check_permission = None
    request_permissions = None
    primary_external_storage_path = None
    MediaScannerConnection = None
    PythonActivity = None


class CameraScanScreen(MDScreen, Alignment):
    """Camera screen that saves photos in a public folder and rotates the preview 90° left."""

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
            needed = [Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE]
            granted = all(check_permission(p) for p in needed)
            if not granted:
                if not self._awaiting_permission:
                    self._awaiting_permission = True
                    request_permissions(needed, self._on_permission_result)
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
            Logger.warning("CameraScanScreen: Camera or storage permission denied by user.")

    def _init_camera_widget(self) -> None:
        if not self.camera_holder or self.camera_view:
            return

        capture_dir = self._build_capture_dir()
        camera = XCamera(
            play=False,
            directory=str(capture_dir),
        )

        # ✅ Rotate camera view 90° left
        with camera.canvas.before:
            PushMatrix()
            self._rotation = Rotate(angle=-90, origin=camera.center)
        with camera.canvas.after:
            PopMatrix()

        # ✅ Keep rotation origin in sync with widget size/pos
        def _update_rotation_origin(*_):
            if hasattr(self, "_rotation"):
                self._rotation.origin = camera.center

        camera.bind(pos=_update_rotation_origin, size=_update_rotation_origin)

        # Hook into XCamera's on_picture_taken event to refresh Gallery
        def on_picture(instance, filepath):
            Logger.info(f"CameraScanScreen: Saved photo -> {filepath}")
            if platform == "android" and MediaScannerConnection:
                ctx = PythonActivity.mActivity
                MediaScannerConnection.scanFile(ctx, [filepath], None, None)

        camera.bind(on_picture_taken=on_picture)

        self.camera_view = camera
        self.camera_holder.add_widget(self.camera_view)

    # ------------------------------------------------------------------
    # Navigation & filesystem helpers
    # ------------------------------------------------------------------
    def _build_capture_dir(self) -> Path:
        """Save photos in a public folder on Android (visible in Gallery)."""
        try:
            if platform == "android" and primary_external_storage_path:
                base = Path(primary_external_storage_path()) / "SmartIDWallet"
            else:
                base = Path.home() / "SmartIDWallet"
        except Exception as e:
            Logger.warning(f"CameraScanScreen: Failed to get external path: {e}")
            base = Path.home() / "SmartIDWallet"

        target = base / "captures"
        target.mkdir(parents=True, exist_ok=True)
        Logger.info(f"CameraScanScreen: Capture directory = {target}")
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
