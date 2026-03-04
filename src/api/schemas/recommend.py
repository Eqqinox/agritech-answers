"""Schémas Pydantic pour l'endpoint /recommend."""

from typing import Optional

from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    """Données d'entrée pour la recommandation de cultures."""

    Area: str = Field(..., min_length=1, description="Pays")
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
    prix_par_tonne: Optional[float] = Field(
        None, description="Prix par tonne (optionnel, pour estimation du revenu)"
    )


class RecommendItem(BaseModel):
    """Détail d'une culture dans le classement de recommandation."""

    culture: str
    rendement_hg_ha: float
    rendement_t_ha: float
    revenu_estime: Optional[float] = None


class RecommendResponse(BaseModel):
    """Résultat de la recommandation : classement des cultures."""

    pays: str
    classement: list[RecommendItem]
