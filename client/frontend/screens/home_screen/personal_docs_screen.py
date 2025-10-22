from frontend.screens.home_screen.document_screens_base import (
    BaseDocumentsScreen,
    DocumentCardTemplate,
)


class _PersonalDocumentCard(DocumentCardTemplate):
    """Slightly more compact variant for personal documents."""

    TITLE_SP = DocumentCardTemplate.TITLE_SP * 0.9
    SUBTITLE_SP = DocumentCardTemplate.SUBTITLE_SP * 0.9
    META_SP = DocumentCardTemplate.META_SP * 0.9


class PersonalDocsScreen(BaseDocumentsScreen):
    screen_name = "personal_docs"
    title_text = "Documente personale"
    subtitle_text = "Vizualizezi toate actele personale încărcate în portofel."
    empty_text = "Nu există documente personale momentan."
    document_categories = ("personal_docs", "personal", "identity")
    TITLE_SP = BaseDocumentsScreen.TITLE_SP * 0.9
    SUBTITLE_SP = BaseDocumentsScreen.SUBTITLE_SP * 0.9

    def _build_document_card(self, document: dict):
        card = _PersonalDocumentCard(
            title=self._extract_title(document),
            subtitle=self._extract_subtitle(document),
            meta_lines=self._extract_meta(document),
        )
        return self._wrap_row(card)


__all__ = ["PersonalDocsScreen"]
