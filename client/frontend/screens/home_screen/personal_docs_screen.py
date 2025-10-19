from kivy.uix.screenmanager import Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.graphics.texture import Texture
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.metrics import dp, sp 


from frontend.screens.widgets.custom_background import GradientBackground
from frontend.screens.widgets.custom_buttons import CustomButton
from frontend.screens.widgets.custom_input import CustomInput
from frontend.screens.widgets.custom_label import CustomLabels,LinkLabel 
from frontend.screens.widgets.custom_alignment import Alignment




class PersonalDocsScreen(Screen,CustomLabels,CustomButton,CustomInput,Alignment):
    def __init__(self, server=None, **kwargs):
        super().__init__(name='personal_docs', **kwargs)
        self.server = server

        # Background gradient
        self.bg = GradientBackground()
        self.add_widget(self.bg)