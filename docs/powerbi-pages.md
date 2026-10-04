# Spécifications des pages Power BI

Ce document décrit, visuel par visuel, la construction des 5 pages du rapport : type de
visuel, position, champs, filtres, interactions et mise en forme. Il traduit la maquette
validée ([dashboard-spec.md](dashboard-spec.md), section 10) en consignes Power BI Desktop.

Prérequis : le modèle construit selon [powerbi/README.md](../powerbi/README.md), le thème
appliqué, et les **32 mesures** de [`measures.tmdl`](../powerbi/measures.tmdl) installées
(si le script a déjà été appliqué avec 30 mesures, le recoller entièrement dans la vue TMDL
et cliquer sur **Appliquer** : il remplace les mesures existantes et ajoute les deux
nouvelles, `Prix médian m² Bretagne` et `Couleur tranche médiane`).

Les positions sont en pixels sur une page de **1280 × 720** (format 16:9 par défaut) ; elles
se saisissent dans **Format > Général > Propriétés > Taille et position**.

---

## 0. Méthode de construction

1. Construire entièrement la **page 1**, en-tête compris.
2. Copier les éléments d'en-tête (titre, navigateur, 3 segments, pied de page) et les coller
   sur chaque autre page. Au collage des segments, Power BI propose de les
   **synchroniser** : accepter.
3. Construire le contenu de chaque page.
4. Vérifier les critères de la section 7.

**Titres de visuels** : les titres proposés énoncent l'enseignement observé sur les données
publiées le 18/05/2026 et restent vrais pour les deux types de bien. Ils sont à relire à
chaque mise à jour des données ; les titres de page, eux, sont dynamiques.

---

## 1. En-tête et pied de page (toutes les pages)

| Élément | Visuel | Position (x, y, l, h) | Contenu |
|---|---|---|---|
| Titre de page | Carte | 16, 8, 1248, 40 | La mesure de titre de la page (voir chaque page) |
| Navigation | Navigateur de pages | 16, 52, 600, 36 | Pages visibles du rapport |
| Filtre année | Segment | 640, 52, 180, 40 | `dim_date[annee]` |
| Filtre département | Segment | 832, 52, 200, 40 | `dim_commune[nom_departement]` |
| Filtre type de bien | Segment | 1044, 52, 220, 40 | `dim_type_bien[libelle_type_bien]` |
| Pied de page | Carte | 16, 692, 1248, 24 | `Texte source` |

**Titre de page** (Carte) : masquer l'étiquette de catégorie ; valeur en Segoe UI Semibold
18 pt, `#1F2933`, alignée à gauche ; arrière-plan et bordure désactivés.

**Navigateur de pages** : **Insérer > Boutons > Navigateur > Navigateur de pages**. Il
affiche automatiquement les pages visibles ; la fiche commune, masquée, n'y figure pas.
Bouton de la page active : remplissage `#2B6F77`, texte blanc.

**Segments** :

| Segment | Style | Sélection | Valeur par défaut |
|---|---|---|---|
| Année | Liste déroulante | **Sélection unique** activée | 2025 |
| Département | Liste déroulante | Multiple, option « Sélectionner tout » | Tous |
| Type de bien | Mosaïque (boutons) | **Sélection unique** activée | Maison |

**Synchronisation** : **Affichage > Synchroniser les segments**, puis pour chacun des 3
segments, cocher **Synchroniser** et **Visible** sur les 5 pages.

**Pied de page** (Carte) : masquer l'étiquette ; valeur en Segoe UI 9 pt, `#52606D`, alignée
à gauche ; sans arrière-plan ni bordure.

**Info-bulles** : sur chaque visuel de prix, ajouter `Mention volume` dans le champ
**Info-bulles**. Elle n'apparaît que lorsque le prix est masqué faute de ventes.

---

## 2. Page 1 : Vue d'ensemble

Nom de la page : **Vue d'ensemble**. Titre de page : mesure `Titre vue d'ensemble`.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Titre · navigation · segments                                                │
├──────────────────────────────────────────────────────────────────────────────┤
│ A  Ventes · Prix médian au m² · Prix médian bien type · Part des maisons     │
├─────────────────────────────────────┬────────────────────────────────────────┤
│ B  Prix médian au m², par trimestre │ C  Ventes par trimestre                │
│    et par département               │                                        │
├─────────────────────────────────────┴────────────────────────────────────────┤
│ D  Tableau des départements                                                  │
└──────────────────────────────────────────────────────────────────────────────┘
```

### A. Cartes KPI

