"""Router pour l'endpoint de recommandation."""

from fastapi import APIRouter, Request

from src.api.schemas.recommend import RecommendRequest, RecommendResponse
from src.api.services import prediction as prediction_service

router = APIRouter()


@router.post("/recommend", response_model=RecommendResponse)
def recommend(request_data: RecommendRequest, request: Request):
    """Simule le rendement pour toutes les cultures et retourne un classement."""
    résultat = prediction_service.recommend(
        pipeline=request.app.state.pipeline,
        metadata=request.app.state.metadata,
        area=request_data.Area,
        year=request_data.Year,
        average_rain_fall_mm_per_year=request_data.average_rain_fall_mm_per_year,
        pesticides_tonnes=request_data.pesticides_tonnes,
        avg_temp=request_data.avg_temp,
        prix_par_tonne=request_data.prix_par_tonne,
    )
    return RecommendResponse(**résultat)
