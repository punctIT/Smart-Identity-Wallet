import os

os.environ.setdefault("KIVY_CLIPBOARD", "sdl2")

from frontend.app import SmartIdApp

if __name__ == "__main__":
    SmartIdApp().run()