- **Visuel** : Carte (nouvelle carte, plusieurs valeurs). Position 16, 100, 1248, 112.
- **Valeurs** : `Ventes`, `Prix médian m²`, `Prix médian bien type`, `Part maisons %`.
- **Étiquettes de référence** (une par carte) :

  | Carte | Étiquette de référence | Couleur (fx > Valeur du champ) |
  |---|---|---|
  | Ventes | `Évol. ventes %`, libellé « vs N-1 » | `Couleur évol. ventes` |
  | Prix médian m² | `Évol. prix m² %`, libellé « vs N-1 » | `Couleur évol. prix` |
  | Prix médian bien type | `Libellé bien type` | `#52606D` |
  | Part maisons % | (aucune) | |

- **Pas de titre de visuel** : les libellés des cartes suffisent.

### B. Évolution du prix au m²

- **Visuel** : Graphique en courbes. Position 16, 224, 616, 268.
- **Axe X** : `dim_date[libelle_trimestre]`. **Axe Y** : `Prix médian m²`.
  **Légende** : `dim_commune[nom_departement]`.
- **Titre** : « Les prix au m² ont progressé de 17 % depuis 2021, avec un palier en 2023-2024 ».
- **Mise en forme** : légende masquée et **étiquettes de série** activées (nom du
  département en bout de courbe), traits de 2 px, marqueurs désactivés. Couleurs des séries
  dans l'ordre de la palette : Côtes-d'Armor `#2B6F77`, Finistère `#B07A12`,
  Ille-et-Vilaine `#4A4A8A`, Morbihan `#5C3D2E`.
- **Info-bulles** : `Ventes avec prix`, `Évol. prix m² %`, `Mention volume`.
- **Interaction** : ignore le segment Année (section 6).

### C. Volume des ventes

- **Visuel** : Histogramme groupé. Position 648, 224, 616, 268.
- **Axe X** : `dim_date[libelle_trimestre]`. **Axe Y** : `Ventes`.
- **Titre** : « Les ventes ont reculé d'un tiers entre 2021 et 2024, avant de repartir en 2025 ».
- **Mise en forme** : couleur unique `#2B6F77`, étiquettes de données désactivées.
- **Info-bulles** : `Ventes N-1`, `Évol. ventes %`.
- **Interaction** : ignore le segment Année.

### D. Les départements

- **Visuel** : Tableau. Position 16, 504, 1248, 180.
- **Colonnes** : `dim_commune[nom_departement]`, `Ventes`, `Évol. ventes %`,
  `Prix médian m²`, `Évol. prix m² %`, `Prix médian bien type`.
- **Titre** : « L'Ille-et-Vilaine et le Morbihan restent nettement plus chers que le
  Finistère et les Côtes-d'Armor ».
- **Mise en forme conditionnelle** : colonne `Évol. ventes %`, **Mise en forme de cellule >
  Couleur de police > fx**, style **Valeur du champ**, champ `Couleur évol. ventes` ; idem
  pour `Évol. prix m² %` avec `Couleur évol. prix`.
- La ligne **Total** donne la Bretagne entière.

---

## 3. Page 2 : Géographie

Nom de la page : **Géographie**. Titre de page : mesure `Titre géographie`.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Titre · navigation · segments                                                │
├───────────────────────────────────────────┬──────────────────────────────────┤
│ A  Carte des communes                     │ B  Prix par département          │
│                                           ├────────────────┬─────────────────┤
│                                           │ C  Top hausses │ D  Top baisses  │
│                                           ├────────────────┴─────────────────┤
│                                           │ E  Classement des communes       │
└───────────────────────────────────────────┴──────────────────────────────────┘
```

### A. Carte des communes

- **Visuel** : Carte de formes (fonctionnalité en préversion, activée à l'étape 2 du guide
  de construction). Position 16, 100, 680, 584.
- **Emplacement** : `dim_commune[libelle_commune]`. **Saturation des couleurs** :
  `Prix médian m²`.
- **Format > Paramètres de la carte** :
  - Type de carte : **Carte personnalisée**, **Ajouter une carte** >
    `powerbi/maps/communes-bretagne.topojson` (contours simplifiés produits par
    `ingestion/build_communes_topojson.py`) ;
  - Projection : **Mercator** ;
  - **Afficher les clés de la carte** : vérifier que la clé est `libelle_commune` ; ses
    valeurs (« Vannes (56) ») sont identiques à celles de `dim_commune`.
- **Couleurs de remplissage** : saturation de `#E3F1F0` (minimum) à `#12464C` (maximum),
  divergence désactivée ; **couleur par défaut** `#C5CCD3` : les communes sans prix (moins
  de 10 ventes) apparaissent en gris neutre.
