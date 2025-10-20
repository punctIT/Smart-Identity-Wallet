from kivy.uix.screenmanager import Screen

from frontend.screens.widgets.custom_buttons import CustomButton
from frontend.screens.widgets.custom_input import CustomInput
from frontend.screens.widgets.custom_label import CustomLabels
from frontend.screens.widgets.document_list import DocumentListMixin


class TransportDocsScreen(
    DocumentListMixin,
    Screen,
    CustomLabels,
    CustomButton,
    CustomInput,
):
    TITLE_TEXT = "Documente transport"
    SUBTITLE_TEXT = "Abonamentele și biletele active sunt afișate aici."
    EMPTY_TEXT = "Nu există documente de transport momentan."

    def __init__(self, server=None, **kwargs):
        Screen.__init__(self, name="transport_docs", **kwargs)
        self.setup_document_screen(
            server=server,
            title_text=self.TITLE_TEXT,
            subtitle_text=self.SUBTITLE_TEXT,
            empty_text=self.EMPTY_TEXT,
        )


__all__ = ["TransportDocsScreen"]
