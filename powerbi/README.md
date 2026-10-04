# Power BI : construction du modèle sémantique

Ce guide construit, dans Power BI Desktop, le modèle en étoile produit par dbt : 4 tables du
schéma en étoile et 2 tables de méthodologie, lues depuis les exports Parquet. Il se suit
une fois, à la création du projet ; ensuite, une mise à jour des données se résume à
`dbt build` puis **Actualiser**.

Les mesures DAX, le thème et les visuels font l'objet d'étapes suivantes
(`measures.tmdl`, `theme/`, `docs/powerbi-pages.md`).

Les libellés de menus sont ceux de Power BI Desktop en français (version novembre 2025).

---

## 1. Prérequis

1. **Power BI Desktop** novembre 2025 ou plus récent.
2. **Les exports Parquet à jour** : depuis la racine du projet,

   ```powershell
   cd dbt; uv run dbt build; cd ..
   ```

   Le dossier `exports/` doit contenir 6 fichiers `.parquet`.

## 2. Options de Power BI Desktop

**Fichier > Options et paramètres > Options**

| Section | Option | Valeur | Pourquoi |
|---|---|---|---|
| GLOBAL > Fonctionnalités en préversion | Visuel Carte de formes (*Shape map*) | ✅ Activé | Carte des communes de la page Géographie. **Redémarrer Power BI** après activation. |
| GLOBAL > Fonctionnalités en préversion | Format de rapport Power BI amélioré (PBIR) | ✅ Activé (déjà le cas) | Rapport enregistré en fichiers texte lisibles, versionnables dans Git. |
| FICHIER ACTUEL > Paramètres régionaux | Paramètres régionaux pour l'importation | Français (France) | Formats de nombres et de dates à la française. |
| FICHIER ACTUEL > Chargement des données | Date/heure automatique | ❌ Désactivé | `dim_date` est la seule table de dates : les tables de dates cachées que Power BI crée pour chaque colonne date alourdiraient le modèle. |
| FICHIER ACTUEL > Chargement des données | Détecter automatiquement les nouvelles relations après le chargement des données | ❌ Désactivé | Les relations sont créées à la main (section 6), pour éviter toute relation devinée à tort. |

## 3. Créer le projet PBIP

1. Nouveau rapport vide.
2. **Fichier > Enregistrer sous**, type **Fichiers de projet Power BI (\*.pbip)**.
3. Dossier `powerbi/` du dépôt, nom **`dvf-bretagne`**.

Power BI crée `dvf-bretagne.pbip`, `dvf-bretagne.SemanticModel/` (modèle au format TMDL) et
`dvf-bretagne.Report/`. Le cache local (`.pbi/cache.abf`) et les paramètres utilisateur
(`.pbi/localSettings.json`) sont exclus de Git par `.gitignore`.

## 4. Paramètre du chemin des exports

Le chemin des fichiers Parquet est un **paramètre** : sur une autre machine, il suffit de le
modifier, sans toucher aux requêtes.

**Accueil > Transformer les données** (ouvre Power Query), puis
**Gérer les paramètres > Nouveau paramètre** :

| Champ | Valeur |
|---|---|
| Nom | `CheminExports` |
| Description | Dossier des exports Parquet produits par dbt (avec la barre oblique finale) |
| Obligatoire | ✅ |
| Type | Texte |
| Valeurs suggérées | N'importe quelle valeur |
| Valeur actuelle | `C:\ClaudeProjects\dvf-analytics-bretagne\exports\` |

La barre oblique inverse finale est nécessaire : les requêtes y ajoutent le nom du fichier.

## 5. Requêtes des 6 tables

Pour chaque table : **Nouvelle source > Requête vide**, puis **Éditeur avancé**, coller le
code, valider, et **renommer la requête** avec le nom indiqué (clic droit > Renommer).
Les noms reprennent ceux des modèles dbt : chaque table Power BI se retrouve telle quelle
dans la documentation dbt.

Modèle de code, où seul le nom du fichier change :

```powerquery
let
    Source = Parquet.Document(File.Contents(CheminExports & "fct_ventes.parquet"))
in
    Source