- **Titre** : « Les prix les plus élevés se concentrent sur le littoral, du golfe du Morbihan
  à la Côte d'Émeraude ».
- **Info-bulles** : `Prix médian m²`, `Ventes avec prix`, `Évol. prix m² %`,
  `Écart vs département %`, `Mention volume`.

### B. Prix par département

- **Visuel** : Graphique à barres groupées. Position 712, 100, 552, 156.
- **Axe Y** : `dim_commune[nom_departement]`. **Axe X** : `Prix médian m²`.
  Tri : `Prix médian m²` décroissant.
- **Volet Analyse > Ligne X constante** : valeur **fx > Valeur du champ**
  `Prix médian m² Bretagne`, libellé « Bretagne », couleur `#52606D`, trait en pointillés.
- **Titre** : « Deux départements au-dessus de la médiane bretonne ».
- **Mise en forme** : couleur unique `#2B6F77`, étiquettes de données activées.

### C. Top 10 des hausses

- **Visuel** : Graphique à barres groupées. Position 712, 268, 272, 220.
- **Axe Y** : `dim_commune[libelle_commune]`. **Axe X** : `Évol. prix m² %`.
  Tri : `Évol. prix m² %` décroissant.
- **Filtre de ce visuel** sur `Rang hausse prix` (filtrage avancé) : **est inférieur ou
  égal à 10** **Et** **n'est pas vide**. Sans la seconde condition, les communes non
  éligibles (rang vide) s'afficheraient aussi.
- **Couleur** des barres : `#B5401A`.
- **Titre** : « 10 plus fortes hausses (20 ventes min.) ».
- **Info-bulles** : `Ventes avec prix`, `Prix médian m²`, `Prix médian m² N-1`.

### D. Top 10 des baisses

- Comme C, position 992, 268, 272, 220, avec `Rang baisse prix`, tri **croissant** sur
  `Évol. prix m² %`, couleur `#1565A8`.
- **Titre** : « 10 plus fortes baisses (20 ventes min.) ».

### E. Classement des communes

- **Visuel** : Tableau. Position 712, 500, 552, 184.
- **Colonnes** : `dim_commune[libelle_commune]`, `Prix médian m²`, `Ventes avec prix`,
  `Évol. prix m² %`, `Écart vs département %`. Tri : `Prix médian m²` décroissant.
- **Mise en forme conditionnelle** (couleur de police, Valeur du champ) :
  `Évol. prix m² %` avec `Couleur évol. prix`, `Écart vs département %` avec
  `Couleur écart département`.
- **Titre** : « Toutes les communes, de la plus chère à la moins chère ».
- Totaux désactivés.

**Drill-through** : un clic droit sur une commune dans A, C, D ou E propose **Extraire >
Fiche commune**.

---

## 4. Page 3 : Typologie des biens

Nom de la page : **Typologie des biens**. Titre de page : mesure `Titre typologie`.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Titre · navigation · segments                                                │
├──────────────────────────────────────────────────────────────────────────────┤
│ A  Part des maisons · Prix médian T3 · Prix médian maison 4-5 p.             │
├──────────────────────────────────────┬───────────────────────────────────────┤
│ B  Ventes par nombre de pièces       │ C  Ventes par tranche de surface      │
├──────────────────────────────────────┼───────────────────────────────────────┤
│ D  Distribution des prix au m²       │ E  Prix au m² par nombre de pièces    │
└──────────────────────────────────────┴───────────────────────────────────────┘
```

### A. Repères

- **Visuel** : Carte (nouvelle carte). Position 16, 100, 1248, 96.
- **Valeurs** : `Part maisons %`, `Prix médian T3`, `Prix médian maison 4-5 p.`. Ces
  mesures fixent elles-mêmes le type de bien : aucune interaction à modifier.

### B. Ventes par nombre de pièces

- **Visuel** : Histogramme groupé. Position 16, 208, 616, 232.
- **Axe X** : `fct_ventes[tranche_pieces]`. **Axe Y** : `Ventes avec prix`.
  **Légende** : `dim_type_bien[libelle_type_bien]` (Maison `#2B6F77`, Appartement
  `#B07A12`).
- **Titre** : « Les appartements vendus sont surtout des T3, les maisons des 5 pièces ».
- **Interaction** : ignore le segment Type de bien (section 6).

