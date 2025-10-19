from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget




class BaseDocumentScreen(Screen):
    def __init__(self, *, name: str, title: str, description: str, server=None, **kwargs):
        pass