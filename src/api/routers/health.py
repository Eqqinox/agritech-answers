"""Router pour l'endpoint de vérification de santé."""

from fastapi import APIRouter, Request

from src.api.exceptions import ModeleNonCharge

router = APIRouter()


@router.get("/health")
def health(request: Request):
    """Vérifie que l'API est opérationnelle et que le modèle est chargé."""
    if not hasattr(request.app.state, "metadata") or request.app.state.metadata is None:
        raise ModeleNonCharge("Les métadonnées ne sont pas chargées.")
    return {
        "status": "ok",
        "modele": request.app.state.metadata["modele_champion"],
    }
