from __future__ import annotations

from pathlib import Path

from kivy.app import App
from kivy.logger import Logger
from kivy.utils import platform
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.uix.floatlayout import FloatLayout

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
        self.camera_holder: FloatLayout | None = None
        self._awaiting_permission = False

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        root = FloatLayout()
        self.add_widget(root)

        self.camera_holder = FloatLayout(size_hint=(1, 1))
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
        camera.size_hint = (1, 1)
        if hasattr(camera, "allow_stretch"):
            camera.allow_stretch = True
        if hasattr(camera, "keep_ratio"):
            camera.keep_ratio = False

        self.camera_view = camera
        self._apply_camera_rotation(self.camera_view)
        self.camera_holder.add_widget(self.camera_view)

    def _apply_camera_rotation(self, camera: XCamera) -> None:
        if hasattr(camera, "_rotation_instruction"):
            return
        with camera.canvas.before:
            PushMatrix()
            camera._rotation_instruction = Rotate(angle=-90, axis=(0, 0, 1), origin=camera.center)
        with camera.canvas.after:
            PopMatrix()
        camera.bind(pos=self._sync_camera_rotation_origin, size=self._sync_camera_rotation_origin)
        self._sync_camera_rotation_origin(camera)

    @staticmethod
    def _sync_camera_rotation_origin(camera: XCamera, *_):
        rotate = getattr(camera, "_rotation_instruction", None)
        if rotate:
            rotate.origin = camera.center

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


__all__ = ["CameraScanScreen"]
