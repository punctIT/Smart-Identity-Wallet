from frontend.screens.home_screen.document_screens_base import BaseDocumentsScreen


class TransportDocsScreen(BaseDocumentsScreen):
    screen_name = "transport_docs"
    title_text = "Documente transport"
    subtitle_text = "Abonamentele și biletele active sunt afișate aici."
    empty_text = "Nu există documente de transport momentan."
    document_categories = ("transport_docs", "transport", "transit")
    require_category_match = True


__all__ = ["TransportDocsScreen"]
