from __future__ import annotations

from pathlib import Path
from typing import Optional

from kivy.app import App
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.utils import platform
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

from kivy_garden.xcamera.xcamera import XCamera

from frontend.screens.widgets.custom_alignment import Alignment

try:
    if platform == "android":
        from android.permissions import Permission, check_permission, request_permissions
        from android.storage import primary_external_storage_path
        from jnius import autoclass

        MediaScannerConnection = autoclass("android.media.MediaScannerConnection")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
    else:
        Permission = check_permission = request_permissions = None
        primary_external_storage_path = None
        MediaScannerConnection = None
        PythonActivity = None
        autoclass = None
except ImportError:
    Permission = check_permission = request_permissions = None
    primary_external_storage_path = None
    MediaScannerConnection = None
    PythonActivity = None
    autoclass = None


class CameraScanScreen(MDScreen, Alignment):
    """Camera screen that saves photos in an accessible folder and rotates the preview 90°."""

    def __init__(self, server=None, **kwargs):
        super().__init__(name="camera_scan", **kwargs)
        self.server = server
        self.camera_view: Optional[XCamera] = None
        self.camera_holder: Optional[MDBoxLayout] = None
        self._camera_error_label: Optional[Label] = None
        self._awaiting_permission = False
        self._camera_index: Optional[int] = None
        self._rotation = None
        self.capture_button: Optional[MDIconButton] = None
        self._capture_in_progress = False

        self._build_ui()

    # ------------------------------------------------------------------
    # UI
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

        header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48))
        back_btn = MDIconButton(
            icon="arrow-left",
            theme_icon_color="Custom",
            icon_color=(1, 1, 1, 0.92),
            on_release=lambda *_: self._go_back(),
        )
        header.add_widget(back_btn)
        header.add_widget(MDLabel())
        root.add_widget(header)

        self.camera_holder = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            padding=(0, 0, 0, 0),
            spacing=0,
        )
        root.add_widget(self.camera_holder)

        controls = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(72),
            padding=(dp(12), dp(8)),
        )
        controls.add_widget(Widget())
        capture_btn = MDIconButton(
            icon="camera",
            theme_icon_color="Custom",
            icon_color=(1, 1, 1, 0.95),
            icon_size=dp(48),
            disabled=True,
            on_release=lambda *_: self.capture_photo(),
        )
        self.capture_button = capture_btn
        controls.add_widget(capture_btn)
        controls.add_widget(Widget())
        root.add_widget(controls)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def on_pre_enter(self, *_):
        super().on_pre_enter()
        self._ensure_camera_ready()
        if self.camera_view:
            try:
                self.camera_view.play = True
            except Exception as exc:  # noqa: BLE001
                Logger.error(f"CameraScanScreen: unable to start preview: {exc}")
                print(f"[Camera] start preview failed: {exc}", flush=True)
                self._show_camera_error("Camera indisponibilă.\nNu am reușit să pornesc previzualizarea.")
                self._dispose_camera()

    def on_leave(self, *_):
        super().on_leave()
        if self.camera_view:
            self.camera_view.play = False

    # ------------------------------------------------------------------
    # Permissions + camera setup
    # ------------------------------------------------------------------
    def _ensure_camera_ready(self) -> None:
        if platform == "android" and Permission and request_permissions and check_permission:
            needed = [Permission.CAMERA]
            read_images = getattr(Permission, "READ_MEDIA_IMAGES", None)
            if read_images:
                needed.append(read_images)
            # fallback for older APIs
            if hasattr(Permission, "WRITE_EXTERNAL_STORAGE"):
                needed.append(Permission.WRITE_EXTERNAL_STORAGE)

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
        if all(grants):
            self._awaiting_permission = False
            self._init_camera_widget()
            if self.camera_view:
                self.camera_view.play = True
        else:
            Logger.warning("CameraScanScreen: Camera/storage permission denied.")

    # ------------------------------------------------------------------
    # Camera
    # ------------------------------------------------------------------
    def _init_camera_widget(self) -> None:
        if not self.camera_holder or self.camera_view:
            return

        capture_dir = self._build_capture_dir()
        camera_kwargs = {"play": False, "directory": str(capture_dir)}

        if platform == "android":
            index = self._select_primary_camera_index()
            if index is not None:
                self._camera_index = index
                camera_kwargs["index"] = index

        try:
            camera = XCamera(**camera_kwargs)
        except Exception as exc:
            Logger.error(f"CameraScanScreen: Unable to initialise camera: {exc}")
            self._show_camera_error("Camera indisponibilă.\nVerifică permisiunile sau conectează o cameră.")
            return

        camera.size_hint = (1, 1)

        # Rotate 90° left
        with camera.canvas.before:
            PushMatrix()
            self._rotation = Rotate(angle=-90, origin=camera.center)
        with camera.canvas.after:
            PopMatrix()

        def _update_origin(*_):
            if self._rotation:
                self._rotation.origin = camera.center

        camera.bind(pos=_update_origin, size=_update_origin)

        # When a picture is taken, rescan so Gallery sees it
        def on_picture(_, filepath):
            Logger.info(f"CameraScanScreen: Saved photo -> {filepath}")
            print(f"[Camera] photo saved -> {filepath}", flush=True)
            self._capture_in_progress = False
            if self.capture_button:
                self.capture_button.disabled = False
            if platform == "android" and MediaScannerConnection:
                ctx = PythonActivity.mActivity
                MediaScannerConnection.scanFile(ctx, [filepath], None, None)

        camera.bind(on_picture_taken=on_picture)

        self.camera_view = camera
        self._ensure_android_capture_backend()
        self._remove_default_capture_button()
        self.camera_holder.add_widget(self.camera_view)

        if self._camera_error_label and self._camera_error_label.parent:
            self._camera_error_label.parent.remove_widget(self._camera_error_label)
            self._camera_error_label = None

        try:
            camera.play = True
        except Exception as exc:  # noqa: BLE001
            Logger.error(f"CameraScanScreen: unable to start camera preview: {exc}")
            print(f"[Camera] start preview failed: {exc}", flush=True)
            self._show_camera_error("Camera indisponibilă.\nNu am reușit să pornesc previzualizarea.")
            self._dispose_camera()
            return

        if self.capture_button:
            self.capture_button.disabled = False
        self._capture_in_progress = False

    # ------------------------------------------------------------------
    # Filesystem helpers
    # ------------------------------------------------------------------
    def _build_capture_dir(self) -> Path:
        """Save captures in a public folder: /storage/emulated/0/Pictures/SmartID/"""
        try:
            if platform == "android":
                from android.storage import primary_external_storage_path

                # Get base external storage path, e.g. /storage/emulated/0
                base = Path(primary_external_storage_path())

                # Put captures in the public Pictures directory
                target = base / "Pictures" / "SmartID"
            else:
                # Fallback for desktop
                target = Path.home() / "Pictures" / "SmartID"
        except Exception as e:
            Logger.warning(f"CameraScanScreen: Could not resolve public capture dir: {e}")
            target = Path.home() / "Pictures" / "SmartID"

        target.mkdir(parents=True, exist_ok=True)
        Logger.info(f"CameraScanScreen: Capture dir = {target}")
        return target

    # ------------------------------------------------------------------
    # Android helpers
    # ------------------------------------------------------------------
    def _select_primary_camera_index(self) -> Optional[int]:
        """Select back-facing camera if available."""
        if platform != "android" or autoclass is None:
            return None
        try:
            AndroidCamera = autoclass("android.hardware.Camera")
            CameraInfo = autoclass("android.hardware.Camera$CameraInfo")
        except Exception as exc:
            Logger.warning(f"CameraScanScreen: cannot access camera info: {exc}")
            return None

        info = CameraInfo()
        cam_count = AndroidCamera.getNumberOfCameras()
        for idx in range(cam_count):
            AndroidCamera.getCameraInfo(idx, info)
            try:
                if info.facing == CameraInfo.CAMERA_FACING_BACK:
                    return idx
            except AttributeError:
                pass
        return 0 if cam_count > 0 else None

    def _ensure_android_capture_backend(self) -> None:
        """Force XCamera to use native Android picture backend."""
        if platform != "android":
            return
        try:
            from importlib import import_module

            platform_api = import_module("kivy_garden.xcamera.platform_api")
            android_api = import_module("kivy_garden.xcamera.android_api")
            xcamera_module = import_module("kivy_garden.xcamera.xcamera")
        except ImportError:
            Logger.warning("CameraScanScreen: Could not import xcamera backend modules.")
            return

        android_take_picture = getattr(android_api, "take_picture", None)
        if callable(android_take_picture):
            if not getattr(android_api, "_smartid_rotation_patch", False):
                original_take_picture = android_take_picture

                def rotated_take_picture(camera_widget, filename, on_success):
                    android_camera = getattr(getattr(camera_widget, "_camera", None), "_android_camera", None)
                    if android_camera:
                        try:
                            params = android_camera.getParameters()
                            params.setRotation(-90)
                            android_camera.setParameters(params)
                        except Exception as exc:  # noqa: BLE001
                            Logger.warning(f"CameraScanScreen: unable to adjust camera rotation: {exc}")
                    return original_take_picture(camera_widget, filename, on_success)

                android_api._smartid_rotation_patch = True
                android_api.take_picture = rotated_take_picture

            platform_api.take_picture = android_api.take_picture
            xcamera_module.take_picture = android_api.take_picture

    # ------------------------------------------------------------------
    # Error + navigation
    # ------------------------------------------------------------------
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
            self._camera_error_label.bind(size=lambda lbl, s: setattr(lbl, "text_size", s))
        if not self._camera_error_label.parent:
            self.camera_holder.add_widget(self._camera_error_label)
        if self.capture_button:
            self.capture_button.disabled = True
        self._capture_in_progress = False

    def _remove_default_capture_button(self) -> None:
        """Remove the stock XCamera capture button so our custom control is the only one."""
        if not self.camera_view:
            return
        shoot_button = getattr(self.camera_view, "ids", {}).get("shoot_button") if hasattr(self.camera_view, "ids") else None
        if shoot_button and shoot_button.parent:
            shoot_button.parent.remove_widget(shoot_button)

    def _dispose_camera(self) -> None:
        """Release current camera widget and reset state."""
        if self.camera_view:
            try:
                self.camera_view.play = False
            except Exception:
                pass
            if self.camera_view.parent:
                self.camera_view.parent.remove_widget(self.camera_view)
        self.camera_view = None
        self._rotation = None
        if self.capture_button:
            self.capture_button.disabled = True
        self._capture_in_progress = False

    # ------------------------------------------------------------------
    # Capture actions
    # ------------------------------------------------------------------
    def capture_photo(self) -> None:
        """Trigger a capture and log to terminal."""
        if self._capture_in_progress:
            Logger.info("CameraScanScreen: Capture already in progress.")
            return
        if not self.camera_view:
            Logger.warning("CameraScanScreen: Capture requested without an active camera.")
            self._show_camera_error("Camera indisponibilă.")
            return

        Logger.info("CameraScanScreen: capture requested, shooting photo.")
        print("[Camera] capture requested", flush=True)
        self._capture_in_progress = True
        if self.capture_button:
            self.capture_button.disabled = True

        try:
            self.camera_view.shoot()
        except Exception as exc:
            Logger.error(f"CameraScanScreen: Failed to shoot photo: {exc}")
            print(f"[Camera] capture failed: {exc}", flush=True)
            self._capture_in_progress = False
            if self.capture_button:
                self.capture_button.disabled = False
            return

        if self.capture_button:
            self.capture_button.disabled = True

    def _go_back(self) -> None:
        manager = getattr(self, "manager", None)
        if not manager:
            return
        if manager.has_screen("home"):
            tr = getattr(manager, "transition", None)
            prev_dir = getattr(tr, "direction", None)
            if tr:
                tr.direction = "down"
            manager.current = "home"
            if tr and prev_dir:
                tr.direction = prev_dir
        else:
            manager.current = manager.previous()


__all__ = ["CameraScanScreen"]
