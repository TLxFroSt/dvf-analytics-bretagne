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
l'objet de la [section 10](#10-maquette-des-pages).

## 9. Critères de réussite

- Chaque question Q1 à Q5 trouve sa réponse en **3 clics au plus** depuis la vue d'ensemble.
- Chaque chiffre affiché est **traçable** jusqu'à sa définition dans le dictionnaire des KPI
  et jusqu'au modèle dbt qui le calcule.
- Aucun indicateur de prix n'est affiché sur moins de ventes que le seuil documenté.
- Les totaux du dashboard concordent avec les tables dbt (contrôle à chaque mise à jour).

## 10. Maquette des pages

Format : page 16:9 (1280 × 720 px). Les noms de mesures renvoient au
[dictionnaire des KPI](kpi-dictionary.md). Les chiffres et les titres des maquettes sont
**illustratifs** : ils montrent la forme attendue, pas des résultats.

### 10.1 Éléments communs à toutes les pages

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ TITRE DE LA PAGE = message principal (dynamique)                             │
│ [Vue d'ensemble] [Géographie] [Typologie] [Méthodologie]                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ Année [2025 ▾]     Département [Tous ▾]     Type de bien [ Maison | Appart. ]│
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         zone des visuels de la page                          │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│ Source : DVF géolocalisées (DGFiP) · Données au JJ/MM/AAAA · Méthodologie →  │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Bandeau de filtres**, synchronisé entre les pages :

| Filtre | Comportement | Valeur par défaut | Raison |
|---|---|---|---|
| Année | Liste déroulante, **sélection unique** | Dernière année complète (2025) | Les évolutions N-1 comparent une année à la précédente : une seule année doit être active. |
| Département | Liste déroulante, sélection multiple | Tous | Permet de comparer deux départements ou d'en isoler un. |
| Type de bien | Boutons, **sélection unique** | Maison (deux tiers des ventes) | Les prix des maisons et des appartements ne se mélangent jamais (voir le dictionnaire). Imposer un type évite tout visuel vide ou trompeur, et chaque page se lit « pour les maisons » ou « pour les appartements ». |

**Titres dynamiques** : le titre de page est une mesure DAX qui assemble l'enseignement à
partir des données filtrées (sens de l'évolution, valeur clé, territoire). Il reste donc
juste quel que soit le filtre.

**Exceptions aux filtres**, réglées par les interactions entre visuels :

- les courbes temporelles ignorent le filtre Année et montrent toute la période 2021-2025,
  pour situer l'année sélectionnée dans sa tendance ;
- les visuels de comparaison maisons / appartements (page Typologie) ignorent le filtre
  Type de bien.

**Valeurs masquées** : une mesure vide sous le seuil de volume s'affiche « Moins de 10
ventes » en gris dans les cartes et les tableaux, et en gris neutre sur la carte.

### 10.2 Page 1 : Vue d'ensemble

**Message** : où en est le marché cette année par rapport à l'an dernier (Q2).
Exemple de titre : « Maisons en 2025 : les ventes repartent (+8 %), les prix se stabilisent ».

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Titre · navigation · bandeau de filtres                                      │
├──────────────────┬──────────────────┬──────────────────┬─────────────────────┤
│ A  Ventes        │    Prix médian   │    Prix médian   │    Part des maisons │
│    25 000        │    au m²         │    bien type     │    64 %             │
│    +8,0 % vs N-1 │    2 300 €       │    245 000 €     │                     │
│                  │    +1,2 % vs N-1 │    Maison 4-5 p. │                     │
├──────────────────┴──────────────────┼──────────────────┴─────────────────────┤
│ B  Prix médian au m² par trimestre  │ C  Ventes par trimestre                │
│    une courbe par département       │    colonnes, 2021 T1 → 2025 T4         │
│    2021 T1 → 2025 T4                │                                        │
├─────────────────────────────────────┴────────────────────────────────────────┤
│ D  Les départements : Ventes · Évol. ventes % · Prix médian m² ·             │
│    Évol. prix m² % · Prix médian bien type        (+ ligne Bretagne)         │
└──────────────────────────────────────────────────────────────────────────────┘
```

| Visuel | Type | Contenu | Pourquoi ce choix |
|---|---|---|---|
| A | Carte multi-valeurs (1 visuel, 4 valeurs) | `Ventes` et `Évol. ventes %` ; `Prix médian m²` et `Évol. prix m² %` ; `Prix médian bien type` ; `Part maisons %` | Les 4 chiffres à retenir, lus en premier (haut gauche du Z). La variation N-1 en couleur d'accent donne le sens avant même la lecture du chiffre. |
| B | Courbes | `Prix médian m²` par trimestre, une courbe par département | La courbe est la forme naturelle d'une tendance continue. 4 séries restent lisibles ; une 5e (Bretagne) surchargerait le visuel. |
| C | Histogramme en colonnes | `Ventes` par trimestre | Un volume par période discrète se lit mieux en colonnes. Séparé de B plutôt qu'en double axe, qui suggère des corrélations visuelles trompeuses. |
| D | Tableau | Une ligne par département et un total Bretagne | Le détail chiffré, en bas du Z. Mise en forme conditionnelle des évolutions (couleurs hausse et baisse). |

Info-bulles : sur B et C, la valeur, `Ventes avec prix` (B) et l'évolution vs le même
trimestre N-1. Interaction : un clic sur un département dans D filtre B et C.

### 10.3 Page 2 : Géographie

**Message** : où le marché est cher, et où il monte ou baisse (Q1, Q4).
Exemple de titre : « Appartements en 2025 : Rennes et le golfe du Morbihan dépassent
3 500 €/m² ».

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Titre · navigation · bandeau de filtres                                      │
├───────────────────────────────────────────┬──────────────────────────────────┤
│ A  Carte des communes                     │ B  Prix médian au m²             │
│    couleur = Prix médian m²               │    par département               │
│    gris = moins de 10 ventes              │    ligne de référence Bretagne   │
│                                           ├────────────────┬─────────────────┤
│                                           │ C  Top 10      │ D  Top 10       │
│                                           │    hausses     │    baisses      │
│                                           │    barres      │    barres       │
│                                           ├────────────────┴─────────────────┤
│                                           │ E  Classement des communes       │
│                                           │    Prix · Ventes · Évol. · Écart │
└───────────────────────────────────────────┴──────────────────────────────────┘
```

| Visuel | Type | Contenu | Pourquoi ce choix |
|---|---|---|---|
| A | Carte choroplèthe (Shape map, contours TopoJSON des communes) | `Prix médian m²` par commune, palette séquentielle à une teinte | La question est géographique : la carte révèle des structures spatiales (littoral, couronne rennaise) qu'aucun tableau ne montre. Palette séquentielle car on représente un niveau, pas un écart. Communes masquées en gris neutre, distinct de la palette. |
| B | Barres horizontales | `Prix médian m²` par département, ligne de référence à la médiane Bretagne | 4 valeurs à comparer : des barres triées suffisent. La ligne de référence situe chaque département. |
| C, D | Barres horizontales | `Évol. prix m² %` des 10 communes en plus forte hausse (C) et en plus forte baisse (D), filtrées par `Commune éligible top` | Un classement se lit en barres triées. Deux visuels, en couleur d'accent hausse et baisse, pour que les deux listes ne se confondent pas. Volume de ventes en info-bulle. |
| E | Tableau | Toutes les communes : `Prix médian m²`, `Ventes avec prix`, `Évol. prix m² %`, `Écart vs département %`, triées par prix décroissant | Le détail exhaustif, avec tri. Les communes sous le seuil y figurent avec la mention « Moins de 10 ventes ». |

Info-bulle de la carte : commune, `Prix médian m²`, `Ventes avec prix`, `Évol. prix m² %`,
`Écart vs département %`. Clic droit sur une commune (A, C, D, E) : **drill-through vers la
fiche commune**.

### 10.4 Page 3 : Typologie des biens

**Message** : ce qui se vend, et à quel prix selon la surface et le nombre de pièces (Q5).
Exemple de titre : « Les petites surfaces se paient le plus cher au m² : +40 % pour un T1
par rapport à un T4 ».

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Titre · navigation · bandeau de filtres                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│ A  Part des maisons · Prix médian T3 · Prix médian maison 4-5 p.             │
├──────────────────────────────────────┬───────────────────────────────────────┤
│ B  Ventes par nombre de pièces       │ C  Ventes par tranche de surface      │
│    maisons et appartements côte à    │    maisons et appartements côte à     │
│    côte, 1 → 6 et plus               │    côte, < 30 m² → 150 m² et plus     │
├──────────────────────────────────────┼───────────────────────────────────────┤
│ D  Distribution des prix au m²       │ E  Prix médian au m² par nombre de    │
│    tranches de 250 €/m²,             │    pièces                             │
│    ligne verticale = médiane         │                                       │
└──────────────────────────────────────┴───────────────────────────────────────┘
```

Population : les ventes d'un seul logement (population prix), seules à décrire un bien
individuellement (surface, nombre de pièces).

| Visuel | Type | Contenu | Pourquoi ce choix |
|---|---|---|---|
| A | Carte multi-valeurs | `Part maisons %`, `Prix médian T3`, `Prix médian maison 4-5 p.` | Les repères de la page. Ignore le filtre Type de bien : la page compare les deux types. |
| B | Colonnes groupées | `Ventes avec prix` par nombre de pièces, une couleur par type | Catégories ordonnées et deux séries : des colonnes groupées comparent directement maisons et appartements. Pas de camembert (6 catégories). Ignore le filtre Type de bien. |
| C | Colonnes groupées | `Ventes avec prix` par tranche de surface, une couleur par type | Même logique que B, appliquée à la surface. Ignore le filtre Type de bien. |
| D | Histogramme (colonnes contiguës sur des tranches de prix calculées dans dbt) | `Ventes avec prix` par tranche de 250 €/m², pour le type sélectionné | Montre la forme de la distribution (asymétrie, dispersion) que la médiane seule masque, et justifie visuellement le choix de la médiane. Power BI n'ayant pas d'histogramme natif, les tranches sont préparées dans dbt. |
| E | Colonnes | `Prix médian m²` par nombre de pièces, pour le type sélectionné | Met en évidence l'effet taille : le prix au m² baisse quand la surface augmente. Aide à interpréter les écarts entre communes. |

### 10.5 Page 4 : Fiche commune (drill-through)

**Message** : le marché d'une commune comparé à son département (Q3).
Exemple de titre : « Vannes, appartements en 2025 : 3 450 €/m², 18 % au-dessus du Morbihan ».

Page masquée dans la navigation, atteinte par drill-through sur une commune (champ
`dim_commune[code_commune_insee]`), en conservant tous les filtres. Bouton retour en
haut à gauche.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ← Retour   Titre (commune, type, année) · bandeau de filtres                 │
├──────────────────┬──────────────────┬──────────────────┬─────────────────────┤
│ A  Ventes        │    Prix médian   │    Prix médian   │    Écart vs         │
│    + évol. N-1   │    au m²         │    bien type     │    département      │
│                  │    + évol. N-1   │                  │                     │
├──────────────────┴──────────────────┼──────────────────┴─────────────────────┤
│ B  Prix médian au m² par année      │ C  Ventes par année                    │
│    commune vs département           │    2021 → 2025                         │
│    (2 courbes)                      │                                        │
├─────────────────────────────────────┴────────────────────────────────────────┤
│ D  Commune vs département : chaque KPI en ligne,                             │
│    colonnes Commune · Département · Écart                                    │
└──────────────────────────────────────────────────────────────────────────────┘
```

| Visuel | Type | Contenu | Pourquoi ce choix |
|---|---|---|---|
| A | Carte multi-valeurs | `Ventes` et `Évol. ventes %` ; `Prix médian m²` et `Évol. prix m² %` ; `Prix médian bien type` ; `Écart vs département %` | Répond d'emblée à « combien, et est-ce cher pour le secteur ? ». |
| B | Courbes | `Prix médian m²` de la commune et `Prix médian m² département`, par année | Grain **annuel** et non trimestriel : à l'échelle d'une commune, un trimestre compte trop peu de ventes. Une année sous le seuil laisse un trou dans la courbe plutôt qu'un point trompeur. |
| C | Colonnes | `Ventes` par année | Montre la profondeur du marché local et éclaire la fiabilité des prix. |
| D | Tableau (mesures en lignes) | Ventes, prix médian au m², prix du bien type, part des maisons : commune, département, écart | La comparaison terme à terme, en bas du Z. |

### 10.6 Page 5 : Méthodologie

**Message** : d'où viennent les chiffres, et ce qu'ils ne couvrent pas.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Titre · navigation · bandeau de filtres (sans effet sur cette page)          │
├─────────────────────────────────────┬────────────────────────────────────────┤
│ A  Source, période, date de mise à  │ B  Des actes notariés aux ventes       │
│    jour, licence                    │    analysées : entonnoir des règles    │
│                                     │    (424 238 → 268 341 → 216 900)       │
├─────────────────────────────────────┴────────────────────────────────────────┤
│ C  Définitions et règles : médiane, prix au m², exclusions, seuils, VEFA,    │
│    lien vers le dictionnaire des KPI                                         │
└──────────────────────────────────────────────────────────────────────────────┘
```

| Visuel | Type | Contenu | Pourquoi ce choix |
|---|---|---|---|
| A | Zone de texte et carte | Source, licence, période ; date de mise à jour lue dans les données | La date provient du modèle, pas d'une saisie manuelle : elle ne peut pas être oubliée lors d'une mise à jour. |
| B | Entonnoir | Nombre de mutations restant après chaque règle (R2 à R5), depuis une table dédiée | Rend les exclusions concrètes et vérifiables : l'utilisateur voit ce qui a été écarté, et pourquoi. |
| C | Zone de texte | Résumé des règles et définitions du dictionnaire | Le dashboard se suffit à lui-même ; le dictionnaire complet reste la référence. |

## 11. Impacts sur le modèle de données

La maquette fixe des besoins que les modèles dbt doivent couvrir :

| Besoin | Où | Utilisé par |
|---|---|---|
| Indicateur d'appartenance à la population prix (R4) | `fct_ventes` | Toutes les mesures de prix |
| Prix au m², surface, nombre de pièces, nombre de logements | `fct_ventes` | Prix, typologie |
| Tranches de surface, de nombre de pièces et de prix au m² | `fct_ventes` | Page Typologie (B, C, D) |
| Libellé de trimestre (« 2025 T1 ») et clé de tri | `dim_date` | Courbes trimestrielles |
| Département, nom, population et EPCI de chaque commune | `dim_commune` (seed INSEE) | Filtres, drill-through, comparaisons |
| Comptages de l'entonnoir des règles | `mart_entonnoir_population` | Page Méthodologie (B) |
| Date de publication des données | Table de métadonnées | Pied de page, Méthodologie |
| Contours simplifiés des communes bretonnes (TopoJSON) | `powerbi/` | Carte de la page Géographie |
