"""Tests unitaires pour les schémas Pydantic."""

import pytest
from pydantic import ValidationError

from src.api.schemas.predict import PredictRequest, PredictResponse
from src.api.schemas.recommend import RecommendRequest, RecommendItem, RecommendResponse


# ---------------------------------------------------------------------------
# Données valides de référence
# ---------------------------------------------------------------------------

VALID_PREDICT = {
    "Area": "France",
    "Item": "Wheat",
    "Year": 2010,
    "average_rain_fall_mm_per_year": 800.0,
    "pesticides_tonnes": 100.0,
    "avg_temp": 15.0,
}

VALID_RECOMMEND = {
    "Area": "France",
    "Year": 2010,
    "average_rain_fall_mm_per_year": 800.0,
    "pesticides_tonnes": 100.0,
    "avg_temp": 15.0,
}


# ---------------------------------------------------------------------------
# PredictRequest
# ---------------------------------------------------------------------------

class TestPredictRequest:
    """Tests de validation pour PredictRequest."""

    def test_nominal(self):
        req = PredictRequest(**VALID_PREDICT)
        assert req.Area == "France"
        assert req.Item == "Wheat"

    def test_year_borne_basse(self):
        with pytest.raises(ValidationError):
            PredictRequest(**{**VALID_PREDICT, "Year": 1899})

    def test_year_borne_haute(self):
        with pytest.raises(ValidationError):
            PredictRequest(**{**VALID_PREDICT, "Year": 2101})

    def test_avg_temp_borne_basse(self):
        with pytest.raises(ValidationError):
            PredictRequest(**{**VALID_PREDICT, "avg_temp": -51})

    def test_avg_temp_borne_haute(self):
        with pytest.raises(ValidationError):
            PredictRequest(**{**VALID_PREDICT, "avg_temp": 61})

    def test_area_vide(self):
        with pytest.raises(ValidationError):
            PredictRequest(**{**VALID_PREDICT, "Area": ""})

    def test_item_manquant(self):
        data = {k: v for k, v in VALID_PREDICT.items() if k != "Item"}
        with pytest.raises(ValidationError):
            PredictRequest(**data)

    def test_year_type_incorrect(self):
        with pytest.raises(ValidationError):
            PredictRequest(**{**VALID_PREDICT, "Year": "abc"})


# ---------------------------------------------------------------------------
# RecommendRequest
# ---------------------------------------------------------------------------

class TestRecommendRequest:
    """Tests de validation pour RecommendRequest."""

    def test_nominal(self):
        req = RecommendRequest(**VALID_RECOMMEND)
        assert req.Area == "France"
        assert req.prix_par_tonne is None

    def test_prix_par_tonne_absent(self):
        req = RecommendRequest(**VALID_RECOMMEND)
        assert req.prix_par_tonne is None

    def test_prix_par_tonne_valide(self):
        req = RecommendRequest(**{**VALID_RECOMMEND, "prix_par_tonne": 200.0})
        assert req.prix_par_tonne == 200.0

    def test_prix_par_tonne_negatif(self):
        with pytest.raises(ValidationError):
            RecommendRequest(**{**VALID_RECOMMEND, "prix_par_tonne": -10})

    def test_year_borne_basse(self):
        with pytest.raises(ValidationError):
            RecommendRequest(**{**VALID_RECOMMEND, "Year": 1899})

    def test_year_borne_haute(self):
        with pytest.raises(ValidationError):
            RecommendRequest(**{**VALID_RECOMMEND, "Year": 2101})

    def test_area_vide(self):
        with pytest.raises(ValidationError):
            RecommendRequest(**{**VALID_RECOMMEND, "Area": ""})


# ---------------------------------------------------------------------------
# PredictResponse / RecommendResponse
# ---------------------------------------------------------------------------

class TestResponses:
    """Tests de validation pour les schémas de réponse."""

    def test_predict_response(self):
        resp = PredictResponse(
            culture="Wheat", pays="France",
            rendement_hg_ha=50000.0, rendement_t_ha=5.0,
        )
        assert resp.culture == "Wheat"

    def test_recommend_item(self):
        item = RecommendItem(
            culture="Wheat", rendement_hg_ha=50000.0, rendement_t_ha=5.0,
        )
        assert item.revenu_estime is None

    def test_recommend_item_avec_revenu(self):
        item = RecommendItem(
            culture="Wheat", rendement_hg_ha=50000.0,
            rendement_t_ha=5.0, revenu_estime=1000.0,
        )
        assert item.revenu_estime == 1000.0
