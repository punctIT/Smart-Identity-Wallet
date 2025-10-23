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
from kivy.clock import Clock

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog

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

        # Simple overlay notification system (no MDDialog)
        self._notification_overlay: Optional[MDBoxLayout] = None
        self._notification_event = None

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
        self._cancel_processing_flow()
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
                # Ensure buttons stay hidden after restart
                Clock.schedule_once(lambda dt: self._remove_default_capture_button(), 0.1)
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
            # Camera este pornită deja în _init_camera_widget
        else:
            Logger.warning("CameraScanScreen: Camera/storage permission denied.")
            self._show_camera_error("Permisiunea pentru cameră/stocare a fost refuzată.")

    # ------------------------------------------------------------------
    # Camera
    # ------------------------------------------------------------------
    def _init_camera_widget(self) -> None:
        if not self.camera_holder or self.camera_view:
            return

        capture_dir = self._build_capture_dir()
        camera_kwargs = {"play": False, "directory": str(capture_dir)}
        
        # Force disable XCamera controls from the start
        camera_kwargs["show_controls"] = False

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

        # MODIFICARE: Aplicăm rotația imediat, înainte de a adăuga la layout
        # Setăm camera să ocupe tot spațiul disponibil și să mențină aspect ratio
        camera.size_hint = (1, 1)
        camera.allow_stretch = True  # Permite stretch pentru dimensiuni mai mari
        camera.keep_ratio = True     # Menține aspect ratio

        # Rotirea 90° stânga
        with camera.canvas.before:
            PushMatrix()
            self._rotation = Rotate(angle=-90, origin=camera.center)
        with camera.canvas.after:
            PopMatrix()

        def _update_origin(*_):
            if self._rotation:
                self._rotation.origin = camera.center

        camera.bind(pos=_update_origin, size=_update_origin)

        # Când o poză este făcută, rescanare, afișare popup și navigare înapoi
        def on_picture(_, filepath):
            Logger.info(f"CameraScanScreen: Saved photo -> {filepath}")
            print(f"[Camera] photo saved -> {filepath}", flush=True)
            self._capture_in_progress = False
            if self.capture_button:
                self.capture_button.disabled = False
            if platform == "android" and MediaScannerConnection:
                ctx = PythonActivity.mActivity
                MediaScannerConnection.scanFile(ctx, [filepath], None, None)
            self._on_capture_completed(Path(filepath))

        camera.bind(on_picture_taken=on_picture)

        self.camera_view = camera
        self._ensure_android_capture_backend()
        
        # Aggressive button hiding - call before and after adding to layout
        self._remove_default_capture_button()
        self.camera_holder.add_widget(self.camera_view)
        
        # Schedule another button removal after widget is added
        Clock.schedule_once(lambda dt: self._remove_default_capture_button(), 0.1)
        Clock.schedule_once(lambda dt: self._remove_default_capture_button(), 0.5)

        if self._camera_error_label and self._camera_error_label.parent:
            self._camera_error_label.parent.remove_widget(self._camera_error_label)
            self._camera_error_label = None

        # Start camera with retry mechanism for mobile stability
        def _start_camera_with_retry(attempt=0):
            try:
                camera.play = True
                Logger.info("CameraScanScreen: Camera started successfully")
            except Exception as exc:  # noqa: BLE001
                Logger.error(f"CameraScanScreen: unable to start camera preview (attempt {attempt + 1}): {exc}")
                print(f"[Camera] start preview failed (attempt {attempt + 1}): {exc}", flush=True)
                
                if attempt < 2 and platform == "android":  # Retry up to 3 times on Android
                    Logger.info(f"CameraScanScreen: Retrying camera start in 1 second...")
                    Clock.schedule_once(lambda dt: _start_camera_with_retry(attempt + 1), 1.0)
                else:
                    self._show_camera_error("Camera indisponibilă.\nNu am reușit să pornesc previzualizarea.")
                    self._dispose_camera()
                    return
        
        _start_camera_with_retry()

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
    # Simple overlay notification system (replaces unreliable MDDialog)
    # ------------------------------------------------------------------
    def _on_capture_completed(self, filepath: Path) -> None:
        """Called after XCamera fired on_picture_taken."""
        msg = f"Fotografie salvată:\n{filepath.name}"
        
        self._show_success_overlay(msg)
        
        # Schedule auto-close and navigation after 2 seconds
        if self._notification_event:
            self._notification_event.cancel()
        self._notification_event = Clock.schedule_once(self._finish_processing, 2.0)

    def _show_success_overlay(self, message: str) -> None:
        """Show a simple success overlay that works reliably on mobile."""
        # Remove any existing overlay
        self._remove_notification_overlay()
        
        # Create success overlay
        from kivymd.uix.card import MDCard
        
        overlay = MDBoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            width=dp(280),
            height=dp(120),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            spacing=dp(10),
            padding=dp(20)
        )
        
        # Background card
        card = MDCard(
            md_bg_color=(0.2, 0.7, 0.2, 0.95),  # Green with transparency
            size_hint=(1, 1),
            elevation=10,
            radius=[15, 15, 15, 15]
        )
        
        # Success icon
        icon = MDLabel(
            text="✓",
            font_size=dp(32),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            halign="center",
            size_hint_y=0.4
        )
        
        # Message text
        text_label = MDLabel(
            text=message,
            font_size=dp(14),
            theme_text_color="Custom", 
            text_color=(1, 1, 1, 1),
            halign="center",
            text_size=(dp(240), None),
            size_hint_y=0.6
        )
        
        overlay.add_widget(icon)
        overlay.add_widget(text_label)
        
        # Add card background
        card_container = MDBoxLayout(size_hint=(1, 1))
        card_container.add_widget(card)
        card_container.add_widget(overlay)
        
        self._notification_overlay = card_container
        
        # Add to the main screen (not camera_holder to ensure it's on top)
        if self.children:
            self.add_widget(self._notification_overlay)
        
        Logger.info(f"CameraScanScreen: Showing success overlay: {message}")
        print(f"[Camera] Success overlay shown: {message}", flush=True)

    def _remove_notification_overlay(self) -> None:
        """Remove the notification overlay if it exists."""
        if self._notification_overlay and self._notification_overlay.parent:
            self._notification_overlay.parent.remove_widget(self._notification_overlay)
        self._notification_overlay = None

    def _finish_processing(self, *_):
        """Remove overlay and navigate back."""
        self._notification_event = None
        
        # Reset capture state
        self._capture_in_progress = False 
        if self.capture_button:
            self.capture_button.disabled = False
            
        # Remove overlay and navigate
        self._remove_notification_overlay()
        self._go_back()

    def _cancel_processing_flow(self) -> None:
        """Cancel any scheduled events and remove overlay."""
        if self._notification_event:
            self._notification_event.cancel()
            self._notification_event = None
        self._remove_notification_overlay()


    def _finish_processing(self, *_):
        """
        Închide dialogul și navighează înapoi.
        """
        self._processing_event = None
        
        # MODIFICARE: Resetăm starea înainte de a închide și naviga.
        self._capture_in_progress = False 
        if self.capture_button:
            self.capture_button.disabled = False
            
        self._dismiss_processing_dialog()
        self._go_back()

    def _show_fallback_notification(self, message: str) -> None:
        """Arată un label temporar ca fallback dacă MDDialog nu funcționează."""
        if self._fallback_label:
            if self._fallback_label.parent:
                self._fallback_label.parent.remove_widget(self._fallback_label)
        
        self._fallback_label = MDLabel(
            text=message,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint=(0.8, None),
            height=dp(100),
            halign="center",
            markup=True
        )
        
        if self.camera_holder:
            self.camera_holder.add_widget(self._fallback_label)

    def _dismiss_processing_dialog(self) -> None:
        """
        Închide dialogul dacă este deschis.
        """
        if self._processing_dialog:
            try:
                self._processing_dialog.dismiss()
            except Exception as e:
                Logger.warning(f"CameraScanScreen: Failed to dismiss dialog: {e}")
            finally:
                self._processing_dialog = None
        
        # Șterge și fallback label-ul dacă există
        if self._fallback_label and self._fallback_label.parent:
            self._fallback_label.parent.remove_widget(self._fallback_label)
            self._fallback_label = None

    def _cancel_processing_flow(self) -> None:
        """Anulează evenimentele temporizate și închide dialogul."""
        if self._processing_event:
            self._processing_event.cancel()
            self._processing_event = None
        self._dismiss_processing_dialog()

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
        self._cancel_processing_flow()

    def _remove_default_capture_button(self) -> None:
        """Remove the stock XCamera capture button so our custom control is the only one."""
        if not self.camera_view:
            return
        
        # Method 1: Disable show_controls property
        if hasattr(self.camera_view, 'show_controls'):
            self.camera_view.show_controls = False
        
        # Method 2: Hide via XCamera property if available
        if hasattr(self.camera_view, 'show_shoot_button'):
            self.camera_view.show_shoot_button = False
        
        # Method 3: Manual removal from ids
        if hasattr(self.camera_view, "ids") and self.camera_view.ids:
            shoot_button = self.camera_view.ids.get("shoot_button")
            if shoot_button and shoot_button.parent:
                try:
                    shoot_button.parent.remove_widget(shoot_button)
                    Logger.info("CameraScanScreen: Removed shoot_button via ids")
                except:
                    pass
        
        # Method 4: Search and remove any buttons in camera widget tree
        self._recursive_remove_buttons(self.camera_view)
    
    def _recursive_remove_buttons(self, widget):
        """Recursively search and remove any buttons that might be capture buttons."""
        if not widget:
            return
        
        # Remove buttons that look like camera capture buttons
        children_to_remove = []
        for child in widget.children:
            if hasattr(child, '__class__'):
                class_name = child.__class__.__name__.lower()
                # Look for button-like widgets
                if 'button' in class_name:
                    # Check if it might be a capture button
                    if hasattr(child, 'text') and child.text in ['', '●', '⚫', 'capture', 'shoot']:
                        children_to_remove.append(child)
                    elif hasattr(child, 'background_normal') or hasattr(child, 'source'):
                        children_to_remove.append(child)
            
            # Recurse into child widgets
            self._recursive_remove_buttons(child)
        
        # Remove identified buttons
        for btn in children_to_remove:
            try:
                widget.remove_widget(btn)
                Logger.info(f"CameraScanScreen: Removed button widget: {btn.__class__.__name__}")
            except:
                pass

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
        self._cancel_processing_flow()

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
            # XCamera va apela on_picture_taken la finalizare
            self.camera_view.shoot() 
        except Exception as exc:
            Logger.error(f"CameraScanScreen: Failed to shoot photo: {exc}")
            print(f"[Camera] capture failed: {exc}", flush=True)
            self._capture_in_progress = False
            if self.capture_button:
                self.capture_button.disabled = False
            return

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