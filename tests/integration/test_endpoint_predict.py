"""Tests d'intégration pour l'endpoint POST /predict."""

import pytest


VALID_PAYLOAD = {
    "Area": "France",
    "Item": "Wheat",
    "Year": 2010,
    "average_rain_fall_mm_per_year": 800.0,
    "pesticides_tonnes": 100.0,
    "avg_temp": 15.0,
}


class TestPredictMock:
    """Tests avec modèle mocké."""

    def test_nominal(self, client_mock):
        response = client_mock.post("/predict", json=VALID_PAYLOAD)
        assert response.status_code == 200
        data = response.json()
        assert data["rendement_hg_ha"] > 0
        assert "rendement_t_ha" in data
        assert data["culture"] == "Wheat"
        assert data["pays"] == "France"

    def test_culture_inconnue(self, client_mock):
        payload = {**VALID_PAYLOAD, "Item": "Fraises"}
        response = client_mock.post("/predict", json=payload)
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_pays_inconnu(self, client_mock):
        payload = {**VALID_PAYLOAD, "Area": "Narnia"}
        response = client_mock.post("/predict", json=payload)
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_valeur_negative(self, client_mock):
        payload = {**VALID_PAYLOAD, "pesticides_tonnes": -1}
        response = client_mock.post("/predict", json=payload)
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_champ_manquant(self, client_mock):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "Item"}
        response = client_mock.post("/predict", json=payload)
        assert response.status_code == 422

    def test_type_incorrect(self, client_mock):
        payload = {**VALID_PAYLOAD, "Year": "abc"}
        response = client_mock.post("/predict", json=payload)
        assert response.status_code == 422

    def test_route_inexistante(self, client_mock):
        response = client_mock.post("/predikt", json=VALID_PAYLOAD)
        assert response.status_code == 404


class TestPredictReal:
    """Tests avec le vrai modèle (local uniquement)."""

    @pytest.mark.local
    def test_nominal(self, client_real):
        response = client_real.post("/predict", json=VALID_PAYLOAD)
        assert response.status_code == 200
        data = response.json()
        assert data["rendement_hg_ha"] > 0
        assert data["rendement_t_ha"] > 0
        assert data["culture"] == "Wheat"
        assert data["pays"] == "France"
