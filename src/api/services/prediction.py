"""Logique métier pour la prédiction et la recommandation de rendement agricole.

Ce module est indépendant du framework FastAPI.
Il ne connaît ni HTTP, ni les codes de statut, ni les schémas Pydantic.
Il lève ses propres exceptions métier en cas d'erreur.
"""

from typing import Optional

import numpy as np
import pandas as pd

from src.api.exceptions import (
    CultureInconnue,
    ModeleNonCharge,
    PaysInconnu,
    ValeurNegative,
)


def _vérifier_modèle(pipeline, metadata) -> None:
    """Vérifie que le pipeline et les métadonnées sont chargés."""
    if pipeline is None:
        raise ModeleNonCharge(
            "Le pipeline de prédiction n'est pas chargé en mémoire."
        )
    if metadata is None:
        raise ModeleNonCharge(
            "Les métadonnées du modèle ne sont pas chargées en mémoire."
        )


def _valider_règles_métier(
    average_rain_fall_mm_per_year: float,
    pesticides_tonnes: float,
    prix_par_tonne: Optional[float] = None,
) -> None:
    """Valide les règles métier sur les valeurs numériques."""
    erreurs = []
    if average_rain_fall_mm_per_year < 0:
        erreurs.append("average_rain_fall_mm_per_year ne peut pas être négatif.")
    if pesticides_tonnes < 0:
        erreurs.append("pesticides_tonnes ne peut pas être négatif.")
    if prix_par_tonne is not None and prix_par_tonne < 0:
        erreurs.append("prix_par_tonne ne peut pas être négatif.")
    if erreurs:
        raise ValeurNegative(" ".join(erreurs))


def predict(
    pipeline,
    metadata: dict,
    area: str,
    item: str,
    year: int,
    average_rain_fall_mm_per_year: float,
    pesticides_tonnes: float,
    avg_temp: float,
) -> dict:
    """Prédit le rendement pour une culture et un contexte donnés.

    Retourne un dictionnaire avec les clés :
    culture, pays, rendement_hg_ha, rendement_t_ha.
    """
    _vérifier_modèle(pipeline, metadata)
    _valider_règles_métier(average_rain_fall_mm_per_year, pesticides_tonnes)

    if area not in metadata["pays_disponibles"]:
        raise PaysInconnu(f"Pays inconnu : {area}")
    if item not in metadata["cultures_disponibles"]:
        raise CultureInconnue(f"Culture inconnue : {item}")

    df = pd.DataFrame([{
        "Area": area,
        "Item": item,
        "Year": year,
        "average_rain_fall_mm_per_year": average_rain_fall_mm_per_year,
        "pesticides_tonnes": pesticides_tonnes,
        "avg_temp": avg_temp,
    }])

    prediction_log = pipeline.predict(df)[0]
    rendement_hg_ha = float(np.expm1(prediction_log))
    rendement_t_ha = round(rendement_hg_ha / 10_000, 4)

    return {
        "culture": item,
        "pays": area,
        "rendement_hg_ha": round(rendement_hg_ha, 2),
        "rendement_t_ha": rendement_t_ha,
    }


def recommend(
    pipeline,
    metadata: dict,
    area: str,
    year: int,
    average_rain_fall_mm_per_year: float,
    pesticides_tonnes: float,
    avg_temp: float,
    prix_par_tonne: Optional[float] = None,
) -> dict:
    """Simule le rendement pour toutes les cultures et retourne un classement.

    Retourne un dictionnaire avec les clés :
    pays, classement (liste triée par rendement ou revenu estimé).
    """
    _vérifier_modèle(pipeline, metadata)
    _valider_règles_métier(
        average_rain_fall_mm_per_year, pesticides_tonnes, prix_par_tonne
    )

    if area not in metadata["pays_disponibles"]:
        raise PaysInconnu(f"Pays inconnu : {area}")

    cultures = metadata["cultures_disponibles"]

    rows = [
        {
            "Area": area,
            "Item": culture,
            "Year": year,
            "average_rain_fall_mm_per_year": average_rain_fall_mm_per_year,
            "pesticides_tonnes": pesticides_tonnes,
            "avg_temp": avg_temp,
        }
        for culture in cultures
    ]
    df = pd.DataFrame(rows)

    predictions_log = pipeline.predict(df)
    rendements_hg_ha = np.expm1(predictions_log)

    classement = []
    for culture, rendement in zip(cultures, rendements_hg_ha):
        rendement_hg = float(rendement)
        rendement_t = round(rendement_hg / 10_000, 4)
        item = {
            "culture": culture,
            "rendement_hg_ha": round(rendement_hg, 2),
            "rendement_t_ha": rendement_t,
        }
        if prix_par_tonne is not None:
            item["revenu_estime"] = round(rendement_t * prix_par_tonne, 2)
        classement.append(item)

    if prix_par_tonne is not None:
        classement.sort(key=lambda x: x["revenu_estime"], reverse=True)
    else:
        classement.sort(key=lambda x: x["rendement_hg_ha"], reverse=True)

    return {
        "pays": area,
        "classement": classement,
    }
