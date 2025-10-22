from __future__ import annotations

from pathlib import Path
import os
import threading
from datetime import datetime

from kivy.app import App
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.utils import platform
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import PushMatrix, PopMatrix, Rotate, Color, Line
from kivy.clock import Clock

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

from kivy_garden.xcamera.xcamera import XCamera
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

        filename = self._build_filename()

        width, height = texture.size
        pixel_data = bytes(texture.pixels)

        def _save():
            try:
                os.makedirs(os.path.dirname(filename), exist_ok=True)

                try:
                    from PIL import Image  # local import to avoid mandatory dependency at import time

                    image = Image.frombytes("RGBA", (width, height), pixel_data)
                    image = image.transpose(Image.FLIP_TOP_BOTTOM)
                    image = image.transpose(Image.ROTATE_90)
                    image.save(filename, format="PNG")
                except ImportError:
                    texture = self.texture
                    if texture is None:
                        raise RuntimeError("Texture unavailable for fallback save.")
                    texture.save(filename, flipped=False)

                play_shutter()
                success = True
            except Exception as exc:  # noqa: BLE001
                Logger.warning(f"SafeXCamera: Failed to save capture ({exc})")
                success = False

            def _notify(*_):
                self.play = previous_play_state
                if success:
                    Logger.info(f"SafeXCamera: Saved capture to {filename}")
                    self.dispatch("on_picture_taken", filename)

            Clock.schedule_once(_notify, 0)

        threading.Thread(target=_save, daemon=True).start()

    def _build_filename(self) -> str:
        directory = self.directory or os.path.join(str(Path.home()), "SmartIDWallet", "captures")
        os.makedirs(directory, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join(directory, f"{timestamp}.png")


class DocumentFrameOverlay(Widget):
    """Guide rectangle overlay to help users align their documents."""

    FRAME_WIDTH_RATIO = 0.86
    FRAME_HEIGHT_RATIO = 0.68
    CORNER_RATIO = 0.12
    LINE_WIDTH_DP = 2.0

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint", (1, 1))
        super().__init__(**kwargs)

        line_width = dp(self.LINE_WIDTH_DP)

        with self.canvas:
            Color(1, 1, 1, 0.22)
            self._outline = Line(rectangle=(0, 0, 0, 0), width=line_width)
            Color(1, 1, 1, 0.32)
            self._corner_lines = [
                Line(points=[0, 0, 0, 0], width=line_width) for _ in range(8)
            ]

        self.bind(size=self._update_frame, pos=self._update_frame)
        Clock.schedule_once(lambda *_: self._update_frame())

    def _update_frame(self, *_):
        width = self.width
        height = self.height
        if width <= 0 or height <= 0:
            return

        frame_w = width * self.FRAME_WIDTH_RATIO
        frame_h = height * self.FRAME_HEIGHT_RATIO
        frame_x = self.x + (width - frame_w) / 2
        frame_y = self.y + (height - frame_h) / 2

        corner_len = min(frame_w, frame_h) * self.CORNER_RATIO

        self._outline.rectangle = (frame_x, frame_y, frame_w, frame_h)

        bl_h, bl_v = self._corner_lines[0:2]
        br_h, br_v = self._corner_lines[2:4]
        tl_h, tl_v = self._corner_lines[4:6]
        tr_h, tr_v = self._corner_lines[6:8]

        bl_h.points = [frame_x, frame_y, frame_x + corner_len, frame_y]
        bl_v.points = [frame_x, frame_y, frame_x, frame_y + corner_len]

        br_h.points = [
            frame_x + frame_w - corner_len,
            frame_y,
            frame_x + frame_w,
            frame_y,
        ]
        br_v.points = [
            frame_x + frame_w,
            frame_y,
            frame_x + frame_w,
            frame_y + corner_len,
        ]

        tl_h.points = [
            frame_x,
            frame_y + frame_h,
            frame_x + corner_len,
            frame_y + frame_h,
        ]
        tl_v.points = [
            frame_x,
            frame_y + frame_h - corner_len,
            frame_x,
            frame_y + frame_h,
        ]

        tr_h.points = [
            frame_x + frame_w - corner_len,
            frame_y + frame_h,
            frame_x + frame_w,
            frame_y + frame_h,
        ]
        tr_v.points = [
            frame_x + frame_w,
            frame_y + frame_h - corner_len,
            frame_x + frame_w,
            frame_y + frame_h,
        ]


class CameraScanScreen(MDScreen, Alignment):
    """Minimal camera capture screen powered by Kivy Garden XCamera."""

    def __init__(self, server=None, **kwargs):
        super().__init__(name="camera_scan", **kwargs)
        self.server = server
        self.camera_view: XCamera | None = None
        self.camera_holder: FloatLayout | None = None
        self._camera_error = False
        self._capture_dir = self._build_capture_dir()
        self._awaiting_permission = False
        self.status_label: MDLabel | None = None
        self.frame_overlay: DocumentFrameOverlay | None = None

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

        self.camera_holder = FloatLayout()
        root.add_widget(self.camera_holder)
        self._init_camera_widget()

        self.status_label = MDLabel(
            text="",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.75),
            halign="center",
            size_hint_y=None,
        )
        self.status_label.bind(texture_size=lambda *_: self._update_status_height())
        root.add_widget(self.status_label)
        Clock.schedule_once(lambda *_: self._update_status_height())
        self._set_status(f"Capturile vor fi salvate în:\n{self._capture_dir}")

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
                    self._set_status("Se solicită permisiunea camerei...")
                    request_permissions([Permission.CAMERA], self._on_permission_result)
                return
        self._awaiting_permission = False
        self._set_status("Se inițializează camera...")
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
                self._set_status("Camera pregătită.")
        else:
            Logger.warning("CameraScanScreen: Camera permission denied by user.")
            self._set_status("Permisiunea camerei a fost respinsă.")

    def _on_picture_taken(self, _instance, filename: str) -> None:
        Logger.info(f"CameraScanScreen: Captured image saved at {filename}")
        self._set_status(f"Imagine salvată în:\n{filename}")

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
            self._set_status("Camera indisponibilă pe acest dispozitiv.")
            return

        self.camera_view = camera
        self.camera_view.bind(on_picture_taken=self._on_picture_taken)
        self.camera_view.bind(on_camera_ready=lambda *_: self._on_camera_ready())
        self._apply_camera_rotation(self.camera_view)
        self.camera_holder.add_widget(self.camera_view)
        self._attach_overlay()
        self._set_status(f"Capturile vor fi salvate în:\n{self._capture_dir}")

    def _on_camera_ready(self) -> None:
        if self.camera_view and not self._camera_error:
            self.camera_view.play = True

    def _apply_camera_rotation(self, camera: XCamera) -> None:
        if hasattr(camera, "_rotation_instruction"):
            return
        with camera.canvas.before:
            PushMatrix()
            camera._rotation_instruction = Rotate(angle=90, axis=(0, 0, 1), origin=camera.center)
        with camera.canvas.after:
            PopMatrix()
        camera.bind(pos=self._sync_camera_rotation_origin, size=self._sync_camera_rotation_origin)
        self._sync_camera_rotation_origin(camera)

    @staticmethod
    def _sync_camera_rotation_origin(camera: XCamera, *_):
        rotate = getattr(camera, "_rotation_instruction", None)
        if rotate:
            rotate.origin = camera.center

    def _attach_overlay(self) -> None:
        if not self.camera_holder:
            return
        if self.frame_overlay is None:
            self.frame_overlay = DocumentFrameOverlay()
        if self.frame_overlay.parent is not self.camera_holder:
            self.camera_holder.add_widget(self.frame_overlay)

    def _set_status(self, message: str) -> None:
        if not self.status_label:
            return
        self.status_label.text = message or ""
        self._update_status_height()

    def _update_status_height(self, *_):
        if not self.status_label:
            return
        label = self.status_label
        text = label.text.strip()
        if not text:
            label.height = 0
            label.opacity = 0
            return
        label.texture_update()
        label.height = label.texture_size[1] + dp(12)
        label.opacity = 1.0

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
