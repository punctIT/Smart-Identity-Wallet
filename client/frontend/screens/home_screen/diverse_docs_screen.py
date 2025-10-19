from .document_screen_base import BaseDocumentScreen

DIVERSE_DOCS_DESCRIPTION = (
    "[b]Documente Diverse[/b]\n"
    "  • Legitimații de bibliotecă\n"
    "  • Adeverințe, certificate și alte documente personale\n"
    "  • Note și copii scanate\n\n"
    "Folosește această secțiune pentru documentele care nu se încadrează în celelalte categorii."
)


class DiverseDocsScreen(BaseDocumentScreen):
    def __init__(self, server=None, **kwargs):
        super().__init__(
            name="diverse_docs",
            title="Diverse",
            description=DIVERSE_DOCS_DESCRIPTION,
            server=server,
            **kwargs,
        )


__all__ = ["DiverseDocsScreen"]
