# Cahier des charges du dashboard : marché immobilier breton

Ce document fixe ce que le dashboard doit permettre de comprendre et de décider, avant toute
construction dans Power BI. Les définitions précises des indicateurs figurent dans
[kpi-dictionary.md](kpi-dictionary.md).

## 1. Objet

Donner une lecture claire et fiable du marché de l'habitat ancien en Bretagne à partir des
ventes réellement signées chez le notaire (base DVF de la DGFiP) : niveaux de prix,
dynamique des volumes et évolutions, de la région jusqu'à la commune.

Le dashboard privilégie la **robustesse statistique** à l'exhaustivité : prix médians plutôt
que moyens, valeurs aberrantes exclues selon une règle documentée, indicateurs masqués
lorsqu'ils reposent sur trop peu de ventes.

## 2. Public cible et usages

| Public | Besoin principal | Usage type | Fréquence |
|---|---|---|---|
| **Acheteurs** (particuliers) | Savoir quel budget prévoir pour un bien donné dans une commune | Consulter la fiche de la commune visée, comparer avec les communes voisines | Ponctuelle, pendant un projet d'achat |
| **Investisseurs** (locatif, marchands de biens) | Repérer les secteurs où les prix montent ou baissent, et leur niveau de prix | Classer les communes par évolution, croiser prix et volume | Trimestrielle |
| **Collectivités** (communes, EPCI, départements) | Situer le marché local par rapport au département et suivre sa dynamique | Comparer la commune à son département, suivre l'évolution des volumes | Semestrielle, à chaque mise à jour des données |

Le public est non technique : chaque indicateur doit se lire sans connaître la base DVF, et
chaque titre de visuel énonce l'enseignement à retenir.

## 3. Questions métier et décisions

| # | Question | Décision qu'elle éclaire | Indicateurs | Page |
|---|---|---|---|---|
| Q1 | Où le marché est-il le plus cher et le plus dynamique ? | Cibler une zone de recherche ou d'investissement | Prix médian au m², nombre de ventes, écart à la médiane départementale | Géographie |
| Q2 | Comment les prix et les volumes évoluent-ils ? | Choisir le moment d'acheter ou de vendre, anticiper un retournement | Évolution N-1 des prix et des ventes, courbe trimestrielle | Vue d'ensemble |
| Q3 | Quel budget pour un bien type dans une commune donnée ? | Calibrer un budget ou une offre d'achat | Prix médian d'un appartement T3 et d'une maison 4-5 pièces, prix médian au m² | Fiche commune |
| Q4 | Quelles communes montent ou baissent ? | Repérer les secteurs en tension ou en repli | Top 10 des hausses et des baisses de prix médian au m² | Géographie |
| Q5 | Quel type de bien se vend, et à quel prix ? | Adapter un projet (maison ou appartement, surface, nombre de pièces) | Part des maisons, répartition par surface et par nombre de pièces, distribution des prix | Typologie des biens |

## 4. Périmètre

| Dimension | Périmètre retenu |
|---|---|
| Géographie | Les 4 départements bretons : Côtes-d'Armor (22), Finistère (29), Ille-et-Vilaine (35), Morbihan (56). Maille la plus fine : la commune. |
| Période | 2021 à 2025, années civiles complètes selon la date de signature de l'acte. Les évolutions N-1 sont donc disponibles de 2022 à 2025. |
| Transactions | Ventes de gré à gré uniquement (`nature_mutation = 'Vente'`). |
| Biens | Maisons et appartements. Les indicateurs de prix portent sur les ventes d'un seul logement, éventuellement accompagné de dépendances (garage, cave, parking). |
| Source | DVF géolocalisées, DGFiP / Etalab, data.gouv.fr, Licence Ouverte. |
| Actualisation | Semestrielle, au rythme des publications de la DGFiP (avril et octobre). La date de mise à jour figure sur la page Méthodologie. |

## 5. Hors périmètre

Ces exclusions sont rappelées sur la page Méthodologie, pour que l'utilisateur sache ce que
les chiffres ne couvrent pas.

- **Ventes en l'état futur d'achèvement (VEFA)**, soit le neuf vendu sur plan : environ 5 %
  des mutations. La base ne décrit pas le logement vendu pour la quasi-totalité d'entre elles
  (pas de type ni de surface), et le prix du neuf obéit à une logique différente de l'ancien.
