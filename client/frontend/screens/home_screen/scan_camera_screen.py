from datetime import datetime
from pathlib import Path

from kivy.clock import Clock
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
    else:  # pragma: no cover - desktop fallback
        app_storage_path = None
        primary_external_storage_path = None
except ImportError:  # pragma: no cover - safety net for build variants
    app_storage_path = None
    primary_external_storage_path = None

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
        self.add_widget(self.camera_widget)

        with self.camera_widget.canvas.before:
            PushMatrix()
            self._rotation = Rotate(angle=-90, origin=self.camera_widget.center)
        with self.camera_widget.canvas.after:
            PopMatrix()

        self.camera_widget.bind(pos=self._update_rotation_origin, size=self._update_rotation_origin)

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
        if hasattr(self, "_frame_rotation") and self._frame_rotation:
            self._frame_rotation.origin = self.center

    def _update_frame(self, *_):
        aspect_ratio = 1.58  # width/height ratio approximating an ID card
        available_width = max(self.width * 0.8, 0)
        available_height = max(self.height * 0.8, 0)
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
        self._camera_available = False
        self.status_label = None

        self.add_widget(GradientBackground())

        content = BoxLayout(
            orientation="vertical",
            padding=[dp(18), dp(16), dp(18), dp(24)],
            spacing=dp(18)
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
            valign="middle"
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
            height=dp(38)
        )
        instructions.bind(size=lambda lbl, size: setattr(lbl, "text_size", size))
        content.add_widget(instructions)

        preview_holder = AnchorLayout(size_hint=(1, 1))
        preview_holder.padding = [0, 0, 0, dp(12)]
        self.camera_frame = self._build_camera_widget()
        preview_holder.add_widget(self.camera_frame)
        content.add_widget(preview_holder)

        self.capture_btn = self.make_rounded_button("Fotografiază", ACCENT, self._capture)
        self.capture_btn.size_hint = (None, None)
        self.capture_btn.width = dp(200)
        self.capture_btn.disabled = not self._camera_available
        content.add_widget(self.center_row(self.capture_btn, rel_width=0.6, min_w=dp(220), max_w=dp(320), height=dp(46)))

        self.status_label = Label(
            text="",
            color=TEXT_SECONDARY,
            font_size=sp(14),
            size_hint_y=None,
            height=dp(20),
            halign="center",
            valign="middle"
        )
        self.status_label.bind(size=lambda lbl, size: setattr(lbl, "text_size", size))
        content.add_widget(self.status_label)

    def on_pre_enter(self, *_):
        Clock.schedule_once(lambda *_: self._start_camera(), 0)

    def on_leave(self, *_):
        self._stop_camera()

    def _build_camera_widget(self):
        try:
            widget = Camera(
                resolution=(1920, 1080),
                play=False,
                index=0
            )
        except Exception as exc:  # noqa: BLE001
            Logger.warning(f"CameraScanScreen: camera unavailable ({exc})")
            self._camera_available = False
            self.camera_widget = None
            fallback = AnchorLayout(size_hint=(1, None), height=dp(240))
            message = Label(
                text="Camera nu este disponibilă pe acest dispozitiv.",
                color=TEXT_SECONDARY,
                font_size=sp(16),
                halign="center",
                valign="middle"
            )
            message.bind(size=lambda lbl, size: setattr(lbl, "text_size", size))
            fallback.add_widget(message)
            return fallback
        else:
            widget.allow_stretch = True
            widget.keep_ratio = True
            self._camera_available = True
            self.camera_widget = widget
            frame = CameraFrame(widget, size_hint=(1, 1))
            return frame

    def _start_camera(self):
        if self._camera_available and self.camera_widget:
            self.camera_widget.play = True
            self.status_label.text = ""
            if hasattr(self, "capture_btn"):
                self.capture_btn.disabled = False

    def _stop_camera(self):
        if self._camera_available and self.camera_widget:
            self.camera_widget.play = False

    def _resolve_capture_directory(self) -> Path:
        """Pick a writable directory that survives on Android packaging."""
        app = App.get_running_app()

        if platform == "android":
            storage_root = None
            if callable(primary_external_storage_path):
                try:
                    storage_root = Path(primary_external_storage_path())
                except Exception:  # noqa: BLE001
                    storage_root = None
            if storage_root:
                # Use the shared Pictures directory so the user can find captures.
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
