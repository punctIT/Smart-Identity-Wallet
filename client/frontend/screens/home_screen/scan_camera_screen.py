from __future__ import annotations

from pathlib import Path
from typing import Optional

from kivy.app import App
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.utils import platform
from kivy.graphics import PushMatrix, PopMatrix, Rotate  # ✅ added for rotation
from kivy.uix.label import Label

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
        from jnius import JavaException, autoclass

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
        JavaException = None
        autoclass = None
except ImportError:  # pragma: no cover
    Permission = None
    check_permission = None
    request_permissions = None
    primary_external_storage_path = None
    MediaScannerConnection = None
    PythonActivity = None
    JavaException = None
    autoclass = None


class CameraScanScreen(MDScreen, Alignment):
    """Camera screen that saves photos in a public folder and rotates the preview 90° left."""

    def __init__(self, server=None, **kwargs):
        super().__init__(name="camera_scan", **kwargs)
        self.server = server
        self.camera_view: XCamera | None = None
        self.camera_holder: MDBoxLayout | None = None
        self._camera_error_label: Optional[Label] = None
        self._awaiting_permission = False
        self._camera_index: Optional[int] = None

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
        camera_kwargs = {
            "play": False,
            "directory": str(capture_dir),
        }

        if platform == "android":
            index = self._select_primary_camera_index()
            if index is not None:
                self._camera_index = index
                camera_kwargs["index"] = index

        try:
            camera = XCamera(**camera_kwargs)
        except Exception as exc:  # noqa: BLE001
            Logger.error(f"CameraScanScreen: unable to initialise camera widget: {exc}")
            self._show_camera_error("Camera indisponibilă.\nVerifică permisiunile sau conectează o cameră.")
            return

        camera.size_hint = (1, 1)

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
        self._ensure_android_capture_backend()
        self.camera_holder.add_widget(self.camera_view)
        if self._camera_error_label and self._camera_error_label.parent:
            self._camera_error_label.parent.remove_widget(self._camera_error_label)
            self._camera_error_label = None

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

    def _select_primary_camera_index(self) -> Optional[int]:
        """Try to pick the primary (non-wide) rear camera on Android."""
        if platform != "android" or autoclass is None:
            return None

        try:
            AndroidCamera = autoclass("android.hardware.Camera")
            CameraInfo = autoclass("android.hardware.Camera$CameraInfo")
        except Exception as exc:  # noqa: BLE001
            Logger.warning(f"CameraScanScreen: unable to access camera info: {exc}")
            return None

        info = CameraInfo()
        cam_count = AndroidCamera.getNumberOfCameras()
        best_index: Optional[int] = None
        fallback_index: Optional[int] = None
        best_focal = 0.0

        for idx in range(cam_count):
            AndroidCamera.getCameraInfo(idx, info)
            try:
                is_back = info.facing == CameraInfo.CAMERA_FACING_BACK
            except AttributeError:
                is_back = False

            if not is_back:
                continue
            if fallback_index is None:
                fallback_index = idx

            camera_instance = None
            try:
                camera_instance = AndroidCamera.open(idx)
                params = camera_instance.getParameters()
                focal_lengths = []
                for key in ("focal-lengths", "focal-length"):
                    value = params.get(key)
                    if not value:
                        continue
                    try:
                        focal_lengths.extend(float(item) for item in value.split(",") if item)
                    except ValueError:
                        continue
                focal_value = max(focal_lengths) if focal_lengths else 0.0
                if focal_value >= best_focal:
                    best_focal = focal_value
                    best_index = idx
            except Exception as exc:  # pragma: no cover - Android specific
                Logger.warning(f"CameraScanScreen: cannot probe camera {idx}: {exc}")
            finally:
                if camera_instance is not None:
                    camera_instance.release()

        return best_index if best_index is not None else fallback_index

    def _ensure_android_capture_backend(self) -> None:
        """Force XCamera to use the Android-native capture implementation."""
        if platform != "android":
            return

        try:
            from importlib import import_module

            platform_module = import_module("kivy_garden.xcamera.platform_api")
            android_module = import_module("kivy_garden.xcamera.android_api")
            xcamera_module = import_module("kivy_garden.xcamera.xcamera")
        except ImportError:
            Logger.warning("CameraScanScreen: Unable to enforce Android capture backend.")
            return

        android_take_picture = getattr(android_module, "take_picture", None)
        if not callable(android_take_picture):
            return

        if getattr(platform_module, "take_picture", None) is not android_take_picture:
            platform_module.take_picture = android_take_picture
        if getattr(xcamera_module, "take_picture", None) is not android_take_picture:
            xcamera_module.take_picture = android_take_picture

    def _show_camera_error(self, message: str) -> None:
        if not self.camera_holder:
            return
        if self._camera_error_label is None:
            self._camera_error_label = Label(
                text=message,
                halign="center",
                valign="middle",
                color=(0.95, 0.35, 0.35, 1),
                size_hint=(0.9, 0.9),
            )
            self._camera_error_label.bind(
                size=lambda lbl, size: setattr(lbl, "text_size", size),
            )
        if self._camera_error_label.parent is None:
            self.camera_holder.add_widget(self._camera_error_label)

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
