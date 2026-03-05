"""Tests d'intégration pour l'endpoint POST /recommend."""

import pytest


VALID_PAYLOAD = {
    "Area": "France",
    "Year": 2010,
    "average_rain_fall_mm_per_year": 800.0,
    "pesticides_tonnes": 100.0,
    "avg_temp": 15.0,
}


class TestRecommendMock:
    """Tests avec modèle mocké."""

    def test_nominal_sans_prix(self, client_mock):
        response = client_mock.post("/recommend", json=VALID_PAYLOAD)
        assert response.status_code == 200
        data = response.json()
        assert data["pays"] == "France"
        classement = data["classement"]
        assert len(classement) > 0
        # Vérifie le tri décroissant
        rendements = [c["rendement_t_ha"] for c in classement]
        assert rendements == sorted(rendements, reverse=True)

    def test_nominal_avec_prix(self, client_mock):
        payload = {**VALID_PAYLOAD, "prix_par_tonne": 200.0}
        response = client_mock.post("/recommend", json=payload)
        assert response.status_code == 200
        data = response.json()
        classement = data["classement"]
        for item in classement:
            assert item["revenu_estime"] is not None
        # Vérifie le tri décroissant par revenu
        revenus = [c["revenu_estime"] for c in classement]
        assert revenus == sorted(revenus, reverse=True)

    def test_filtrage_cultures(self, client_mock):
        """Vérifie que seules les cultures autorisées pour le pays sont retournées."""
        payload = {**VALID_PAYLOAD, "Area": "Estonia"}
        response = client_mock.post("/recommend", json=payload)
        assert response.status_code == 200
        classement = response.json()["classement"]
        cultures = {c["culture"] for c in classement}
        # Estonia : Maize, Potatoes, Wheat dans le mock
        assert cultures == {"Maize", "Potatoes", "Wheat"}

    def test_pays_inconnu(self, client_mock):
        payload = {**VALID_PAYLOAD, "Area": "Narnia"}
        response = client_mock.post("/recommend", json=payload)
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_valeur_negative(self, client_mock):
        payload = {**VALID_PAYLOAD, "average_rain_fall_mm_per_year": -5}
        response = client_mock.post("/recommend", json=payload)
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_prix_negatif(self, client_mock):
        payload = {**VALID_PAYLOAD, "prix_par_tonne": -50}
        response = client_mock.post("/recommend", json=payload)
        assert response.status_code == 422


class TestRecommendReal:
    """Tests avec le vrai modèle (local uniquement)."""

    @pytest.mark.local
    def test_nominal(self, client_real):
        response = client_real.post("/recommend", json=VALID_PAYLOAD)
        assert response.status_code == 200
        data = response.json()
        classement = data["classement"]
        assert len(classement) > 0
        # Vérifie le tri décroissant
        rendements = [c["rendement_t_ha"] for c in classement]
        assert rendements == sorted(rendements, reverse=True)
