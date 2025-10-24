from __future__ import annotations

from pathlib import Path
from typing import Optional
import time
import os

from kivy.app import App
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.utils import platform
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock

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
    """Camera screen that saves photos in an accessible folder using Kivy Camera."""

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
        
        # Photo saving
        self._capture_dir: Optional[Path] = None

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

        # Header este comentat în codul tău, așa că îl păstrăm așa.
        
        self.camera_holder = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, 0.85),  # Take more space, leaving room for controls
            padding=(0, 0, 0, 0),
            spacing=0,
        )
        root.add_widget(self.camera_holder)

        controls = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, 0.15),  # Use remaining space
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
        Logger.info("CameraScanScreen: Entering camera screen")
        
        # Force permission check and camera setup
        self._awaiting_permission = False  # Reset state
        self._ensure_camera_ready()
        
        # Bind app lifecycle events pentru Android
        if platform == "android":
            app = App.get_running_app()
            if app and hasattr(app, 'bind'):
                app.bind(on_pause=self._on_app_pause)
                app.bind(on_resume=self._on_app_resume)

    def on_enter(self, *_):
        """Called when screen becomes active - restart camera if needed."""
        super().on_enter()
        if self.camera_view and not self.camera_view.play:
            try:
                self.camera_view.play = True
            except Exception as e:
                Logger.warning(f"CameraScanScreen: Failed to restart camera on enter: {e}")

    def on_leave(self, *_):
        super().on_leave()
        if self.camera_view:
            self.camera_view.play = False
        # Unbind app lifecycle events
        if platform == "android":
            app = App.get_running_app()
            if app and hasattr(app, 'unbind'):
                try:
                    app.unbind(on_pause=self._on_app_pause)
                    app.unbind(on_resume=self._on_app_resume)
                except:
                    pass

    # ------------------------------------------------------------------
    # App lifecycle handlers (Android)
    # ------------------------------------------------------------------
    def _on_app_pause(self, *args):
        """Called when app is paused (minimized, switched away)."""
        if self.camera_view:
            try:
                self.camera_view.play = False
                Logger.info("CameraScanScreen: Camera paused due to app pause")
            except Exception as e:
                Logger.warning(f"CameraScanScreen: Failed to pause camera: {e}")
        return True  # Allow pause

    def _on_app_resume(self, *args):
        """Called when app is resumed (brought back to foreground)."""
        # Only restart camera if this screen is currently active
        if hasattr(self, 'manager') and self.manager and self.manager.current == self.name:
            if self.camera_view:
                # Add small delay to ensure system is ready
                Clock.schedule_once(self._restart_camera, 0.5)
                Logger.info("CameraScanScreen: Scheduled camera restart after app resume")

    def _restart_camera(self, *args):
        """Restart camera after app resume."""
        if self.camera_view:
            try:
                self.camera_view.play = True
                Logger.info("CameraScanScreen: Camera restarted after resume")
            except Exception as e:
                Logger.error(f"CameraScanScreen: Failed to restart camera: {e}")
                # If restart fails, reinitialize the whole camera
                self._dispose_camera()
                self._ensure_camera_ready()

    # ------------------------------------------------------------------
    # Permissions + camera setup
    # ------------------------------------------------------------------
    def _ensure_camera_ready(self) -> None:
        Logger.info("CameraScanScreen: Checking camera permissions and setup")
        
        if platform == "android" and Permission and request_permissions and check_permission:
            needed = [Permission.CAMERA]
            
            # For Android 13+ (API 33+), we need READ_MEDIA_IMAGES instead of older storage permissions
            if hasattr(Permission, "READ_MEDIA_IMAGES"):
                needed.append(Permission.READ_MEDIA_IMAGES)
                Logger.info("CameraScanScreen: Using READ_MEDIA_IMAGES for Android 13+")
            else:
                # Fallback for older APIs
                if hasattr(Permission, "WRITE_EXTERNAL_STORAGE"):
                    needed.append(Permission.WRITE_EXTERNAL_STORAGE)
                if hasattr(Permission, "READ_EXTERNAL_STORAGE"):  
                    needed.append(Permission.READ_EXTERNAL_STORAGE)
                Logger.info("CameraScanScreen: Using legacy storage permissions")

            Logger.info(f"CameraScanScreen: Checking permissions: {[str(p) for p in needed]}")
            granted = all(check_permission(p) for p in needed)
            
            if not granted:
                missing = [str(p) for p in needed if not check_permission(p)]
                Logger.info(f"CameraScanScreen: Missing permissions: {missing}")
                
                if not self._awaiting_permission:
                    self._awaiting_permission = True
                    Logger.info("CameraScanScreen: Requesting permissions...")
                    request_permissions(needed, self._on_permission_result)
                return
            else:
                Logger.info("CameraScanScreen: All permissions granted")

        self._awaiting_permission = False
        self._init_camera_widget()

    def _on_permission_result(self, permissions, grants):
        Logger.info(f"CameraScanScreen: Permission result - permissions: {permissions}, grants: {grants}")
        
        if not permissions:
            Logger.warning("CameraScanScreen: No permissions in result")
            return
        
        # Use Clock.schedule_once to ensure UI updates happen on main thread
        if all(grants):
            Logger.info("CameraScanScreen: All permissions granted, initializing camera")
            self._awaiting_permission = False
            Clock.schedule_once(lambda dt: self._init_camera_widget(), 0)
        else:
            denied = [str(p) for p, granted in zip(permissions, grants) if not granted]
            Logger.warning(f"CameraScanScreen: Permission(s) denied: {denied}")
            error_msg = (
                "Permisiunea pentru cameră/stocare a fost refuzată.\n\n"
                "Pentru a folosi camera, activează permisiunile în Setări > Aplicații > Smart ID Wallet > Permisiuni."
            )
            Clock.schedule_once(lambda dt: self._show_camera_error(error_msg), 0)

    # ------------------------------------------------------------------
    # Camera
    # ------------------------------------------------------------------
    def _init_camera_widget(self) -> None:
        Logger.info("CameraScanScreen: Initializing camera widget")
        
        if not self.camera_holder:
            Logger.error("CameraScanScreen: No camera holder available")
            return
            
        if self.camera_view:
            Logger.info("CameraScanScreen: Camera already exists, disposing first")
            self._dispose_camera()

        self._capture_dir = self._build_capture_dir()
        Logger.info(f"CameraScanScreen: Using capture directory: {self._capture_dir}")
        
        camera_kwargs = {
            "play": False,
            "directory": str(self._capture_dir),
        }
        camera = XCamera(**camera_kwargs)
       
        def _on_capture(instance, filename):
            import os, shutil
            new_name = os.path.join(self._capture_dir, "document.jpg")
            shutil.move(filename, new_name)
            print(f"Saved capture as: {new_name}")
            
        camera.bind(on_capture=_on_capture)
        
        if platform == "android":
            index = self._select_primary_camera_index()
            Logger.info(f"CameraScanScreen: Selected camera index: {index}")
            if index is not None:
                self._camera_index = index
                camera_kwargs["index"] = index

        Logger.info(f"CameraScanScreen: Creating XCamera with kwargs: {camera_kwargs}")
        try:
           
            Logger.info("CameraScanScreen: XCamera created successfully")
        except Exception as exc:
            Logger.error(f"CameraScanScreen: Unable to initialise camera: {exc}")
            import traceback
            Logger.error(f"CameraScanScreen: Full traceback: {traceback.format_exc()}")
            self._show_camera_error(f"Camera indisponibilă.\nEroare: {str(exc)}\n\nVerifică permisiunile sau conectează o cameră.")
            return

        # Setup camera display properties
        camera.size_hint = (1, 1)
        camera.allow_stretch = True
        camera.keep_ratio = True

        # Rotirea 90° stânga pentru Android
        if platform == "android":
            with camera.canvas.before:
                PushMatrix()
                self._rotation = Rotate(angle=-90, origin=camera.center)
            with camera.canvas.after:
                PopMatrix()

            def _update_origin(*_):
                if self._rotation:
                    self._rotation.origin = camera.center

            camera.bind(pos=_update_origin, size=_update_origin)

        # Bind XCamera photo capture callback
        def on_picture(_, filepath):
            Logger.info(f"CameraScanScreen: Photo saved -> {filepath}")
            print(f"[Camera] photo saved -> {filepath}", flush=True)
            
            # Notify Android media scanner if available
            if platform == "android" and MediaScannerConnection:
                try:
                    ctx = PythonActivity.mActivity
                    MediaScannerConnection.scanFile(ctx, [filepath], None, None)
                except Exception as e:
                    Logger.warning(f"CameraScanScreen: Failed to notify media scanner: {e}")
            
            # Use Clock.schedule_once to ensure UI updates happen on main thread
            Clock.schedule_once(lambda dt: self._on_capture_completed(Path(filepath)), 0)

        camera.bind(on_picture_taken=on_picture)

        self.camera_view = camera
        self._ensure_android_capture_backend()
        self._remove_default_capture_button()
        self.camera_holder.add_widget(self.camera_view)

        # Clear any existing error messages
        if self._camera_error_label and self._camera_error_label.parent:
            self._camera_error_label.parent.remove_widget(self._camera_error_label)
            self._camera_error_label = None

        # Start camera with retry mechanism for mobile stability
        def _start_camera_with_retry(attempt=0):
            try:
                camera.play = True
                Logger.info("CameraScanScreen: Camera started successfully")
                if self.capture_button:
                    self.capture_button.disabled = False
                self._capture_in_progress = False
            except Exception as exc:  # noqa: BLE001
                Logger.error(f"CameraScanScreen: unable to start camera preview (attempt {attempt + 1}): {exc}")
                print(f"[Camera] start preview failed (attempt {attempt + 1}): {exc}", flush=True)
                
                if attempt < 2:  # Retry up to 3 times
                    Logger.info(f"CameraScanScreen: Retrying camera start in 1 second...")
                    Clock.schedule_once(lambda dt: _start_camera_with_retry(attempt + 1), 1.0)
                else:
                    self._show_camera_error("Camera indisponibilă.\nNu am reușit să pornesc previzualizarea.")
                    self._dispose_camera()
                    return
        
        _start_camera_with_retry()

    # ------------------------------------------------------------------
    # Filesystem helpers
    # ------------------------------------------------------------------
    def _build_capture_dir(self) -> Path:
        """Save captures in a public folder: /storage/emulated/0/Pictures/SmartID/"""
        try:
            if platform == "android":
                # Get base external storage path, e.g. /storage/emulated/0
                # MODIFICARE: Adăugăm o verificare de siguranță pentru primary_external_storage_path
                base_path = primary_external_storage_path()
                if base_path:
                    base = Path(base_path)
                    target = base / "Pictures" / "SmartID"
                else:
                    raise RuntimeError("External storage path not available.")
            else:
                # Fallback for desktop
                target = Path.home() / "Pictures" / "SmartID"
        except Exception as e:
            Logger.warning(f"CameraScanScreen: Could not resolve public capture dir, falling back: {e}")
            target = Path(App.get_running_app().user_data_dir) / "captures" # Fallback mai sigur
            
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
        """Force XCamera to use native Android picture backend (and set EXIF rotation)."""
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
            # patch rotation once (optional, guards against multiple wraps)
            if not getattr(android_api, "_smartid_rotation_patch", False):
                original_take_picture = android_take_picture

                def rotated_take_picture(camera_widget, filename, on_success):
                    android_camera = getattr(getattr(camera_widget, "_camera", None), "_android_camera", None)
                    if android_camera:
                        try:
                            params = android_camera.getParameters()
                            params.setRotation(90)
                            android_camera.setParameters(params)
                        except Exception as exc:  # noqa: BLE001
                            Logger.warning(f"CameraScanScreen: unable to adjust camera rotation: {exc}")
                    return original_take_picture(camera_widget, filename, on_success)

                android_api._smartid_rotation_patch = True
                android_api.take_picture = rotated_take_picture

            platform_api.take_picture = android_api.take_picture
            xcamera_module.take_picture = android_api.take_picture

    # ------------------------------------------------------------------
    # Direct navigation back after photo capture
    # ------------------------------------------------------------------
    def _on_capture_completed(self, filepath: Path) -> None:
        """Called after XCamera fires on_picture_taken - navigate to OCR processing screen."""
        Logger.info(f"CameraScanScreen: Photo capture completed: {filepath}")
        
        # Reset capture state
        self._capture_in_progress = False
        if self.capture_button:
            self.capture_button.disabled = False
        
        # Navigate to save_data screen with the captured image for OCR processing
        self._navigate_to_save_screen(str(filepath))

    def _navigate_to_save_screen(self, image_path: str) -> None:
        """Navigate to save_data screen with the captured image for OCR processing."""
        print(f"🔄 [NEW CODE] _navigate_to_save_screen called with: {image_path}", flush=True)
        Logger.info(f"CameraScanScreen: Navigating to save_data screen with image: {image_path}")
        
        manager = getattr(self, "manager", None)
        if not manager:
            Logger.error("CameraScanScreen: No screen manager available")
            print("❌ [NEW CODE] No screen manager available!", flush=True)
            return
            
        # Navigate to save_data screen and set image path for OCR processing
        print(f"🔍 [NEW CODE] Navigating to save_data screen...", flush=True)
        if manager.has_screen("save_data"):
            try:
                save_screen = manager.get_screen("save_data")
                save_screen.set_image_path(image_path)
                
                # Set transition direction
                if hasattr(manager, "transition"):
                    manager.transition.direction = "left"
                
                manager.current = "save_data"
                Logger.info(f"CameraScanScreen: Navigated to save_data screen with image: {image_path}")
                print(f"✅ [NEW CODE] Successfully navigated to save_data screen", flush=True)
                
            except Exception as e:
                Logger.error(f"CameraScanScreen: Failed to navigate to save_data screen: {e}")
                print(f"❌ [NEW CODE] Navigation failed: {e}", flush=True)
                # Fallback: go back and cleanup
                self._cleanup_and_go_back(image_path)
        else:
            Logger.error("CameraScanScreen: save_data screen not found")
            print("❌ [NEW CODE] save_data screen not found!", flush=True)
            self._cleanup_and_go_back(image_path)

    def _cleanup_and_go_back(self, image_path: str) -> None:
        """Cleanup image and navigate back as fallback."""
        try:
            filepath = Path(image_path)
            if filepath.exists():
                filepath.unlink()
                Logger.info(f"CameraScanScreen: Cleaned up image: {image_path}")
        except Exception as e:
            Logger.warning(f"CameraScanScreen: Failed to cleanup image: {e}")
        
        self._go_back()

    # All dialog and popup methods removed for direct navigation

    # ------------------------------------------------------------------
    # Error + navigation
    # ------------------------------------------------------------------
    def _show_camera_error(self, message: str) -> None:
        Logger.info(f"CameraScanScreen: Showing camera error: {message}")
        if not self.camera_holder:
            return
            
        # Clear existing error widgets
        self.camera_holder.clear_widgets()
        
        # Create error container
        error_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint=(0.9, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Error message
        error_label = Label(
            text=message,
            halign="center", 
            valign="middle",
            color=(0.95, 0.35, 0.35, 1),
            size_hint_y=None,
            height=dp(120)
        )
        error_label.bind(size=lambda lbl, s: setattr(lbl, "text_size", s))
        error_container.add_widget(error_label)
        
        # Retry button for permissions
        if "permis" in message.lower():
            retry_btn = MDIconButton(
                icon="refresh",
                theme_icon_color="Custom",
                icon_color=(0.25, 0.60, 1.00, 1),
                size_hint=(None, None),
                size=(dp(48), dp(48)),
                pos_hint={'center_x': 0.5},
                on_release=lambda *_: self._retry_permissions()
            )
            error_container.add_widget(retry_btn)
            
            retry_label = Label(
                text="Apasă pentru a încerca din nou",
                halign="center",
                color=(0.7, 0.7, 0.7, 1),
                size_hint_y=None,
                height=dp(30),
                font_size=dp(12)
            )
            error_container.add_widget(retry_label)
        
        self.camera_holder.add_widget(error_container)
        
        if self.capture_button:
            self.capture_button.disabled = True
        self._capture_in_progress = False
    
    def _retry_permissions(self):
        """Manually retry permission request."""
        Logger.info("CameraScanScreen: Manual permission retry requested")
        if self.camera_holder:
            self.camera_holder.clear_widgets()
        self._awaiting_permission = False
        Clock.schedule_once(lambda dt: self._ensure_camera_ready(), 0)

    def _remove_default_capture_button(self) -> None:
        """Remove the stock XCamera capture button so our custom control is the only one."""
        if not self.camera_view:
            return
        
        # Disable default controls
        if hasattr(self.camera_view, 'show_controls'):
             self.camera_view.show_controls = False
             
        # Manual removal as fallback
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
            self.capture_button.disabled = True # Dezactivăm imediat butonul

        try:
            # XCamera will call on_picture_taken callback when done
            self.camera_view.shoot() 
        except Exception as exc:
            Logger.error(f"CameraScanScreen: Failed to shoot photo: {exc}")
            print(f"[Camera] capture failed: {exc}", flush=True)
            self._capture_in_progress = False
            if self.capture_button:
                self.capture_button.disabled = False
            self._show_camera_error(f"Eroare la capturarea fotografiei: {str(exc)}")
            return
    
    # _on_photo_saved removed - using XCamera's on_picture_taken callback instead

    def _go_back(self) -> None:
        manager = getattr(self, "manager", None)
        if not manager:
            return
        if manager.has_screen("save_data"):
            tr = getattr(manager, "transition", None)
            prev_dir = getattr(tr, "direction", None)
            if tr:
                tr.direction = "down"
            manager.current = "save_data"
            if tr and prev_dir:
                tr.direction = prev_dir
        else:
            manager.current = manager.previous()


__all__ = ["CameraScanScreen"]