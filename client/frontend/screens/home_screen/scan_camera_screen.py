from __future__ import annotations

from pathlib import Path
import os
import threading

from kivy.app import App
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.utils import platform
from kivy.uix.widget import Widget

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

from kivy_garden.xcamera.xcamera import XCamera, get_filename
from kivy_garden.xcamera.platform_api import play_shutter

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


class SafeXCamera(XCamera):
    """XCamera variant that safely captures frames without blocking the UI."""

    def shoot(self):  # noqa: D401
        if platform == "android":
            return super().shoot()

        previous_play_state = self.play
        self.play = False

        texture = self.texture
        if texture is None:
            Logger.warning("SafeXCamera: capture skipped, no texture available.")
            self.play = previous_play_state
            return

        filename = get_filename()
        if self.directory:
            filename = os.path.join(self.directory, filename)

        width, height = texture.size
        pixel_data = bytes(texture.pixels)

        def _save():
            try:
                try:
                    from PIL import Image  # local import to avoid mandatory dependency at import time

                    image = Image.frombytes("RGBA", (width, height), pixel_data)
                    image = image.transpose(Image.FLIP_TOP_BOTTOM)
                    image.save(filename, format="PNG")
                except ImportError:
                    texture = self.texture
                    if texture is None:
                        raise RuntimeError("Texture unavailable for fallback save.")
                    texture.save(filename, flipped=False)

                play_shutter()
                Logger.info(f"SafeXCamera: Saved capture to {filename}")
                success = True
            except Exception as exc:  # noqa: BLE001
                Logger.warning(f"SafeXCamera: Failed to save capture ({exc})")
                success = False

            from kivy.clock import Clock

            def _notify(*_):
                self.play = previous_play_state
                if success:
                    self.dispatch("on_picture_taken", filename)

            Clock.schedule_once(_notify, 0)

        threading.Thread(target=_save, daemon=True).start()


class CameraScanScreen(MDScreen, Alignment):
    """Minimal camera capture screen powered by Kivy Garden XCamera."""

    def __init__(self, server=None, **kwargs):
        super().__init__(name="camera_scan", **kwargs)
        self.server = server
        self.camera_view: XCamera | None = None
        self.camera_holder: MDBoxLayout | None = None
        self._camera_error = False
        self._capture_dir = self._build_capture_dir()
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
            padding=(0, 0),
        )
        back_btn = MDIconButton(
            icon="arrow-left",
            theme_icon_color="Custom",
            icon_color=(1, 1, 1, 0.92),
            on_release=lambda *_: self._go_back(),
        )
        header.add_widget(back_btn)
        header.add_widget(Widget())
        root.add_widget(header)

        self.camera_holder = MDBoxLayout()
        root.add_widget(self.camera_holder)
        self._init_camera_widget()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self._ensure_camera_ready()
        if self.camera_view and not self._camera_error:
            self.camera_view.play = True

    def on_leave(self, *args):
        super().on_leave(*args)
        if self.camera_view and not self._camera_error:
            self.camera_view.play = False

    # ------------------------------------------------------------------
    # Camera helpers
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
            if not self.camera_view:
                self._init_camera_widget()
            if self.camera_view and not self._camera_error:
                self.camera_view.play = True
        else:
            Logger.warning("CameraScanScreen: Camera permission denied by user.")

    def _on_picture_taken(self, _instance, filename: str) -> None:
        Logger.info(f"CameraScanScreen: Captured image saved at {filename}")

    def _init_camera_widget(self) -> None:
        if self.camera_view:
            return
        if not self.camera_holder:
            return
        self.camera_holder.clear_widgets()
        self._camera_error = False
        try:
            camera = SafeXCamera(
                play=False,
                directory=str(self._capture_dir),
            )
        except Exception as exc:  # noqa: BLE001
            Logger.warning(f"CameraScanScreen: Failed to initialise camera ({exc})")
            self._camera_error = True
            self.camera_view = None
            self.camera_holder.add_widget(
                MDLabel(
                    text="Camera indisponibilă pe acest dispozitiv.",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 0.7),
                )
            )
            return

        self.camera_view = camera
        self.camera_view.bind(on_picture_taken=self._on_picture_taken)
        self.camera_view.bind(on_camera_ready=lambda *_: self._on_camera_ready())
        self.camera_holder.add_widget(self.camera_view)

    def _on_camera_ready(self) -> None:
        if self.camera_view and not self._camera_error:
            self.camera_view.play = True

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
            prev_direction = getattr(transition, "direction", None)
            if transition:
                transition.direction = "down"
            manager.current = "home"
            if transition and prev_direction:
                transition.direction = prev_direction
        else:
            manager.current = manager.previous()


__all__ = ["CameraScanScreen"]
