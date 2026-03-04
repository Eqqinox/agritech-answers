"""Exceptions métier de l'API Agritech Answers."""


class AgritechException(Exception):
    """Exception de base pour l'API Agritech."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class CultureInconnue(AgritechException):
    """Culture non référencée dans le modèle."""


class PaysInconnu(AgritechException):
    """Pays non référencé dans le modèle."""


class ValeurNegative(AgritechException):
    """Valeur négative détectée sur un champ qui ne le permet pas."""


class ModeleNonCharge(AgritechException):
    """Le modèle ou les métadonnées ne sont pas chargés en mémoire."""
