from frontend.screens.home_screen.document_screens_base import BaseDocumentsScreen


class VehiculDocsScreen(BaseDocumentsScreen):
    screen_name = "vehicul_docs"
    title_text = "Documente vehicul"
    subtitle_text = "Vizualizezi asigurările, ITP-ul și talonul vehiculului."
    empty_text = "Nu există documente asociate vehiculului momentan."
    document_categories = ("vehicul_docs", "vehicul", "vehicle")
    require_category_match = True


__all__ = ["VehiculDocsScreen"]
