"""Schémas Pydantic pour l'endpoint /predict."""

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """Données d'entrée pour la prédiction de rendement."""

    Area: str = Field(..., min_length=1, description="Pays")
    Item: str = Field(..., min_length=1, description="Culture")
    Year: int = Field(..., ge=1900, le=2100, description="Année")
    average_rain_fall_mm_per_year: float = Field(
        ..., description="Précipitations moyennes (mm/an)"
    )
    pesticides_tonnes: float = Field(
        ..., description="Usage de pesticides (tonnes)"
    )
    avg_temp: float = Field(
        ..., ge=-50, le=60, description="Température moyenne (°C)"
    )


class PredictResponse(BaseModel):
    """Résultat de la prédiction de rendement."""

    culture: str
    pays: str
    rendement_hg_ha: float
    rendement_t_ha: float
