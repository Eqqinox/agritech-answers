# Rapport métier : Agritech Answers
# Système de prédiction et de recommandation de rendement agricole



## 1. Synthèse exécutive

Le système Agritech Answers est opérationnel. Il prédit le rendement de dix cultures dans cent pays avec un R² de 0,93 sur des données que le modèle n'a jamais vues. Deux fonctions sont accessibles depuis l'interface : estimer le rendement d'une culture pour des conditions données, ou classer toutes les cultures disponibles par rendement prédit (avec option de pondération par le prix de vente).

Le modèle retenu est XGBoost, nommé XGBoost_Agritech_1. Il a été préféré à ExtraTrees, pourtant meilleur en validation croisée standard, pour la raison suivante : ExtraTrees n'a presque rien gagné à l'optimisation (+0,99 % de RMSE), là où XGBoost a progressé de 15,55 % grâce à ses paramètres de régularisation. Sur des données chronologiques, cette robustesse compte.

Le résultat central à retenir : la culture est de loin le premier déterminant du rendement. Température et précipitations arrivent ensuite, à importance quasi égale. Les pesticides et le pays complètent le tableau. L'année n'a aucun impact mesurable sur la période 1990-2013.

---

## 2. Données et préparation

### Sources

Deux jeux de données ont été utilisés. Le premier, issu de la FAO (Food and Agriculture Organization), constitue la source unique pour la modélisation, l'API et l'interface : il regroupe les rendements historiques de cent un pays sur dix cultures, de 1990 à 2013, enrichis des données annuelles de précipitations, température et usage de pesticides. Le second, un jeu synthétique d'un million de lignes, a servi exclusivement à l'analyse en composantes principales (ACP) demandée par Gabriel (il n'entre pas dans le pipeline de modélisation).

**Dataset final :** 13 130 observations, 7 variables, aucune valeur manquante.

### Nettoyage principal

Un problème structurel a été détecté : 53,51 % des clés métier (Area + Item + Year) étaient dupliquées, causées par plusieurs relevés de température par pays et par année dans le fichier source. Correction appliquée par agrégation en moyenne, vérifiée sur trois pays représentatifs (Albanie 1990, France 2000, Inde 2010). Les valeurs aberrantes ont été conservées, car elles correspondent à des réalités agronomiques ou géographiques documentées, pas à des erreurs de saisie.

### Ce que l'ACP a confirmé

Trois composantes principales couvrent 85 % de la variance :

- PC1 (34 %) : axe climatique (température et précipitations dominent).
- PC2 (28 %) : axe intrants/rendement (pesticides et rendement sont corrélés).
- PC3 (23 %) : axe rendement pur.

La présence de relations non linéaires, confirmée par l'ACP, a orienté le choix vers les modèles à base d'arbres. Le modèle linéaire (Ridge, R² = 0,08) le confirme a posteriori.

---

## 3. Résultats de la modélisation

### Comparaison des modèles (baseline, KFold 5)

| Modèle           | RMSE CV | R² CV  |
|:-----------------|:--------|:-------|
| ExtraTrees       | 0,2129  | 0,9641 |
| RandomForest     | 0,2458  | 0,9517 |
| XGBoost          | 0,2706  | 0,9418 |
| CatBoost         | 0,2907  | 0,9330 |
| LightGBM         | 0,3264  | 0,9156 |
| GradientBoosting | 0,5042  | 0,7988 |
| Ridge            | 1,0766  | 0,0834 |

Les modèles à base d'arbres dominent sans ambiguité.<br> Ridge échoue : les données sont non linéaires.

### Pourquoi XGBoost et pas ExtraTrees

La validation temporelle (TimeSeriesSplit) a mis en évidence un écart significatif entre validation croisée standard et généralisation temporelle pour les trois meilleurs modèles.<br> Après optimisation, XGBoost est le seul à avoir réellement progressé :

| Modèle       | RMSE baseline | RMSE optimisé | Gain      |
|:-------------|:--------------|:--------------|:----------|
| ExtraTrees   | 0,2129        | 0,2108        | +0,99 %   |
| RandomForest | 0,2458        | 0,2830        | -15,12 %  |
| XGBoost      | 0,2706        | 0,2285        | +15,55 %  |

ExtraTrees a atteint son plafond dès les paramètres par défaut. XGBoost a bénéficié de la régularisation native (`reg_lambda=5.0`, `min_child_weight=3`) et d'un affinage sur 100 itérations (RandomizedSearchCV), portant le gain total à 15,55 % par rapport à la configuration initiale.

### Performances finales sur le jeu de test (2011-2013)

| Métrique | Echelle log | Echelle hg/ha |
|:---------|:------------|:--------------|
| RMSE     | 0,2479      | 22 535 hg/ha  |
| R²       | 0,9524      | 0,9348        |
| MAE      | 0,1656      | 11 278 hg/ha  |

Le modèle explique 93 % de la variance du rendement sur des années non vues.<br> L'erreur moyenne est de 1,13 tonne par hectare (acceptable pour un outil d'aide à la décision à l'échelle du pays).

### Performance par culture

| Culture              | Obs | RMSE (hg/ha) | R²     |
|:---------------------|:----|:-------------|:-------|
| Soybeans             | 170 | 3 025        | 0,8664 |
| Wheat                | 240 | 5 864        | 0,9213 |
| Rice, paddy          | 198 | 7 473        | 0,8742 |
| Maize                | 273 | 11 795       | 0,8770 |
| Sorghum              | 194 | 12 826       | 0,6632 |
| Yams                 | 60  | 25 249       | 0,7362 |
| Cassava              | 123 | 31 814       | 0,8143 |
| Potatoes             | 282 | 32 660       | 0,9035 |
| Plantains and others | 63  | 36 045       | 0,6819 |
| Sweet potatoes       | 153 | 40 874       | 0,7610 |

Le RMSE absolu élevé des pommes de terre et des patates douces ne traduit pas une faiblesse du modèle; en effet ces cultures ont des rendements naturellement plus élevés.
Le R² reste supérieur à 0,76 pour huit cultures sur dix.<br> Sorgho et plantains font exception car ils sont sous-représentés dans les données.

---

## 4. Variables clés et interprétation agronomique

### Importance des variables

Deux méthodes d'interprétabilité ont été utilisées : l'importance native XGBoost (fréquence d'utilisation dans les splits) et la permutation importance (dégradation réelle de la performance quand la variable est permutée aléatoirement, 30 répétitions).<br> Les deux convergent, ce qui est un bon signe.

| Variable                      | Importance native | Permutation (moy.) |
|:------------------------------|:------------------|:-------------------|
| Item (culture)                | 0,7274            | 1,4965             |
| average_rain_fall_mm_per_year | 0,0973            | 0,1477             |
| avg_temp                      | 0,0587            | 0,1512             |
| pesticides_tonnes             | 0,0522            | 0,1173             |
| Area (pays)                   | 0,0557            | 0,0827             |
| Year                          | 0,0087            | 0,0000             |

### Ce que ces chiffres signifient pour un agriculteur

**La <mark>culture choisie est le déterminant principal</mark>.** Elle capte 73 % de l'importance native. Ce n'est pas surprenant : le potentiel génétique d'une espèce fixe le plafond du rendement atteignable, indépendamment des conditions climatiques.

**Température et précipitations sont les deux leviers climatiques à surveiller.** En permutation importance, ils arrivent quasiment à égalité (0,1512 et 0,1477).<br> Chaque culture a une plage thermique optimale au-delà de laquelle le rendement chute.<br> Les précipitations conditionnent la disponibilité en eau (un déficit ou un excès hydrique en période peut annuler les avantages de la culture choisie).

**Les pesticides reflètent l'intensité du système de production.** Un usage plus élevé est corrélé à des systèmes intensifs qui produisent davantage, mais ce n'est pas un levier direct.

**Le pays capture ce que les autres variables ne disent pas.** Qualité des sols, infrastructures d'irrigation, pratiques locales, politiques agricoles : tout cela est compressé dans une seule variable. Il encode aussi, indirectement, quelles cultures sont agronomiquement viables dans une région, ce qui a justifié la construction d'une liste blanche par pays pour filtrer les recommandations aberrantes.

**L'année n'a aucun impact mesurable.** Sur la période 1990-2013, les tendances temporelles sont négligeables. Le modèle n'est pas adapté à une extrapolation au-delà de 2013 sans données supplémentaires.

---

## 5. Recommandations

### Recommandations agronomiques

Les cinq cultures les plus fiables pour la prise de décision, par ordre de R² décroissant, sont :

**Blé (R² = 0,92, RMSE = 5 864 hg/ha).** Culture la mieux prédite. Large tolérance climatique, bon comportement dans les zones tempérées. Les précipitations et la température sont les principaux leviers d'optimisation.

**Pommes de terre (R² = 0,90, RMSE = 32 660 hg/ha).** Rendements absolus élevés, prédictions robustes. Particulièrement performantes dans les zones tempérées avec précipitations modérées. Le RMSE en valeur absolue est élevé parce que les rendements le sont aussi.

**Maïs (R² = 0,88, RMSE = 11 795 hg/ha).** Culture sensible à la température et aux précipitations. La fonction de recommandation est particulièrement utile ici pour identifier les conditions optimales par pays.

**Soja (R² = 0,87, RMSE = 3 025 hg/ha).** RMSE le plus bas en valeur absolue ; les prédictions sont les plus précises en chiffres bruts. Culture adaptée aux zones chaudes et humides.

**Riz (R² = 0,87, RMSE = 7 473 hg/ha).** Performances solides. Fortement dépendant des précipitations : la prédiction sera d'autant plus fiable que les données pluviométriques locales sont précises.

**Sorgho et plantains : prudence.** R² respectifs de 0,66 et 0,68. Ces deux cultures manquent de données (194 et 63 observations). Les recommandations les impliquant doivent être traitées comme des orientations, pas comme des prédictions fiables.

### Utilisation de la fonction de recommandation

Pour un agriculteur, la démarche naturelle est la suivante : sélectionner son pays, renseigner la température, les précipitations et l'usage de pesticides de sa parcelle, saisir un prix de vente par tonne si disponible, et laisser le système classer les cultures par rendement ou revenu estimé. La variable `Item` dominant le modèle, le classement est structuré par les potentiels biologiques des cultures (les conditions climatiques affinent ensuite le tri).

### Recommandations techniques pour la suite

**Données récentes.** Le modèle est aveugle à tout ce qui s'est passé après 2013 (évolutions climatiques, nouvelles pratiques, variétés améliorées). Intégrer des données FAO jusqu'en 2025-2026 est la priorité pour maintenir la pertinence du système.

**Variables manquantes.** Le type de sol et l'accès à l'irrigation expliquent une part importante de la variance résiduelle. Leur ajout améliorerait les prédictions et réduirait la dépendance à la variable `Area` comme variable proxy.

**Analyse SHAP.** Un bug de compatibilité entre les versions SHAP et XGBoost installées a bloqué cette analyse. Une fois résolu, SHAP permettra d'expliquer chaque prédiction individuellement (pourquoi le modèle recommande telle culture dans tel contexte précis). C'est la prochaine étape naturelle en interprétabilité.

**Monitoring en production.** Une fois le système utilisé sur des données réelles, un suivi du data drift et du performance drift est indispensable pour détecter toute dégradation silencieuse des prédictions.

---

## 6. Limites et vigilance

**Couverture temporelle.** Les données s'arrêtent en 2013. L'interface signale automatiquement quand l'utilisateur saisit une année postérieure (il s'agit alors d'une projection, pas d'une prédiction au sens strict).

**Overfitting modéré.** L'écart entre score d'entraînement (0,9958) et score de validation (0,9586) est de 3,71 points. Les paramètres de régularisation le contiennent, mais il faudra surveiller cet écart si le périmètre des données s'élargit.

**Filtrage géographique des cultures.** Une liste blanche par pays (`cultures_pays_autorises.json`) a été construite pour éviter des recommandations agronomiquement absurdes (le système ne proposera pas de plantains pour un agriculteur estonien). Ce filtre est basé sur les données historiques disponibles et peut exclure des cultures cultivables mais non représentées dans le dataset FAO.

**Hébergement.** L'API est déployée sur un plan gratuit de Render, avec un temps de démarrage à froid de 30 à 50 secondes après 15 minutes d'inactivité. Acceptable pour un prototype, à résoudre avant toute mise en production réelle.

---

## 7. Suivi MLflow

Toutes les expérimentations ont été tracées dans MLflow : paramètres, métriques et tags pour chaque run. Le tableau ci-dessous résume les runs enregistrées.

| Run                                        | Phase                 |
|:-------------------------------------------|:----------------------|
| `{modele}_baseline` (x7)                  | Comparaison baseline  |
| `{modele}_timeseries` (x3)                | Validation temporelle |
| `ExtraTrees_optimise`                      | Optimisation          |
| `RandomForest_optimise`                    | Optimisation          |
| `XGBoost_optimise`                         | Optimisation          |
| `XGBoost_affinage`                         | Affinage              |
| `XGBoost_Agritech_1_evaluation_finale`     | Evaluation finale     |

Les captures d'écran de l'interface MLflow (comparaison des runs, métriques, paramètres optimaux) sont disponibles en annexe.

---

## Conclusion

Le système fonctionne. Il prédit correctement le rendement de huit cultures sur dix avec un R² supérieur à 0,76, et atteint 0,93 sur l'ensemble du jeu de test. La valeur ajoutée principale est la fonction de recommandation : elle permet à un agriculteur de comparer objectivement les options disponibles pour sa parcelle, en intégrant les conditions climatiques réelles et, si souhaité, les prix de marché.

Les deux limites les plus importantes à adresser sont la coupure temporelle de 2013 et l'absence de données sur les sols et les types d'irrigation. Ce sont des contraintes du dataset, pas de l'architecture (le pipeline est conçu pour intégrer de nouvelles données sans modification structurelle).

---
**Auteur :** Mounir Meknaci, Data Scientist ML junior  
**Date :** Mars 2026