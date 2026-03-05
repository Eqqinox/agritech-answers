"""Application Streamlit — Interface utilisateur Agritech Answers."""

import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Agritech Answers",
    page_icon="",
    layout="wide",
)

# ---------------------------------------------------------------------------
# CSS — Dark Mode Premium Bento Grid
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* ----- Fond principal ----- */
    .stApp {
        background-color: #0e0e0e;
        color: #f0f0f0;
    }
    .stMainBlockContainer {
        padding-top: 1rem !important;
    }

    /* ----- Header personnalisé ----- */
    .header-container {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 8px 0 8px 0;
    }
    .header-title {
        font-size: 2.3rem !important;
        font-weight: 700 !important;
        color: #b0f030 !important;
        margin: 0 !important;
    }
    .header-subtitle {
        font-size: 0.95rem;
        color: #888888;
        margin: 0;
    }

    /* ----- Carte Bento ----- */
    .bento-card {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 16px;
    }
    .bento-card h3 {
        color: #b0f030 !important;
        font-size: 1.65rem !important;
        margin-top: 10px !important;
        margin-bottom: 16px !important;
        text-align: center !important;
    }

    /* ----- Grand chiffre résultat ----- */
    .big-number {
        font-size: 3.2rem;
        font-weight: 800;
        color: #b0f030;
        text-align: center;
        line-height: 1.2;
    }
    .big-label {
        font-size: 1rem;
        color: #888888;
        text-align: center;
        margin-top: 4px;
    }
    .secondary-info {
        font-size: 0.9rem;
        color: #888888;
        text-align: center;
        margin-top: 12px;
    }

    /* ----- Avertissement année ----- */
    .year-warning {
        background-color: rgba(255, 106, 0, 0.15);
        border-left: 3px solid #ff6a00;
        color: #ff6a00;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        margin-top: 8px;
    }

    /* ----- Tabs ----- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a1a;
        border-radius: 10px;
        color: #888888;
        padding: 8px 20px;
        border: 1px solid #2a2a2a;
    }
    .stTabs [aria-selected="true"] {
        background-color: #b0f030 !important;
        color: #0e0e0e !important;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* ----- Bouton principal ----- */
    .stButton > button {
        background-color: #b0f030;
        color: #0e0e0e;
        font-weight: 600;
        border: none;
        border-radius: 12px;
        padding: 10px 24px;
        width: 100%;
        font-size: 1rem;
    }
    .stButton > button:hover {
        background-color: #9ad620;
        color: #0e0e0e;
    }

    /* ----- Erreur réseau ----- */
    .error-box {
        background-color: rgba(255, 59, 48, 0.15);
        border-left: 3px solid #ff3b30;
        color: #ff3b30;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 0.9rem;
    }

    /* ----- Labels des widgets (contraste) ----- */
    .stSelectbox label,
    .stSlider label,
    .stNumberInput label {
        color: #888888 !important;
    }
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"] {
        color: #888888 !important;
    }

    /* ----- Masquer éléments Streamlit par défaut ----- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ----- Responsive — Tablette (max 768px) ----- */
    @media (max-width: 768px) {
        .header-title {
            font-size: 1.6rem !important;
        }
        .header-subtitle {
            font-size: 0.8rem !important;
        }
        .bento-card {
            padding: 16px;
            border-radius: 14px;
        }
        .bento-card h3 {
            font-size: 1.3rem !important;
        }
        .big-number {
            font-size: 2.4rem;
        }
        .big-label {
            font-size: 0.9rem;
        }
        .secondary-info {
            font-size: 0.8rem;
        }
        /* Colonnes empilées verticalement */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
    }

    /* ----- Responsive — Mobile (max 480px) ----- */
    @media (max-width: 480px) {
        .header-title {
            font-size: 1.3rem !important;
        }
        .header-subtitle {
            font-size: 0.7rem !important;
        }
        .bento-card {
            padding: 12px;
            border-radius: 10px;
        }
        .bento-card h3 {
            font-size: 1.1rem !important;
        }
        .big-number {
            font-size: 1.8rem;
        }
        .big-label {
            font-size: 0.8rem;
        }
        .secondary-info {
            font-size: 0.7rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 6px 12px;
            font-size: 0.85rem;
        }
        .stButton > button {
            padding: 8px 16px;
            font-size: 0.9rem;
        }
        .year-warning, .error-box {
            font-size: 0.75rem;
            padding: 6px 10px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Chargement dynamique des métadonnées
# ---------------------------------------------------------------------------


@st.cache_data(ttl=300)
def _charger_metadata_cache():
    """Récupère et met en cache les métadonnées (uniquement en cas de succès)."""
    response = requests.get(f"{API_URL}/metadata", timeout=10)
    response.raise_for_status()
    return response.json()


def charger_metadata():
    """Tente de charger les métadonnées. Ne met pas en cache les erreurs."""
    try:
        return _charger_metadata_cache(), None
    except requests.ConnectionError:
        return None, "L'API est inaccessible. Vérifiez qu'elle est bien démarrée."
    except requests.Timeout:
        return None, "L'API ne répond pas (délai d'attente dépassé)."
    except requests.HTTPError as e:
        return None, f"Erreur API : {e.response.status_code}"


metadata, erreur_metadata = charger_metadata()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="header-container">
        <div>
            <p class="header-title">Agritech Answers</p>
            <p class="header-subtitle">
                Prédiction et recommandation de rendement agricole
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Vérification de la disponibilité de l'API
if erreur_metadata:
    st.markdown(
        f'<div class="error-box">{erreur_metadata}</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# Health check non caché : détecte si l'API est tombée après le chargement des métadonnées
try:
    requests.get(f"{API_URL}/health", timeout=5)
except Exception:
    st.markdown(
        '<div class="error-box">'
        "L'API est inaccessible. Vérifiez qu'elle est bien démarrée."
        "</div>",
        unsafe_allow_html=True,
    )
    st.stop()

# ---------------------------------------------------------------------------
# Données pour les formulaires
# ---------------------------------------------------------------------------

cultures = sorted(metadata["cultures_disponibles"])
pays = sorted(metadata["pays_disponibles"])
annees_train = metadata["annees_train"]  # ex: "1990-2010"
cultures_pays = metadata["cultures_pays_autorises"]

# ---------------------------------------------------------------------------
# Onglets
# ---------------------------------------------------------------------------

tab_pred, tab_reco = st.tabs(["Prédiction", "Recommandation"])

# ---------------------------------------------------------------------------
# Fonction utilitaire — appel API avec gestion d'erreurs
# ---------------------------------------------------------------------------


def appeler_api(endpoint, payload):
    """Appelle un endpoint POST de l'API et retourne (données, erreur)."""
    try:
        response = requests.post(
            f"{API_URL}{endpoint}", json=payload, timeout=30
        )
        if response.status_code == 200:
            return response.json(), None
        # Erreurs métier (400, 422, 503, etc.)
        detail = response.json().get("detail", "Erreur inconnue")
        return None, f"Erreur {response.status_code} : {detail}"
    except requests.ConnectionError:
        return None, "L'API est inaccessible. Vérifiez qu'elle est bien démarrée."
    except requests.Timeout:
        return None, "L'API ne répond pas (délai d'attente dépassé)."
    except Exception:
        return None, "Une erreur inattendue est survenue."


# ===================================================================
# ONGLET PRÉDICTION
# ===================================================================

with tab_pred:
    col_inputs, col_results = st.columns([1, 2], gap="large")

    # --- Colonne gauche : formulaire ---
    with col_inputs:
        st.markdown('<div class="bento-card"><h3>Paramètres</h3>', unsafe_allow_html=True)

        pred_area = st.selectbox("Pays", pays, key="pred_area")
        pred_item = st.selectbox("Culture", cultures, key="pred_item")
        pred_year = st.slider("Année", 1990, 2030, 2013, key="pred_year")

        if pred_year > 2013:
            st.markdown(
                '<div class="year-warning">'
                f"Projection hors données d'entraînement ({annees_train})"
                "</div>",
                unsafe_allow_html=True,
            )

        pred_rainfall = st.slider(
            "Précipitations (mm/an)", 50.0, 3250.0, 1000.0, step=50.0, key="pred_rain"
        )
        pred_temp = st.slider(
            "Température moyenne (°C)", 5.0, 30.0, 20.0, step=0.5, key="pred_temp"
        )
        pred_pesticides = st.number_input(
            "Pesticides (tonnes)", min_value=0.0, value=100.0, step=10.0, key="pred_pest"
        )

        btn_pred = st.button("Prédire le rendement", key="btn_pred")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Colonne droite : résultat ---
    with col_results:
        if btn_pred:
            # Vérification : culture autorisée pour ce pays
            pays_autorises = cultures_pays.get(pred_item, [])
            if pred_area not in pays_autorises:
                st.markdown(
                    '<div class="year-warning">'
                    f"{pred_item} n'est pas cultivable dans la zone "
                    f"géographique {pred_area}."
                    "</div>",
                    unsafe_allow_html=True,
                )
            else:
                payload = {
                    "Area": pred_area,
                    "Item": pred_item,
                    "Year": pred_year,
                    "average_rain_fall_mm_per_year": pred_rainfall,
                    "pesticides_tonnes": pred_pesticides,
                    "avg_temp": pred_temp,
                }
                data, erreur = appeler_api("/predict", payload)

                if erreur:
                    st.markdown(
                        f'<div class="error-box">{erreur}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    rendement_t = data["rendement_t_ha"]
                    rendement_hg = data["rendement_hg_ha"]

                    st.markdown(
                        '<div class="bento-card">'
                        '<h3>Résultat de la prédiction</h3>'
                        f'<div class="big-number">{rendement_t:,.2f} t/ha</div>'
                        f'<div class="big-label">{data["culture"]} — {data["pays"]}</div>'
                        f'<div class="secondary-info">'
                        f"{rendement_hg:,.0f} hg/ha | Année {pred_year} | "
                        f"Temp. {pred_temp} °C | Pluie {pred_rainfall:,.0f} mm"
                        "</div>"
                        "</div>",
                        unsafe_allow_html=True,
                    )


# ===================================================================
# ONGLET RECOMMANDATION
# ===================================================================

with tab_reco:
    col_inputs_r, col_results_r = st.columns([1, 2], gap="large")

    # --- Colonne gauche : formulaire ---
    with col_inputs_r:
        st.markdown('<div class="bento-card"><h3>Paramètres</h3>', unsafe_allow_html=True)

        reco_area = st.selectbox("Pays", pays, key="reco_area")
        reco_year = st.slider("Année", 1990, 2030, 2013, key="reco_year")

        if reco_year > 2013:
            st.markdown(
                '<div class="year-warning">'
                f"Projection hors données d'entraînement ({annees_train})"
                "</div>",
                unsafe_allow_html=True,
            )

        reco_rainfall = st.slider(
            "Précipitations (mm/an)", 50.0, 3250.0, 1000.0, step=50.0, key="reco_rain"
        )
        reco_temp = st.slider(
            "Température moyenne (°C)", 5.0, 30.0, 20.0, step=0.5, key="reco_temp"
        )
        reco_pesticides = st.number_input(
            "Pesticides (tonnes)", min_value=0.0, value=100.0, step=10.0, key="reco_pest"
        )
        reco_prix = st.number_input(
            "Prix par tonne (optionnel)", min_value=0.0, value=0.0, step=10.0, key="reco_prix",
            help="Laisser à 0 pour un classement par rendement uniquement.",
        )

        btn_reco = st.button("Recommander les cultures", key="btn_reco")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Colonne droite : résultats ---
    with col_results_r:
        if btn_reco:
            payload = {
                "Area": reco_area,
                "Year": reco_year,
                "average_rain_fall_mm_per_year": reco_rainfall,
                "pesticides_tonnes": reco_pesticides,
                "avg_temp": reco_temp,
            }
            if reco_prix > 0:
                payload["prix_par_tonne"] = reco_prix

            data, erreur = appeler_api("/recommend", payload)

            if erreur:
                st.markdown(
                    f'<div class="error-box">{erreur}</div>',
                    unsafe_allow_html=True,
                )
            else:
                classement = data["classement"]
                df = pd.DataFrame(classement)

                # --- Carte graphique : barres horizontales ---
                st.markdown(
                    '<div class="bento-card">'
                    f'<h3>Classement des cultures — {data["pays"]}</h3>',
                    unsafe_allow_html=True,
                )

                df_plot = df.sort_values("rendement_t_ha", ascending=True)

                fig = px.bar(
                    df_plot,
                    x="rendement_t_ha",
                    y="culture",
                    orientation="h",
                    color="rendement_t_ha",
                    color_continuous_scale=["#ff6a00", "#b0f030"],
                    labels={
                        "rendement_t_ha": "Rendement (t/ha)",
                        "culture": "",
                    },
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#f0f0f0",
                    coloraxis_showscale=False,
                    margin=dict(l=0, r=20, t=10, b=10),
                    height=380,
                    xaxis=dict(gridcolor="#2a2a2a"),
                    yaxis=dict(gridcolor="#2a2a2a"),
                )
                fig.update_traces(
                    marker_line_width=0,
                    text=df_plot["rendement_t_ha"].apply(lambda v: f"{v:,.2f}"),
                    textposition="outside",
                    textfont_color="#f0f0f0",
                )

                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # --- Carte tableau ---
                st.markdown(
                    '<div class="bento-card"><h3>Détail du classement</h3>',
                    unsafe_allow_html=True,
                )

                df_display = df.copy()
                df_display.insert(0, "Rang", range(1, len(df_display) + 1))
                df_display = df_display.rename(
                    columns={
                        "culture": "Culture",
                        "rendement_hg_ha": "Rendement (hg/ha)",
                        "rendement_t_ha": "Rendement (t/ha)",
                        "revenu_estime": "Revenu estimé",
                    }
                )
                colonnes = ["Rang", "Culture", "Rendement (t/ha)", "Rendement (hg/ha)"]
                if reco_prix > 0 and "Revenu estimé" in df_display.columns:
                    colonnes.append("Revenu estimé")

                st.dataframe(
                    df_display[colonnes],
                    use_container_width=True,
                    hide_index=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)
