from datetime import datetime
from pathlib import Path

from kivy.metrics import dp, sp
from kivy.logger import Logger
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Line, PushMatrix, PopMatrix, Rotate
from kivy.app import App
from kivy.utils import platform

try:
    if platform == "android":
        from android.storage import app_storage_path, primary_external_storage_path  # type: ignore
        from android.permissions import (  # type: ignore
            request_permissions,
            check_permission,
            Permission,
        )
    else:  # pragma: no cover
        app_storage_path = None
        primary_external_storage_path = None
        request_permissions = None
        check_permission = None
        Permission = None
except ImportError:  # pragma: no cover
    app_storage_path = None
    primary_external_storage_path = None
    request_permissions = None
    check_permission = None
    Permission = None

from frontend.screens.widgets.custom_alignment import Alignment
from frontend.screens.widgets.custom_background import GradientBackground
from frontend.screens.widgets.custom_buttons import CustomButton
from frontend.screens.widgets.custom_label import CustomLabels


TEXT_PRIMARY = (0.92, 0.95, 1.00, 1)
TEXT_SECONDARY = (0.70, 0.76, 0.86, 1)
ACCENT = (0.25, 0.60, 1.00, 1)
ACCENT_MUTED = (0.16, 0.20, 0.28, 0.85)


class CameraFrame(AnchorLayout):
    def __init__(self, camera_widget, **kwargs):
        super().__init__(**kwargs)
        self.camera_widget = camera_widget
        self.add_widget(camera_widget)

        with camera_widget.canvas.before:
            PushMatrix()
            self._rotation = Rotate(angle=-90, origin=camera_widget.center)
        with camera_widget.canvas.after:
            PopMatrix()

        camera_widget.bind(pos=self._update_rotation_origin, size=self._update_rotation_origin)

        with self.canvas.after:
            PushMatrix()
            self._frame_rotation = Rotate(angle=-90, origin=self.center)
            Color(1, 1, 1, 0.45)
            self._frame = Line(width=dp(2))
            PopMatrix()

        self.bind(size=self._update_frame, pos=self._update_frame)
        self.bind(size=self._update_rotation_origin, pos=self._update_rotation_origin)

    def _update_rotation_origin(self, *_):
        if self._rotation:
            self._rotation.origin = self.camera_widget.center
        if self._frame_rotation:
            self._frame_rotation.origin = self.center

    def _update_frame(self, *_):
        aspect_ratio = 1.58
        available_width = max(self.width * 0.82, 0)
        available_height = max(self.height * 0.82, 0)
        width = min(available_width, available_height * aspect_ratio)
        height = width / aspect_ratio if aspect_ratio else 0
        x = self.center_x - width / 2
        y = self.center_y - height / 2
        self._frame.rectangle = (x, y, width, height)


