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
        self._load_documents()

    def on_pre_enter(self, *args):
        Screen.on_pre_enter(self, *args)
        self._load_documents()

    def _load_documents(self):
        """Fetch wallet data and populate the list of personal documents."""
        documents = []
        if getattr(self, "server", None):
            response = self.server.get_specific_data("GetWalletCards")
            if response and response.get("success"):
                data = response.get("data") or {}
                cards = data.get("cards") or data.get("documents") or []
                if isinstance(cards, dict):
                    cards = list(cards.values())
                if isinstance(cards, list):
                    documents = cards
            if not documents and hasattr(self.server, "_MOCK_WALLET_CARDS"):
                documents = list(self.server._MOCK_WALLET_CARDS)
        else:
            from server_requests.data_requester import DataRequester

            documents = list(getattr(DataRequester, "_MOCK_WALLET_CARDS", []))
        self.set_documents(documents)


__all__ = ["PersonalDocsScreen"]
