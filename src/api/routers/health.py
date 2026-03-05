"""Router pour les endpoints de santé et de métadonnées."""

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


@router.get("/metadata")
def metadata(request: Request):
    """Retourne les listes de pays et cultures disponibles pour le front-end."""
    if not hasattr(request.app.state, "metadata") or request.app.state.metadata is None:
        raise ModeleNonCharge("Les métadonnées ne sont pas chargées.")
    meta = request.app.state.metadata
    return {
        "cultures_disponibles": meta["cultures_disponibles"],
        "pays_disponibles": meta["pays_disponibles"],
        "annees_train": meta["annees_train"],
        "cultures_pays_autorises": request.app.state.cultures_pays,
    }
