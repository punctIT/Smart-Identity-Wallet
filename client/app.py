from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.uix.textinput import TextInput

from server_connect import ServerConnection


class MyApp(App):      
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.server = ServerConnection(size_hint_y=0.8)
        self.server.bind(last_message=self.on_message_update)
        Clock.schedule_once(lambda dt: self.server.connect(), 1)

        next_btn = Button(
            text='SEND',
            size_hint_y=0.2,
            font_size='18sp',
            background_color=(0.2, 0.6, 1, 1)
        )
        next_btn.bind(on_press=self.go_next)
        
        self.text_input = TextInput(
            text="",
            multiline=False, 
            font_size=18
        )

        layout.add_widget(self.server)
        layout.add_widget(self.text_input)
        layout.add_widget(next_btn)

        return layout

    def go_next(self, instance):
        self.server.send_specific_message("user_data",self.text_input.text)

    def on_message_update(self, instance, value):
        print("🟢 Eveniment (signal):", value)
        instance.text = value


if __name__ == "__main__":
    MyApp().run()