```

| Requête | Fichier | Lignes attendues |
|---|---|---:|
| `fct_ventes` | `fct_ventes.parquet` | 268 341 |
| `dim_date` | `dim_date.parquet` | 1 826 |
| `dim_commune` | `dim_commune.parquet` | 1 202 |
| `dim_type_bien` | `dim_type_bien.parquet` | 2 |
| `mart_entonnoir_population` | `mart_entonnoir_population.parquet` | 6 |
| `mart_metadonnees` | `mart_metadonnees.parquet` | 1 |

Les types de colonnes sont lus dans le Parquet (texte, nombre entier, nombre décimal, date,
vrai/faux) : aucune étape de typage n'est nécessaire. Vérifier tout de même, dans l'aperçu
de `fct_ventes`, que `date_mutation` est de type **Date** et `prix_m2` de type
**Nombre décimal**.

Le paramètre `CheminExports` ne doit pas être chargé dans le modèle : clic droit sur
le paramètre > décocher **Activer le chargement** (normalement décoché par défaut).

**Fermer et appliquer.**

## 6. Relations

**Vue Modèle > Gérer les relations > Nouveau**. Trois relations, toutes **plusieurs à un
(\*:1)**, **direction du filtre croisé : Unique** (les dimensions filtrent les faits, jamais
l'inverse), **active** :

| De (côté plusieurs) | Vers (côté un) |
|---|---|
| `fct_ventes[date_mutation]` | `dim_date[date_jour]` |
| `fct_ventes[commune_key]` | `dim_commune[commune_key]` |
| `fct_ventes[type_bien_key]` | `dim_type_bien[type_bien_key]` |

`mart_entonnoir_population` et `mart_metadonnees` restent **sans relation** : ce sont des
tables autonomes de la page Méthodologie.

## 7. Table de dates

Sélectionner `dim_date`, puis **Outils de table > Marquer comme table de dates**, colonne
**`date_jour`**. Les fonctions d'intelligence temporelle des mesures (N-1) s'appuient
dessus.

## 8. Tri des libellés

Sans ce réglage, Power BI trie les libellés par ordre alphabétique (« 120 à 149 m² » avant
« 30 à 49 m² »). Sélectionner la colonne, puis **Outils de colonne > Trier par colonne**.
Chaque libellé doit correspondre à une seule valeur de tri : le nom du mois se trie donc par
le numéro du mois (1 à 12), pas par `tri_mois` (« janvier » y prend une valeur par année).

| Table | Colonne | Trier par |
|---|---|---|
| `dim_date` | `libelle_trimestre` | `tri_trimestre` |
| `dim_date` | `nom_mois` | `mois` |
| `dim_type_bien` | `libelle_type_bien` | `ordre_tri` |
| `dim_type_bien` | `libelle_type_bien_pluriel` | `ordre_tri` |
| `fct_ventes` | `tranche_surface` | `tranche_surface_ordre` |
| `fct_ventes` | `tranche_pieces` | `tranche_pieces_ordre` |
| `fct_ventes` | `tranche_prix_m2` | `tranche_prix_m2_ordre` |

## 9. Synthèse des colonnes numériques

Power BI additionne par défaut toute colonne numérique glissée dans un visuel, ce qui n'a
aucun sens pour une année ou un code. Pour chaque colonne ci-dessous :
**Outils de colonne > Synthèse > Ne pas résumer**.

- `dim_date` : `annee`, `trimestre`, `mois`
- `dim_type_bien` : `code_type_bien`
- `dim_commune` : `population`
- `mart_entonnoir_population` : `etape_ordre`

Les colonnes numériques de `fct_ventes` (prix, surfaces) ne s'utilisent pas directement :
les visuels passent toujours par les mesures, qui appliquent les règles du dictionnaire des
KPI (médiane, population prix, seuils).

## 10. Colonnes masquées

Clic droit > **Masquer dans la vue rapport**. La liste des champs ne montre ainsi que ce
qu'un concepteur de visuels doit utiliser.

| Table | Colonnes à masquer | Raison |
|---|---|---|
| `fct_ventes` | `vente_key`, `commune_key`, `type_bien_key`, `date_mutation` | Clés techniques : on filtre par les dimensions. |
| `fct_ventes` | `tranche_surface_ordre`, `tranche_pieces_ordre`, `tranche_prix_m2_ordre` | Colonnes de tri. |
| `fct_ventes` | `valeur_fonciere`, `nb_logements`, `nb_dependances`, `surface_bati_m2`, `nb_pieces`, `surface_terrain_m2`, `prix_m2`, `est_population_prix` | Utilisées par les mesures uniquement : une somme ou une moyenne de ces colonnes contredirait les règles du dictionnaire. |
| `dim_date` | `tri_trimestre`, `tri_mois` | Colonnes de tri. |
| `dim_commune` | `commune_key` | Clé technique. |
| `dim_type_bien` | `type_bien_key`, `ordre_tri` | Clé technique, colonne de tri. |

Restent visibles dans `fct_ventes` : `id_mutation` (traçabilité vers DVF),
`motif_exclusion_prix` et les trois libellés de tranches.

## 11. Vérifications

Dans la **Vue de table**, le nombre de lignes de chaque table (en bas de l'écran) doit
correspondre au tableau de la section 5. Dans la **Vue Modèle**, le schéma doit montrer
`fct_ventes` au centre, reliée aux trois dimensions par des relations 1-\* à flèche unique,
et les deux tables de méthodologie à l'écart.

Enregistrer (**Ctrl+S**). Dans le dépôt, `git status` doit faire apparaître
`powerbi/dvf-bretagne.pbip`, `powerbi/dvf-bretagne.SemanticModel/` et
`powerbi/dvf-bretagne.Report/`, mais **aucun** `cache.abf` ni `localSettings.json`.

## 12. Mesures DAX

Les 32 mesures sont définies dans [`measures.tmdl`](measures.tmdl), avec leur formule, leur
description (reprise du dictionnaire des KPI), leur format et leur dossier d'affichage.
Elles s'installent en une fois par la vue TMDL de Power BI Desktop.

### 12.1 Créer la table de mesures

1. **Accueil > Entrer des données**.
2. Nommer la table **`Mesures`** (en bas de la fenêtre), laisser la colonne par défaut vide.
3. **Charger**.

### 12.2 Coller le script

1. Ouvrir la **vue TMDL** (icône `</>` dans la barre de gauche, sous la Vue Modèle).
2. Coller tout le contenu de `measures.tmdl` dans l'onglet de script.
3. Cliquer sur **Appliquer**. Power BI signale les éventuelles erreurs de syntaxe avec leur
   numéro de ligne, sans rien modifier tant que le script n'est pas valide.

### 12.3 Finaliser

1. Masquer la colonne par défaut de la table `Mesures` (clic droit > **Masquer dans la vue
   rapport**). Une table dont toutes les colonnes sont masquées et qui contient des mesures
   prend l'icône de calculatrice et remonte en tête du volet Données.
2. **Ctrl+S**.

Le script reste dans le dépôt comme installation de référence ; une fois appliqué, les
mesures font partie du modèle (`dvf-bretagne.SemanticModel/definition/tables/Mesures.tmdl`),
qui devient la source à faire évoluer.

### 12.4 Contrôler les valeurs

Sur une page vide, placer un segment sur `dim_date[annee]` (2025) et un sur
`dim_type_bien[libelle_type_bien]`, puis une carte par mesure. Les valeurs attendues ont été
calculées indépendamment, en SQL sur les exports Parquet :

| Mesure | Maison, 2025 | Appartement, 2025 |
|---|---:|---:|
| `Ventes` | 32 843 | 15 058 |
| `Ventes N-1` | 30 846 | 13 239 |
| `Évol. ventes %` | ▲ +6,5 % | ▲ +13,7 % |
| `Prix médian m²` | 2 290 € | 2 915 € |
| `Prix médian m² N-1` | 2 233 € | 2 836 € |
| `Évol. prix m² %` | ▲ +2,6 % | ▲ +2,8 % |
| `Prix médian bien type` | 230 000 € | 178 100 € |
| `Part maisons %` | 69 % | 69 % (ignore le type) |
| `Titre typologie` | Maisons en 2025 : la moitié des ventes se fait entre 1 640 et 3 010 €/m² | |
| `Titre géographie` | | Appartements en 2025 : le prix au m² le plus élevé est à La Trinité-sur-Mer (56) (5 927 €/m²) |

Avec un segment supplémentaire sur `dim_commune[libelle_commune]` = **Vannes (56)**,
appartements 2025 : `Prix médian m²` = 3 885 €, `Prix médian m² département` = 3 333 €,
`Écart vs département %` = +17 %.

Tops 10 des appartements en 2025 (tableau par `libelle_commune`, filtre de visuel sur le
rang) : `Rang hausse prix` 1 à 3 = Landivisiau (+26,2 %), Vern-sur-Seiche (+21,9 %),
Guingamp (+21,9 %), et rang 10 = Pont-l'Abbé (+12,4 %) ; `Rang baisse prix` 1 à 3 = Guidel
(−41,1 %), Fouesnant (−29,0 %), Sarzeau (−11,6 %).

> **Piège du filtre de rang** : Power BI traite une valeur vide comme 0, si bien que le
> filtre « est inférieur ou égal à 10 » conserve aussi les communes **non éligibles**, dont
> le rang est vide. Le filtre de visuel doit combiner deux conditions : **est inférieur ou
> égal à 10** **Et** **n'est pas vide**.

## Mise à jour des données

1. `uv run python ingestion/download.py` (télécharge les nouvelles publications DVF).
2. `cd dbt; uv run dbt build` (reconstruit les marts et les exports Parquet).
3. Power BI : **Accueil > Actualiser**.
