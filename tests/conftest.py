"""Fixtures partagées pour les tests de l'API Agritech Answers."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest
from fastapi.testclient import TestClient

from src.api.main import app


# ---------------------------------------------------------------------------
# Données de référence pour les mocks
# ---------------------------------------------------------------------------

CULTURES = [
    "Cassava", "Maize", "Plantains and others", "Potatoes",
    "Rice, paddy", "Sorghum", "Soybeans", "Sweet potatoes",
    "Wheat", "Yams",
]

PAYS = [
    "Albania", "Algeria", "Angola", "Argentina", "Armenia",
    "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain",
    "Bangladesh", "Belarus", "Belgium", "Botswana", "Brazil",
    "Bulgaria", "Burkina Faso", "Burundi", "Cameroon", "Canada",
    "Central African Republic", "Chile", "Colombia", "Croatia", "Denmark",
    "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Eritrea",
    "Estonia", "Finland", "France", "Germany", "Ghana",
    "Greece", "Guatemala", "Guinea", "Guyana", "Haiti",
    "Honduras", "Hungary", "India", "Indonesia", "Iraq",
    "Ireland", "Italy", "Jamaica", "Japan", "Kazakhstan",
    "Kenya", "Latvia", "Lebanon", "Lesotho", "Libya",
    "Lithuania", "Madagascar", "Malawi", "Malaysia", "Mali",
    "Mauritania", "Mauritius", "Mexico", "Montenegro", "Morocco",
    "Mozambique", "Namibia", "Nepal", "Netherlands", "New Zealand",
    "Nicaragua", "Niger", "Norway", "Pakistan", "Papua New Guinea",
    "Peru", "Poland", "Portugal", "Qatar", "Romania",
    "Rwanda", "Saudi Arabia", "Senegal", "Slovenia", "South Africa",
    "Spain", "Sri Lanka", "Suriname", "Sweden", "Switzerland",
    "Tajikistan", "Thailand", "Tunisia", "Turkey", "Uganda",
    "Ukraine", "United Kingdom", "Uruguay", "Zambia", "Zimbabwe",
]

# Liste blanche simplifiée pour les tests
CULTURES_PAYS = {
    "Cassava": ["Brazil", "India", "France"],
    "Maize": ["France", "Brazil", "India", "Estonia"],
    "Plantains and others": ["Colombia", "Ecuador", "Ghana"],
    "Potatoes": ["France", "Estonia", "India", "Brazil"],
    "Rice, paddy": ["France", "India", "Japan", "Brazil"],
    "Sorghum": ["France", "India", "Brazil"],
    "Soybeans": ["France", "Brazil", "India"],
    "Sweet potatoes": ["Brazil", "India", "Japan"],
    "Wheat": ["France", "Estonia", "India", "Brazil"],
    "Yams": ["Brazil", "Ghana", "Japan"],
}


# ---------------------------------------------------------------------------
# Fixtures — Mocks
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_pipeline():
    """Pipeline mocké retournant une valeur log fixe."""
    pipeline = MagicMock()
    pipeline.predict.return_value = np.array([9.5])
    return pipeline


@pytest.fixture
def mock_pipeline_multi():
    """Pipeline mocké retournant des valeurs variées pour le tri."""
    pipeline = MagicMock()

    def predict_variees(df):
        n = len(df)
        return np.array([8.0 + i * 0.5 for i in range(n)])

    pipeline.predict.side_effect = predict_variees
    return pipeline


@pytest.fixture
def mock_metadata():
    """Métadonnées mockées imitant model_metadata.json."""
    return {
        "modele_champion": "XGBoost_Agritech_1",
        "features_all": [
            "Area", "Item", "Year",
            "average_rain_fall_mm_per_year", "pesticides_tonnes", "avg_temp",
        ],
        "cultures_disponibles": CULTURES,
        "pays_disponibles": PAYS,
        "annees_train": "1990-2010",
        "metriques_test": {
            "rmse_log": 0.2479,
            "r2_log": 0.9524,
        },
    }


@pytest.fixture
def mock_cultures_pays():
    """Liste blanche cultures/pays mockée."""
    return CULTURES_PAYS


# ---------------------------------------------------------------------------
# Fixtures — TestClient avec mocks
# ---------------------------------------------------------------------------

@pytest.fixture
def client_mock(mock_pipeline_multi, mock_metadata, mock_cultures_pays):
    """TestClient FastAPI avec modèle mocké."""
    app.state.pipeline = mock_pipeline_multi
    app.state.metadata = mock_metadata
    app.state.cultures_pays = mock_cultures_pays
    return TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures — TestClient avec vrai modèle (tests locaux uniquement)
# ---------------------------------------------------------------------------

@pytest.fixture
def client_real():
    """TestClient FastAPI avec le vrai modèle chargé depuis le disque."""
    import joblib

    base_dir = Path(__file__).resolve().parent.parent
    pipeline_path = base_dir / "model" / "model_pipeline.pkl"
    metadata_path = base_dir / "model" / "model_metadata.json"
    cultures_pays_path = base_dir / "model" / "cultures_pays_autorises.json"

    app.state.pipeline = joblib.load(pipeline_path)
    with open(metadata_path, "r") as f:
        app.state.metadata = json.load(f)
    with open(cultures_pays_path, "r") as f:
        app.state.cultures_pays = json.load(f)

    return TestClient(app)
