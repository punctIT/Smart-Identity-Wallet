from .document_screen_base import BaseDocumentScreen

PERSONAL_DOCS_DESCRIPTION = (
    "[b]Documente Personale[/b]\n"
    "  • Carte de Identitate (CI)\n"
    "  • Permis de Conducere\n"
    "  • Asigurare Răspundere Civilă Auto (RCA)\n\n"
    "Stochează și accesează rapid documentele esențiale de identitate și cele asociate permisului."
)


class PersonalDocsScreen(BaseDocumentScreen):
    def __init__(self, server=None, **kwargs):
        super().__init__(
            name="personal_docs",
            title="Personal Docs",
            description=PERSONAL_DOCS_DESCRIPTION,
            server=server,
            **kwargs,
        )


__all__ = ["PersonalDocsScreen"]