### C. Ventes par tranche de surface

- **Visuel** : Histogramme groupé. Position 648, 208, 616, 232.
- **Axe X** : `fct_ventes[tranche_surface]`. **Axe Y** : `Ventes avec prix`.
  **Légende** : `dim_type_bien[libelle_type_bien]`.
- **Titre** : « La plupart des appartements font 50 à 69 m², des maisons 90 à 119 m² ».
- **Interaction** : ignore le segment Type de bien.

### D. Distribution des prix au m²

- **Visuel** : Histogramme groupé. Position 16, 452, 616, 232.
- **Axe X** : `fct_ventes[tranche_prix_m2]` (type **Catégorie**). **Axe Y** :
  `Ventes avec prix`.
- **Couleur des colonnes** : **fx > Valeur du champ** `Couleur tranche médiane` : la tranche
  qui contient le prix médian ressort en foncé.
- **Mise en forme** : **espacement entre les catégories à 0** (aspect d'histogramme),
  étiquettes de l'axe X inclinées si besoin.
- **Titre** : « Une distribution étirée vers les prix élevés : d'où la médiane plutôt que
  la moyenne ».

### E. Prix au m² par nombre de pièces

- **Visuel** : Histogramme groupé. Position 648, 452, 616, 232.
- **Axe X** : `fct_ventes[tranche_pieces]`. **Axe Y** : `Prix médian m²`.
- **Couleur** : `#2B6F77`, étiquettes de données activées.
- **Titre** : « Appartements : le m² des petites surfaces coûte le plus cher ; maisons :
  c'est l'inverse ».
- **Info-bulles** : `Ventes avec prix`, `Mention volume`.

---

## 5. Page 4 : Fiche commune (drill-through)

Nom de la page : **Fiche commune**. Titre de page : mesure `Titre fiche commune`.

**Paramétrage de la page** (page sélectionnée, aucun visuel sélectionné, volet
**Visualisations > Extraire**) :

- champ d'extraction : **`dim_commune[libelle_commune]`** ;
- **Garder tous les filtres** : activé (année, type de bien et département suivent) ;
- **Interrapport** : désactivé.

Power BI ajoute un **bouton Retour** : le placer en 16, 8, 40, 40 et décaler le titre de page
en 64, 8, 1200, 40. Masquer la page : clic droit sur l'onglet > **Masquer la page**.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ← Titre (commune, type, année) · segments                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ A  Ventes · Prix médian au m² · Prix médian bien type · Écart vs département │
├─────────────────────────────────────┬────────────────────────────────────────┤
│ B  Prix au m² : commune et          │ C  Ventes par année                    │
│    département, par année           │                                        │
├─────────────────────────────────────┴────────────────────────────────────────┤
│ D  Fiche chiffrée                                                            │
└──────────────────────────────────────────────────────────────────────────────┘
```

### A. Cartes KPI

- Comme la page 1 (même position), avec les valeurs `Ventes`, `Prix médian m²`,
  `Prix médian bien type` et `Écart vs département %`. Étiquettes de référence : `Évol.
  ventes %` et `Évol. prix m² %` colorées comme en page 1 ; `Libellé bien type`. La valeur
  de `Écart vs département %` est colorée par `Couleur écart département`.

### B. Prix au m² de la commune et de son département

- **Visuel** : Graphique en courbes. Position 16, 224, 616, 268.
- **Axe X** : `dim_date[annee]` (type **Catégorie**, pour éviter les années décimales).
  **Axe Y** : `Prix médian m²` et `Prix médian m² département`.
- **Mise en forme** : commune `#2B6F77` en trait plein de 3 px, département `#52606D` en
  pointillés ; étiquettes de série activées. Une année sous le seuil laisse un trou dans la
  courbe.
- **Titre** : « Prix au m² de la commune et de son département ».
- **Interaction** : ignore le segment Année.

### C. Ventes par année

- **Visuel** : Histogramme groupé. Position 648, 224, 616, 268.
- **Axe X** : `dim_date[annee]` (Catégorie). **Axe Y** : `Ventes`. Couleur `#2B6F77`,
  étiquettes de données activées.
- **Titre** : « Nombre de ventes par année ».
- **Interaction** : ignore le segment Année.

### D. Fiche chiffrée

- **Visuel** : Matrice. Position 16, 504, 1248, 180.
- **Valeurs** : `Ventes`, `Évol. ventes %`, `Prix médian m²`, `Prix médian m² département`,
  `Écart vs département %`, `Prix médian bien type`, `Part maisons %`.
- **Format > Valeurs > Options > Basculer les valeurs vers les lignes** : activé (une ligne
  par indicateur).
- **Titre** : « La commune en chiffres, comparée à son département ».

Écart avec la maquette : celle-ci prévoyait trois colonnes (commune, département, écart)
pour chaque indicateur. Seul le prix au m² dispose d'une variante départementale ; la
matrice présente donc chaque indicateur une fois, le prix départemental et l'écart en
lignes dédiées, sans multiplier les mesures pour une seule table.

---

## 6. Page 5 : Méthodologie

Nom de la page : **Méthodologie**. Titre de page : texte fixe « D'où viennent les chiffres,
et ce qu'ils ne couvrent pas » (Zone de texte, mêmes position et police que les titres
dynamiques).

