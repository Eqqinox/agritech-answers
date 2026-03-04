"""Configuration centralisée de l'API Agritech Answers."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Paramètres de l'application, surchargeables par variables d'environnement."""

    model_pipeline_path: Path = BASE_DIR / "model" / "model_pipeline.pkl"
    model_metadata_path: Path = BASE_DIR / "model" / "model_metadata.json"

    model_config = {"env_prefix": "AGRITECH_"}


@lru_cache
def get_settings() -> Settings:
    """Retourne l'instance unique des paramètres."""
    return Settings()
