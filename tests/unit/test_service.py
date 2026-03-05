"""Tests unitaires pour la couche service (logique métier)."""

import numpy as np
import pytest

from src.api.exceptions import (
    CultureInconnue,
    ModeleNonCharge,
    PaysInconnu,
    ValeurNegative,
)
from src.api.services.prediction import predict, recommend


# ---------------------------------------------------------------------------
# Données de référence
# ---------------------------------------------------------------------------

VALID_ARGS = {
    "area": "France",
    "item": "Wheat",
    "year": 2010,
    "average_rain_fall_mm_per_year": 800.0,
    "pesticides_tonnes": 100.0,
    "avg_temp": 15.0,
}

VALID_RECO_ARGS = {
    "area": "France",
    "year": 2010,
    "average_rain_fall_mm_per_year": 800.0,
    "pesticides_tonnes": 100.0,
    "avg_temp": 15.0,
}


# ---------------------------------------------------------------------------
# predict()
# ---------------------------------------------------------------------------

class TestPredict:
    """Tests de la fonction predict()."""

    def test_nominal(self, mock_pipeline, mock_metadata):
        résultat = predict(
            pipeline=mock_pipeline, metadata=mock_metadata, **VALID_ARGS,
        )
        expected_hg = float(np.expm1(9.5))
        assert résultat["rendement_hg_ha"] == round(expected_hg, 2)
        assert résultat["rendement_t_ha"] == round(expected_hg / 10_000, 4)
        assert résultat["culture"] == "Wheat"
        assert résultat["pays"] == "France"

    def test_culture_inconnue(self, mock_pipeline, mock_metadata):
        with pytest.raises(CultureInconnue):
            predict(
                pipeline=mock_pipeline, metadata=mock_metadata,
                **{**VALID_ARGS, "item": "Fraises"},
            )

    def test_pays_inconnu(self, mock_pipeline, mock_metadata):
        with pytest.raises(PaysInconnu):
            predict(
                pipeline=mock_pipeline, metadata=mock_metadata,
                **{**VALID_ARGS, "area": "Narnia"},
            )

    def test_rainfall_negatif(self, mock_pipeline, mock_metadata):
        with pytest.raises(ValeurNegative):
            predict(
                pipeline=mock_pipeline, metadata=mock_metadata,
                **{**VALID_ARGS, "average_rain_fall_mm_per_year": -1},
            )

    def test_pesticides_negatif(self, mock_pipeline, mock_metadata):
        with pytest.raises(ValeurNegative):
            predict(
                pipeline=mock_pipeline, metadata=mock_metadata,
                **{**VALID_ARGS, "pesticides_tonnes": -0.5},
            )

    def test_modele_non_charge(self, mock_metadata):
        with pytest.raises(ModeleNonCharge):
            predict(
                pipeline=None, metadata=mock_metadata, **VALID_ARGS,
            )


# ---------------------------------------------------------------------------
# recommend()
# ---------------------------------------------------------------------------

class TestRecommend:
    """Tests de la fonction recommend()."""

    def test_nominal_sans_prix(self, mock_pipeline_multi, mock_metadata, mock_cultures_pays):
        résultat = recommend(
            pipeline=mock_pipeline_multi, metadata=mock_metadata,
            cultures_pays=mock_cultures_pays, **VALID_RECO_ARGS,
        )
        assert résultat["pays"] == "France"
        classement = résultat["classement"]
        assert len(classement) > 0
        # Vérifie le tri décroissant par rendement
        rendements = [c["rendement_hg_ha"] for c in classement]
        assert rendements == sorted(rendements, reverse=True)
        # Vérifie que revenu_estime est absent
        for item in classement:
            assert "revenu_estime" not in item or item.get("revenu_estime") is None

    def test_nominal_avec_prix(self, mock_pipeline_multi, mock_metadata, mock_cultures_pays):
        résultat = recommend(
            pipeline=mock_pipeline_multi, metadata=mock_metadata,
            cultures_pays=mock_cultures_pays,
            **{**VALID_RECO_ARGS, "prix_par_tonne": 200.0},
        )
        classement = résultat["classement"]
        # Vérifie que revenu_estime est présent
        for item in classement:
            assert "revenu_estime" in item
            assert item["revenu_estime"] is not None
        # Vérifie le tri décroissant par revenu
        revenus = [c["revenu_estime"] for c in classement]
        assert revenus == sorted(revenus, reverse=True)

    def test_filtrage_cultures_pays(self, mock_pipeline_multi, mock_metadata, mock_cultures_pays):
        """Vérifie que seules les cultures autorisées pour le pays sont retournées."""
        résultat = recommend(
            pipeline=mock_pipeline_multi, metadata=mock_metadata,
            cultures_pays=mock_cultures_pays,
            area="Estonia", year=2010,
            average_rain_fall_mm_per_year=600.0, pesticides_tonnes=50.0, avg_temp=10.0,
        )
        classement = résultat["classement"]
        cultures_retournées = [c["culture"] for c in classement]
        # Estonia n'est autorisée que pour Maize, Potatoes, Wheat dans le mock
        cultures_attendues = {"Maize", "Potatoes", "Wheat"}
        assert set(cultures_retournées) == cultures_attendues

    def test_aucune_culture_disponible(self, mock_pipeline_multi, mock_metadata, mock_cultures_pays):
        """Vérifie qu'un pays sans aucune culture autorisée lève PaysInconnu."""
        # Bahrain n'est dans aucune liste du mock cultures_pays
        with pytest.raises(PaysInconnu, match="Aucune culture référencée"):
            recommend(
                pipeline=mock_pipeline_multi, metadata=mock_metadata,
                cultures_pays=mock_cultures_pays,
                area="Bahrain", year=2010,
                average_rain_fall_mm_per_year=100.0, pesticides_tonnes=10.0, avg_temp=25.0,
            )

    def test_pays_inconnu(self, mock_pipeline_multi, mock_metadata, mock_cultures_pays):
        with pytest.raises(PaysInconnu):
            recommend(
                pipeline=mock_pipeline_multi, metadata=mock_metadata,
                cultures_pays=mock_cultures_pays,
                **{**VALID_RECO_ARGS, "area": "Narnia"},
            )

    def test_rainfall_negatif(self, mock_pipeline_multi, mock_metadata, mock_cultures_pays):
        with pytest.raises(ValeurNegative):
            recommend(
                pipeline=mock_pipeline_multi, metadata=mock_metadata,
                cultures_pays=mock_cultures_pays,
                **{**VALID_RECO_ARGS, "average_rain_fall_mm_per_year": -5},
            )

    def test_tri_decroissant(self, mock_pipeline_multi, mock_metadata, mock_cultures_pays):
        """Vérifie que l'ordre du classement est strictement décroissant."""
        résultat = recommend(
            pipeline=mock_pipeline_multi, metadata=mock_metadata,
            cultures_pays=mock_cultures_pays, **VALID_RECO_ARGS,
        )
        rendements = [c["rendement_hg_ha"] for c in résultat["classement"]]
        for i in range(len(rendements) - 1):
            assert rendements[i] >= rendements[i + 1]
