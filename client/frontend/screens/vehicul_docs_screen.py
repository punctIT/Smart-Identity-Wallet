from .document_screen_base import BaseDocumentScreen

VEHICUL_DOCS_DESCRIPTION = (
    "[b]Documente Vehicul[/b]\n"
    "  • Talon auto și istoricul reviziilor\n"
    "  • Asigurări auto (RCA, CASCO)\n"
    "  • Programări sau rezultate ITP\n\n"
    "Păstrează într-un singur loc toate informațiile despre mașina ta pentru acces rapid."
)


class VehiculDocsScreen(BaseDocumentScreen):
    def __init__(self, server=None, **kwargs):
        super().__init__(
            name="vehicul_docs",
            title="Vehicul",
            description=VEHICUL_DOCS_DESCRIPTION,
            server=server,
            **kwargs,
        )


__all__ = ["VehiculDocsScreen"]
