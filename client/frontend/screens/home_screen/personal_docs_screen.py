from frontend.screens.home_screen.document_screens_base import BaseDocumentsScreen


class PersonalDocsScreen(BaseDocumentsScreen):
    screen_name = "personal_docs"
    title_text = "Documente personale"
    subtitle_text = "Vizualizezi toate actele personale încărcate în portofel."
    empty_text = "Nu există documente personale momentan."
    document_categories = ("personal_docs", "personal", "identity")


__all__ = ["PersonalDocsScreen"]
