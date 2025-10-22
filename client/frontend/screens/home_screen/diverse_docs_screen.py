from frontend.screens.home_screen.document_screens_base import BaseDocumentsScreen


class DiverseDocsScreen(BaseDocumentsScreen):
    screen_name = "diverse_docs"
    title_text = "Documente diverse"
    subtitle_text = "Aici găsești restul documentelor digitale salvate."
    empty_text = "Nu există documente diverse momentan."
    document_categories = ("diverse_docs", "diverse", "other")
    require_category_match = True


__all__ = ["DiverseDocsScreen"]