class CameraScanScreen(Screen, CustomLabels, CustomButton, Alignment):
    def __init__(self, server=None, **kwargs):
        super().__init__(name="camera_scan", **kwargs)
        self.server = server
        self.camera_widget = None
        self.camera_frame = None
        self.preview_holder = None
        self._camera_available = False
        self._awaiting_permission = False

        self.add_widget(GradientBackground())

        content = BoxLayout(
            orientation="vertical",
            padding=[dp(18), dp(16), dp(18), dp(24)],
            spacing=dp(18),
        )
        self.add_widget(content)

        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(12))
        back_btn = self.make_rounded_button("Înapoi", ACCENT_MUTED, self._go_back)
        back_btn.size_hint = (None, None)
        back_btn.width = dp(120)
        header.add_widget(back_btn)
        title_label = Label(
            text="[b]Scanează document[/b]",
            markup=True,
            color=TEXT_PRIMARY,
            font_size=sp(20),
            halign="center",
            valign="middle",
        )
        title_label.bind(size=lambda lbl, size: setattr(lbl, "text_size", size))
        header.add_widget(title_label)
        content.add_widget(header)

        instructions = Label(
            text="Aliniază documentul în cadru și apasă „Fotografiază”.",
            color=TEXT_SECONDARY,
            font_size=sp(15),
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(38),
        )
        instructions.bind(size=lambda lbl, size: setattr(lbl, "text_size", size))
        content.add_widget(instructions)

        self.preview_holder = AnchorLayout(size_hint=(1, 1))
        self.preview_holder.padding = [0, 0, 0, dp(12)]
        content.add_widget(self.preview_holder)
        self._show_placeholder("Se inițializează camera...")

        self.capture_btn = self.make_rounded_button("Fotografiază", ACCENT, self._capture)
        self.capture_btn.size_hint = (None, None)
        self.capture_btn.width = dp(200)
        self.capture_btn.disabled = True
        content.add_widget(
            self.center_row(self.capture_btn, rel_width=0.6, min_w=dp(220), max_w=dp(320), height=dp(46))
        )

        self.status_label = Label(
            text="",
            color=TEXT_SECONDARY,
            font_size=sp(14),
            size_hint_y=None,
            height=dp(20),
            halign="center",
            valign="middle",
        )
        self.status_label.bind(size=lambda lbl, size: setattr(lbl, "text_size", size))
        content.add_widget(self.status_label)

    def on_pre_enter(self, *_):
        self._ensure_camera_ready()

    def on_leave(self, *_):
        self._stop_camera()

    # ------------------------------------------------------------------
    # Permission & initialization helpers
    # ------------------------------------------------------------------
    def _ensure_camera_ready(self):
        if platform == "android" and Permission and request_permissions and check_permission:
            if not check_permission(Permission.CAMERA):
                if not self._awaiting_permission:
                    self._awaiting_permission = True
                    self._show_placeholder("Solicit permisiunea pentru cameră...")
                    request_permissions([Permission.CAMERA], self._on_permission_result)
                return
        self._awaiting_permission = False
        self._start_camera()

    def _on_permission_result(self, permissions, results):
        if not permissions:
            return
        granted = all(results)
        if granted:
            self._ensure_camera_ready()
        else:
            self._show_placeholder("Permisiunea pentru cameră a fost refuzată.")
            self.capture_btn.disabled = True
            self.status_label.text = "Permisiunea este necesară pentru a fotografia documente."

    # ------------------------------------------------------------------
    # Camera lifecycle
    # ------------------------------------------------------------------
    def _build_camera_widget(self):
        last_exc = None
        widget = None

        for index in (0, 1):
            for resolution in [(1920, 1080), (1280, 720), (640, 480)]:
                try:
                    widget = Camera(resolution=resolution, play=False, index=index)
                    break
                except Exception as exc:  # noqa: BLE001
                    last_exc = exc
                    widget = None
            if widget:
                break

        if widget is None:
            Logger.warning(f"CameraScanScreen: camera unavailable ({last_exc})")
            self._camera_available = False
            self.camera_widget = None
            return None

        widget.allow_stretch = True
        widget.keep_ratio = True
        self._camera_available = True
        self.camera_widget = widget
        return CameraFrame(widget, size_hint=(1, 1))

    def _show_placeholder(self, message: str):
        if not self.preview_holder:
            return
        placeholder = AnchorLayout(size_hint=(1, 1))
        label = Label(
            text=message,
            color=TEXT_SECONDARY,
            font_size=sp(16),
            halign="center",
            valign="middle",
        )
        label.bind(size=lambda lbl, size: setattr(lbl, "text_size", size))
        placeholder.add_widget(label)
        self.preview_holder.clear_widgets()
        self.preview_holder.add_widget(placeholder)

    def _ensure_camera_widget(self) -> bool:
        if self._camera_available and self.camera_widget and self.camera_frame:
            return True

        frame = self._build_camera_widget()
        if not frame:
            self._show_placeholder("Camera nu este disponibilă pe acest dispozitiv.")
            self.capture_btn.disabled = True
            return False

        self.preview_holder.clear_widgets()
        self.preview_holder.add_widget(frame)
        self.camera_frame = frame
        return True

    def _start_camera(self):
        if not self._ensure_camera_widget():
            return

        if self.camera_widget:
            try:
                self.camera_widget.play = True
            except Exception as exc:  # noqa: BLE001
                Logger.warning(f"CameraScanScreen: failed to start camera ({exc})")
                self.status_label.text = "Nu am putut porni camera."
                self.capture_btn.disabled = True
                return

        self.status_label.text = ""
        self.capture_btn.disabled = False

    def _stop_camera(self):
        if self._camera_available and self.camera_widget:
            self.camera_widget.play = False

    # ------------------------------------------------------------------
    # Capture helpers
    # ------------------------------------------------------------------
    def _resolve_capture_directory(self) -> Path:
        app = App.get_running_app()

        if platform == "android":
            storage_root = None
            if callable(primary_external_storage_path):
                try:
                    storage_root = Path(primary_external_storage_path())
                except Exception:  # noqa: BLE001
                    storage_root = None
            if storage_root:
                target_dir = storage_root / "Pictures" / "SmartIdentityWallet"
            elif app and getattr(app, "user_data_dir", None):
                target_dir = Path(app.user_data_dir) / "captures"
            elif callable(app_storage_path):
                try:
                    target_dir = Path(app_storage_path())
                except Exception:  # noqa: BLE001
                    target_dir = Path.cwd() / "captures"
            else:
                target_dir = Path.cwd() / "captures"
        else:
            if app and getattr(app, "user_data_dir", None):
                target_dir = Path(app.user_data_dir) / "captures"
            else:
                target_dir = Path.cwd() / "captures"

        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir

    def _capture(self, *_):
        if not self._camera_available or not self.camera_widget:
            self.status_label.text = "Camera nu este disponibilă."
            return
        target_dir = self._resolve_capture_directory()
        filename = datetime.now().strftime("scan_%Y%m%d_%H%M%S.png")
        filepath = target_dir / filename
        try:
            self.camera_widget.export_to_png(str(filepath))
        except Exception as exc:  # noqa: BLE001
            self.status_label.text = f"Nu am putut salva fotografia: {exc}"
        else:
            try:
                rel_root = Path(__file__).resolve().parents[4]
                rel_path = filepath.relative_to(rel_root)
            except ValueError:
                rel_path = filepath
            self.status_label.text = f"Fotografia salvată: {rel_path}"

    def _go_back(self, *_):
        if self.manager and self.manager.has_screen("home"):
            transition = getattr(self.manager, "transition", None)
            previous_direction = getattr(transition, "direction", None)
            if transition:
                transition.direction = "down"
            self.manager.current = "home"
            if transition and previous_direction:
                transition.direction = previous_direction
