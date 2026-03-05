"""Point d'entrée de l'API Agritech Answers.

Ce module gère :
- Le chargement du modèle au démarrage (lifespan)
- L'inclusion des routers
- La traduction des exceptions métier en réponses HTTP
"""

import json
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.config import get_settings
from src.api.exceptions import (
    CultureInconnue,
    ModeleNonCharge,
    PaysInconnu,
    ValeurNegative,
)
from src.api.routers import health, predict, recommend


# --- Chargement au démarrage (lifespan) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Charge le pipeline et les métadonnées une seule fois au démarrage."""
    settings = get_settings()
    app.state.pipeline = joblib.load(settings.model_pipeline_path)
    with open(settings.model_metadata_path, "r") as f:
        app.state.metadata = json.load(f)
    with open(settings.cultures_pays_path, "r") as f:
        app.state.cultures_pays = json.load(f)
    yield


app = FastAPI(
    title="Agritech Answers API",
    description="API de prédiction et de recommandation de rendement agricole.",
    version="1.0.0",
    lifespan=lifespan,
)


# --- Inclusion des routers ---

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(recommend.router)


# --- Traduction des exceptions métier en réponses HTTP ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """422 — Échec de validation Pydantic (mauvais types, champs manquants)."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "message": "Données invalides."},
    )


@app.exception_handler(ValeurNegative)
async def valeur_negative_handler(request: Request, exc: ValeurNegative):
    """400 — Valeur négative détectée sur un champ métier."""
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message},
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """400 — Erreur de valeur lors de la prédiction."""
    return JSONResponse(
        status_code=400,
        content={"detail": f"Erreur lors de la prédiction : {exc}"},
    )


@app.exception_handler(CultureInconnue)
async def culture_inconnue_handler(request: Request, exc: CultureInconnue):
    """422 — Culture non référencée dans le modèle."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.message},
    )


@app.exception_handler(PaysInconnu)
async def pays_inconnu_handler(request: Request, exc: PaysInconnu):
    """422 — Pays non référencé dans le modèle."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.message},
    )


@app.exception_handler(ModeleNonCharge)
async def modele_non_charge_handler(request: Request, exc: ModeleNonCharge):
    """503 — Le modèle n'est pas chargé en mémoire."""
    return JSONResponse(
        status_code=503,
        content={"detail": exc.message},
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404 — Route inexistante."""
    return JSONResponse(
        status_code=404,
        content={"detail": f"Route {request.url.path} introuvable."},
    )


@app.exception_handler(Exception)
async def internal_error_handler(request: Request, exc: Exception):
    """500 — Erreur interne non anticipée."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur."},
    )