### A. Source et période

- **Visuel** : Zone de texte. Position 16, 100, 616, 268. Texte :

  > **Source** : Demandes de valeurs foncières (DVF) géolocalisées, publiées par la DGFiP
  > et Etalab sur data.gouv.fr, sous Licence Ouverte.
  >
  > **Périmètre** : ventes de maisons et d'appartements dans les 4 départements bretons,
  > signées de 2021 à 2025.
  >
  > **Mise à jour** : semestrielle, au rythme des publications de la DGFiP. Les ventes
  > apparaissent dans DVF environ 6 mois après leur signature.
  >
  > **Code, modèle de données et documentation** : dépôt GitHub du projet.

- Sous le texte, une **Carte** affichant `Texte source` (dates lues dans les données).

### B. Des actes notariés aux ventes analysées

- **Visuel** : Entonnoir. Position 648, 100, 616, 268.
- **Catégorie** : `mart_entonnoir_population[etape_libelle]`. **Valeurs** :
  `mart_entonnoir_population[nb_mutations]` (Somme).
- **Mise en forme** : couleur unique `#2B6F77`, étiquettes de données activées.
- **Titre** : « Sur 455 487 actes publiés, 216 900 ventes fondent les indicateurs de prix ».

### C. Définitions et règles

- **Visuel** : Zone de texte. Position 16, 380, 1248, 304. Texte :

  > **Médiane** : prix tel que la moitié des ventes se font en dessous. Elle résiste mieux
  > que la moyenne aux quelques ventes très chères.
  >
  > **Prix au m²** : prix de vente divisé par la surface bâtie du cadastre (et non la
  > surface Loi Carrez), pour les ventes d'un seul logement. Pour une maison, le prix
  > inclut le terrain.
  >
  > **Ventes exclues des prix** : ventes de plusieurs logements, valeur absente, surface
  > inférieure à 9 m², et 1 % des prix au m² les plus bas et les plus hauts de chaque
  > type de bien, département et année.
  >
  > **Seuils** : un prix n'est affiché qu'à partir de 10 ventes ; les tops 10 des hausses
  > et des baisses retiennent les communes d'au moins 20 ventes sur chacune des deux
  > années.
  >
  > **Hors périmètre** : ventes sur plan (VEFA), terrains, locaux professionnels.
  >
  > Les définitions complètes figurent dans le dictionnaire des KPI du projet.

---

## 7. Interactions à modifier

Sélectionner le segment, puis **Format > Modifier les interactions**, et cliquer sur
l'icône **Aucun** (⊘) au-dessus des visuels concernés :

| Page | Segment | Visuels qui l'ignorent |
|---|---|---|
| Vue d'ensemble | Année | B, C |
| Typologie des biens | Type de bien | B, C |
| Fiche commune | Année | B, C |

---

## 8. Vérifications finales

| Critère (dashboard-spec, section 9) | Comment le vérifier |
|---|---|
| Chaque question trouve sa réponse en 3 clics au plus | Q1 et Q4 : Géographie (1 clic) ; Q2 : Vue d'ensemble (0) ; Q3 : Géographie puis clic droit > Extraire (2) ; Q5 : Typologie (1). |
| Aucun prix sous le seuil | Choisir une petite commune via le drill-through : le titre indique « moins de 10 ventes » et les cartes de prix sont vides. |
| Concordance avec dbt | Maison 2025, tous départements : `Ventes` = 32 843, `Prix médian m²` = 2 290 € (contrôle du guide de construction, section 12.4). |
| 4 à 6 visuels par page | Hors en-tête et pied de page : 4, 5, 5, 4 et 3 visuels. |
| Lecture en Z | Cartes KPI en haut, tendances au milieu, détail en bas, sur les pages 1, 3 et 4. |
