from kivy.uix.screenmanager import Screen

from frontend.screens.widgets.add_document_card_mixin import AddDocumentCardMixin
from frontend.screens.widgets.custom_buttons import CustomButton
from frontend.screens.widgets.custom_input import CustomInput
from frontend.screens.widgets.custom_label import CustomLabels
from frontend.screens.widgets.document_list import DocumentListMixin


class PersonalDocsScreen(
    AddDocumentCardMixin,
    DocumentListMixin,
    Screen,
    CustomLabels,
    CustomButton,
    CustomInput,
):
    TITLE_TEXT = "Documente personale"
    SUBTITLE_TEXT = "Vizualizezi toate actele personale încărcate în portofel."
    EMPTY_TEXT = "Nu există documente personale momentan."

    def __init__(self, server=None, **kwargs):
        Screen.__init__(self, name="personal_docs", **kwargs)
        self.setup_document_screen(
            server=server,
            title_text=self.TITLE_TEXT,
            subtitle_text=self.SUBTITLE_TEXT,
            empty_text=self.EMPTY_TEXT,
        )


__all__ = ["PersonalDocsScreen"]
