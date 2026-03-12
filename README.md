# Agritech Answers : Prédiction et recommandation de rendement agricole

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-189FDD?logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI/CD-2088FF?logo=github-actions&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-0194E2?logo=mlflow&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)

Ce projet implémente un système de prédiction et de recommandation de rendement agricole, destiné à aider les agriculteurs à prendre de meilleures décisions. Il s'appuie sur un modèle XGBoost entraîné sur des données FAO (101 pays, 10 cultures, 1990-2013), servi par une API FastAPI et accessible via une interface Streamlit.

**Application déployée :**
- API : https://agritech-api-r98k.onrender.com/docs
- Interface : https://agritech-answers-l8jetqnwc4f8ccbmnpln6r.streamlit.app

> Note : l'API est hébergée sur un plan gratuit Render. Un premier appel peut prendre 30 à 50 secondes après une période d'inactivité.

---

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Architecture](#architecture)
- [Modélisation](#modélisation)
- [API](#api)
- [Interface Streamlit](#interface-streamlit)
- [Tests](#tests)
- [CI/CD et déploiement](#cicd-et-déploiement)
- [Licence](#licence)
- [Auteur](#auteur)

---

## Fonctionnalités

- **Prédiction** : estimation du rendement pour une culture donnée, en fonction des conditions climatiques et agricoles (température, précipitations, pesticides)
- **Recommandation** : simulation de toutes les cultures possibles pour un pays donné, classées par rendement décroissant ou par revenu estimé (si un prix par tonne est fourni)
- **Filtrage intelligent** : seules les cultures réellement cultivées dans un pays sont proposées (liste blanche `cultures_pays_autorises.json`)
- **Interface responsive** : dark mode, layout Bento Grid, graphiques Plotly, compatible tablette et mobile
- **Pipeline CI/CD** : tests automatisés, build Docker et déploiement sur Render à chaque push

---

## Prérequis

- Python 3.11+
- Gestionnaire de paquets Python ([uv](https://docs.astral.sh/uv/))
- Docker et Docker Compose (pour l'exécution conteneurisée)

---

## Installation

1. **Cloner le dépôt**

```bash
$ git clone https://github.com/Eqqinox/agritech-answers
$ cd agritech-answers
```

2. **Créer et activer l'environnement virtuel**

```bash
$ uv venv
$ source .venv/bin/activate
```

3. **Installer les dépendances**

```bash
$ uv add -r requirements.txt
$ uv add -r requirements_dev.txt
```

---

## Utilisation

### <u>1. Lancement local (sans Docker)</u>

**API :**

```bash
$ uvicorn src.api.main:app --reload
```

L'API est accessible sur http://localhost:8000. La documentation interactive est disponible sur http://localhost:8000/docs.

**Streamlit :**

```bash
$ streamlit run src/streamlit/app.py
```

L'interface est accessible sur http://localhost:8501.

### <u>2. Lancement avec Docker Compose</u>

```bash
$ docker compose up --build
```

Deux services sont démarrés :
- API : http://localhost:8000
- Streamlit : http://localhost:8501

### <u>3. Tests</u>

```bash
# Suite complète (avec vrai modèle)
$ pytest -v

# Sans le vrai modèle (mode CI)
$ pytest -v -m "not local"

# Rapport de couverture HTML
$ pytest --cov=src/api --cov-report=html
```

---

## Structure du projet

```
.
├── .github/
│   └── workflows/
│       └── ci-cd.yml                  # Pipeline GitHub Actions
│
├── inputs/                            # Données sources (CSV)
│   ├── crop_yield.csv
│   └── Crop Yield Prediction Dataset/
│       ├── pesticides.csv
│       ├── rainfall.csv
│       ├── temp.csv
│       ├── yield_df.csv
│       └── yield.csv
│
├── model/                             # Fichiers modèle (hors Git, dans GitHub Release)
│   ├── model_pipeline.pkl             # Pipeline sklearn (préprocesseur + XGBoost)
│   ├── model_metadata.json            # Métadonnées : cultures, pays, features, métriques
│   └── cultures_pays_autorises.json   # Liste blanche cultures par pays
│
├── notebooks/
│   ├── exploration_fusion.ipynb       # Exploration, nettoyage, ACP
│   └── modelisations.ipynb            # Comparaison, optimisation, évaluation
│
├── outputs/                           # Visualisations et datasets produits
│   ├── dataset_final.csv
│   ├── crop_yield_clean.csv
│   ├── comparaison_baseline.png
│   ├── evaluation_finale.png
│   ├── feature_importance.png
│   ├── permutation_importance.png
│   ├── learning_curves.png
│   └── rmse_par_culture.png
│
├── src/
│   ├── api/
│   │   ├── main.py                    # Point d'entrée, lifespan, handlers d'erreurs
│   │   ├── config.py                  # Configuration centralisée (BaseSettings)
│   │   ├── exceptions.py              # Exceptions métier
│   │   ├── schemas/
│   │   │   ├── predict.py             # PredictRequest, PredictResponse
│   │   │   └── recommend.py           # RecommendRequest, RecommendResponse
│   │   ├── routers/
│   │   │   ├── health.py              # GET /health, GET /metadata
│   │   │   ├── predict.py             # POST /predict
│   │   │   └── recommend.py           # POST /recommend
│   │   └── services/
│   │       └── prediction.py          # Logique métier (predict, recommend)
│   └── streamlit/
│       └── app.py                     # Interface utilisateur Streamlit
│
├── tests/
│   ├── conftest.py                    # Fixtures partagées (mocks, clients)
│   ├── unit/
│   │   ├── test_schemas.py            # Validation Pydantic (15 tests)
│   │   ├── test_exceptions.py         # Exceptions métier (8 tests)
│   │   └── test_service.py            # Logique métier (13 tests)
│   └── integration/
│       ├── test_endpoint_health.py    # GET /health, GET /metadata (3 tests)
│       ├── test_endpoint_predict.py   # POST /predict (8 tests)
│       └── test_endpoint_recommend.py # POST /recommend (10 tests)
│
├── Dockerfile                         # Image Docker API
├── Dockerfile.streamlit               # Image Docker Streamlit
├── docker-compose.yml                 # Orchestration API + Streamlit
├── requirements.txt                   # Dépendances API
├── requirements_dev.txt               # Dépendances de test
├── requirements_streamlit.txt         # Dépendances Streamlit
├── pytest.ini                         # Configuration pytest
├── pyproject.toml                     # Métadonnées du projet
├── mlflow.db                          # Base MLflow (tracking local)
└── uv.lock                            # Verrou des dépendances
```

---

## Architecture

```
                         Utilisateur
                              │
                              ▼
                    ┌───────────────────┐
                    │    Streamlit      │
                    │   (front-end)     │
                    │  Streamlit Cloud  │
                    └────────┬──────────┘
                             │ requests (HTTP)
                             ▼
                     ┌────────────────┐
                     │   FastAPI      │
                     │  (back-end)    │
                     │    Render      │
                     └───────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────────┐
        │ Routers  │  │ Schemas  │  │  Exceptions  │
        │ (HTTP)   │  │(Pydantic)│  │   (métier)   │
        └────┬─────┘  └──────────┘  └──────────────┘
             │
             ▼
        ┌──────────┐
        │ Services │
        │ (métier) │
        └────┬─────┘
             │
             ▼
    ┌──────────────────┐
    │ Pipeline sklearn │
    │ (XGBoost .pkl)   │
    └──────────────────┘
```

**Principe** : les routers reçoivent la requête HTTP et la transmettent au service. Le service contient toute la logique métier (prédiction, simulation, tri) et ne connaît ni FastAPI ni HTTP. Les schémas Pydantic valident les entrées/sorties. Les exceptions métier sont traduites en codes HTTP par les handlers dans `main.py`.

---

## Modélisation

### <u>Données</u>

- **Source** : données FAO fusionnées (rendement, pesticides, précipitations, température)
- **Dataset** : 13 130 lignes, 100 pays, 10 cultures, période 1990-2013
- **Transformation** : `log1p` sur la variable cible pour compresser la distribution asymétrique
- **Split temporel** : train <= 2010, test 2011-2013 (pas de data leakage)
- **Encodage** : `OrdinalEncoder` sur les variables catégorielles (`Area`, `Item`)
- **Normalisation** : `StandardScaler` sur les variables numériques

### <u>Comparaison et sélection</u>

7 modèles comparés en baseline (KFold 5). Top 3 retenu pour optimisation :

| Modèle | RMSE CV | R2 CV |
|---|---|---|
| ExtraTrees | 0.2129 | 0.9641 |
| RandomForest | 0.2458 | 0.9517 |
| XGBoost | 0.2706 | 0.9418 |

### <u>Modèle retenu : XGBoost</u>

Choisi face à ExtraTrees (RMSE 0.2108) car ExtraTrees atteint son plafond dès les paramètres par défaut (+0.99% de gain). XGBoost offre une régularisation native et une meilleure robustesse en généralisation temporelle.

### <u>Optimisation</u>

| Étape | RMSE |
|---|---|
| XGBoost baseline | 0.2706 |
| GridSearchCV | 0.2340 |
| RandomizedSearchCV (affinage) | **0.2285** |
| **Gain total** | **+15.55%** |

### <u>Evaluation finale (test 2011-2013)</u>

| Métrique | Echelle log | Echelle hg/ha |
|---|---|---|
| R2 | 0.9524 | 0.9348 |
| RMSE | 0.2479 | 22 535 hg/ha |
| MAE | 0.1656 | 11 278 hg/ha |

### <u>Variables clés (permutation importance)</u>

| Rang | Feature | Importance |
|---|---|---|
| 1 | Item (culture) | 1.4965 |
| 2 | avg_temp | 0.1512 |
| 3 | average_rain_fall_mm_per_year | 0.1477 |
| 4 | pesticides_tonnes | 0.1173 |
| 5 | Area (pays) | 0.0827 |
| 6 | Year | 0.0000 |

### <u>Suivi MLflow</u>

Toutes les expérimentations sont tracées dans MLflow : 7 baselines, 3 validations temporelles, 3 optimisations, 1 affinage et 1 évaluation finale.

---

## API

### <u>Endpoints</u>

| Endpoint | Méthode | Description |
|---|---|---|
| `/health` | GET | Statut de l'API et nom du modèle chargé |
| `/metadata` | GET | Cultures, pays et années disponibles |
| `/predict` | POST | Prédiction de rendement pour une culture et des conditions données |
| `/recommend` | POST | Classement de toutes les cultures par rendement (ou revenu) pour un pays |

### <u>Exemple de requête</u>

```bash
# Prédiction
$ curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"Area": "France", "Item": "Wheat", "Year": 2010,
       "average_rain_fall_mm_per_year": 800,
       "pesticides_tonnes": 100, "avg_temp": 15}'

# Recommandation
$ curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"Area": "France", "Year": 2010,
       "average_rain_fall_mm_per_year": 800,
       "pesticides_tonnes": 100, "avg_temp": 15,
       "prix_par_tonne": 200}'
```

### <u>Codes HTTP</u>

| Code | Déclencheur |
|---|---|
| 200 | Succès |
| 400 | Valeur négative sur un champ métier |
| 404 | Route inexistante |
| 422 | Validation Pydantic, culture ou pays inconnu |
| 500 | Erreur interne |
| 503 | Modèle non chargé |

---

## Interface Streamlit

L'application propose deux modes dans une interface dark mode responsive :

- **Onglet Prédiction** : sélection d'un pays, d'une culture et de conditions climatiques. Affichage du rendement estimé en t/ha.
- **Onglet Recommandation** : sélection d'un pays et de conditions. Affichage d'un classement sous forme de graphique Plotly (barres horizontales, dégradé orange vers lime) et d'un tableau récapitulatif.

Le front-end ne contient aucune logique de Machine Learning. Il interroge l'API via la bibliothèque `requests` et affiche les résultats.

---

## Tests

**57 tests** avec une **couverture de 92%** sur `src/api/`

| Catégorie | Fichier | Tests |
|---|---|---|
| Unitaire | `test_schemas.py` | Validation Pydantic (bornes, types, champs) : 15 tests |
| Unitaire | `test_exceptions.py` | Instanciation et héritage des exceptions : 8 tests |
| Unitaire | `test_service.py` | predict, recommend, filtrage, tri : 13 tests |
| Intégration | `test_endpoint_health.py` | GET /health, GET /metadata : 3 tests |
| Intégration | `test_endpoint_predict.py` | POST /predict (nominaux + erreurs) : 8 tests |
| Intégration | `test_endpoint_recommend.py` | POST /recommend (nominaux + filtrage + erreurs) : 10 tests |

Les tests utilisent un modèle mocké pour fonctionner sans le fichier `.pkl`. Les tests marqués `@pytest.mark.local` (avec le vrai modèle) sont exécutés uniquement en local.

---

## CI/CD et déploiement

### <u>Infrastructure</u>

| Composant | Outil |
|---|---|
| Hébergement API | Render (plan Free, Frankfurt) |
| Registre d'images | Docker Hub |
| Front-end | Streamlit Community Cloud |
| Fichiers modèle | GitHub Release `v1.0.0` |

### <u>Pipeline GitHub Actions</u>

Fichier : `.github/workflows/ci-cd.yml`

Déclenché à chaque push ou pull request sur `develop`.

```
Push sur develop
    │
    ├── Job 1 : Tests
    │       pytest -v -m "not local"
    │       │
    │       ▼ (succès)
    │
    └── Job 2 : Build & Deploy
            ├── Téléchargement modèle (GitHub Release)
            ├── Build image Docker (linux/amd64)
            ├── Push vers Docker Hub
            └── Trigger Deploy Hook Render
                    │
                    ▼
            API redéployée automatiquement
```

### <u>Secrets GitHub</u>

| Secret | Rôle |
|---|---|
| `DOCKERHUB_USERNAME` | Authentification Docker Hub (login) |
| `DOCKERHUB_TOKEN` | Authentification Docker Hub (token) |
| `RENDER_DEPLOY_HOOK` | URL webhook de redéploiement Render |

---

## Licence

Projet académique : Formation Expert en Ingénierie et Science des Données

Ce projet a été réalisé dans le cadre d'un parcours de formation et n'est pas destiné à un usage commercial.

---

## Auteur

**Mounir Meknaci**

- Email : meknaci81@gmail.com
- LinkedIn : [Mounir Meknaci](https://www.linkedin.com/in/mounir-meknaci/)
- Formation : Expert en ingénierie et science des données
- Projet : Agritech Answers, Optimisation agricole par les données