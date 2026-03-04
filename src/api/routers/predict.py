"""Router pour l'endpoint de prédiction."""

from fastapi import APIRouter, Request

from src.api.schemas.predict import PredictRequest, PredictResponse
from src.api.services import prediction as prediction_service

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict(request_data: PredictRequest, request: Request):
    """Prédit le rendement pour une culture et un contexte donnés."""
    résultat = prediction_service.predict(
        pipeline=request.app.state.pipeline,
        metadata=request.app.state.metadata,
        area=request_data.Area,
        item=request_data.Item,
        year=request_data.Year,
        average_rain_fall_mm_per_year=request_data.average_rain_fall_mm_per_year,
        pesticides_tonnes=request_data.pesticides_tonnes,
        avg_temp=request_data.avg_temp,
    )
    return PredictResponse(**résultat)
