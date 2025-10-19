from .document_screen_base import BaseDocumentScreen

TRANSPORT_DOCS_DESCRIPTION = (
    "[b]Documente Transport[/b]\n"
    "  • Abonamente integrate pentru transport public\n"
    "  • Bilete și chitanțe electronice\n"
    "  • Istoric călătorii\n\n"
    "Organizează cardurile și abonamentele de transport pentru a le prezenta ușor la control."
)


class TransportDocsScreen(BaseDocumentScreen):
    def __init__(self, server=None, **kwargs):
        super().__init__(
            name="transport_docs",
            title="Transport",
            description=TRANSPORT_DOCS_DESCRIPTION,
            server=server,
            **kwargs,
        )


__all__ = ["TransportDocsScreen"]
