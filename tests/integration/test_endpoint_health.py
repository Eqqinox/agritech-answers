"""Tests d'intégration pour les endpoints /health et /metadata."""

import pytest


class TestHealth:
    def test_health_nominal(self, client_mock):
        response = client_mock.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"
        assert "modele" in data


class TestMetadata:
    def test_metadata_nominal(self, client_mock):
        response = client_mock.get("/metadata")
        assert response.status_code == 200
        data = response.json()
        assert len(data["cultures_disponibles"]) == 10
        assert len(data["pays_disponibles"]) == 100
        assert "annees_train" in data
        assert "cultures_pays_autorises" in data

    @pytest.mark.local
    def test_metadata_real(self, client_real):
        response = client_real.get("/metadata")
        assert response.status_code == 200
        data = response.json()
        assert len(data["cultures_disponibles"]) == 10
        assert len(data["pays_disponibles"]) == 100