- **Échanges, adjudications, expropriations et ventes de terrains à bâtir**.
- **Locaux industriels et commerciaux**, et les ventes qui en comprennent un.
- **Ventes de plusieurs logements** en un seul acte (immeuble entier, lot de maisons) : elles
  comptent dans les volumes mais pas dans les prix, faute de pouvoir répartir le prix
  entre les logements.
- **Loyers et rentabilité locative** : la base DVF ne contient que des prix de vente.

## 6. Limites des données à connaître

- **Décalage temporel** : une vente apparaît dans DVF environ 6 mois après sa signature.
  Le dernier semestre publié peut être légèrement incomplet.
- **Prix** : la valeur foncière est le prix déclaré dans l'acte, TVA comprise le cas échéant
  et hors frais de notaire. Quand des dépendances sont vendues avec le logement, leur valeur
  est incluse dans le prix.
- **Surface** : la surface utilisée est la surface réelle bâtie du cadastre, pas la surface
  Loi Carrez. Pour une maison, le prix inclut aussi le terrain, que le prix au m² bâti
  ne neutralise pas.
- **Caractéristiques absentes** : état du bien, performance énergétique (DPE), étage,
  exposition. Deux biens de même surface dans la même commune peuvent avoir des prix très
  différents pour ces raisons.
- **Petites communes** : de nombreuses communes rurales comptent moins de 10 ventes par an
  et par type de bien. Leurs indicateurs de prix sont masqués plutôt qu'affichés sur une
  base fragile.

## 7. Exigences de conception

- **Lecture en Z** : cartes KPI en haut, tendances au milieu, détail en bas.
- **4 à 6 visuels par page**, un message principal par page, écrit dans le titre de la page.
- **Titres de visuels qui énoncent l'enseignement** (« Les prix des appartements reculent
  depuis 2022 »), pas seulement la mesure (« Prix médian au m² par trimestre »).
- **Bandeau de filtres identique sur chaque page** : année, département, type de bien.
- **Thème unique** : palette restreinte, une couleur d'accent pour la hausse et une pour la
  baisse, contrastes conformes aux recommandations d'accessibilité (WCAG AA).
- **Formats français** : séparateur de milliers par espace, virgule décimale, « € » et
  « m² » en suffixe, pourcentages avec signe (+3,2 %).
- **Info-bulles détaillées** sur chaque visuel : la valeur, son volume de ventes et son
  évolution.
- **Drill-through** de toute commune vers sa fiche commune.
- **Indicateurs fragiles** : en dessous du seuil de volume, l'indicateur affiche une
  valeur vide accompagnée d'une mention explicite, jamais un chiffre trompeur.
- Pas de camembert au-delà de 3 catégories, pas d'effets 3D.

## 8. Organisation des pages

| # | Page | Message principal attendu | Questions |
|---|---|---|---|
| 1 | Vue d'ensemble | Où en est le marché breton cette année par rapport à l'an dernier | Q2 |
| 2 | Géographie | Où le marché est cher, dynamique, en hausse ou en baisse | Q1, Q4 |
| 3 | Typologie des biens | Ce qui se vend, et à quel prix selon le type, la surface et le nombre de pièces | Q5 |
| 4 | Fiche commune (drill-through) | Le marché d'une commune comparé à son département | Q3 |
| 5 | Méthodologie | Source, période, règles d'exclusion, définitions, date de mise à jour | Toutes |

La maquette détaillée de chaque page (visuels, emplacement, choix de représentation) fait
l'objet d'une section dédiée, ajoutée après validation du dictionnaire des KPI.

## 9. Critères de réussite

- Chaque question Q1 à Q5 trouve sa réponse en **3 clics au plus** depuis la vue d'ensemble.
- Chaque chiffre affiché est **traçable** jusqu'à sa définition dans le dictionnaire des KPI
  et jusqu'au modèle dbt qui le calcule.
- Aucun indicateur de prix n'est affiché sur moins de ventes que le seuil documenté.
- Les totaux du dashboard concordent avec les tables dbt (contrôle à chaque mise à jour).
