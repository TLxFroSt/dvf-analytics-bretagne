# Dictionnaire des KPI

Ce document définit chaque indicateur du dashboard : ce qu'il mesure, comment il est calculé,
sur quelle population, et comment le lire. Il fait référence : les modèles dbt et les mesures
DAX l'implémentent tel quel, et chaque mesure Power BI reprend sa description.

Le contexte (public, questions métier, périmètre) est décrit dans
[dashboard-spec.md](dashboard-spec.md).

**Sommaire**

1. [Règles de population](#1-règles-de-population)
2. [Seuils de volume](#2-seuils-de-volume)
3. [Conventions communes](#3-conventions-communes)
4. [Indicateurs de volume](#4-indicateurs-de-volume)
5. [Indicateurs de prix](#5-indicateurs-de-prix)
6. [Indicateurs comparatifs](#6-indicateurs-comparatifs)

Les volumes cités proviennent des données 2021-2025 pour les 4 départements bretons.

---

## 1. Règles de population

Les indicateurs reposent sur deux populations emboîtées, construites dans dbt à partir
des lignes brutes de DVF. Ces règles ne sont **jamais** réappliquées ni modifiées dans le
dashboard.

### R1. Grain mutation

Une **mutation** est un acte notarié (`id_mutation`). Dans la source, une mutation s'étend
sur plusieurs lignes : une par local, par parcelle et par disposition. Toutes les lignes sont
regroupées en **une ligne par mutation** avant tout calcul.

La valeur foncière est répétée à l'identique sur chaque ligne d'une mutation : elle est
prise **une seule fois**, jamais additionnée. Sur les 455 487 mutations de la période,
aucune ne porte deux valeurs différentes, y compris les 2 758 qui comptent plusieurs
dispositions ; un test dbt vérifie que cela reste vrai à chaque mise à jour.

### R2. Ventes uniquement

Seules les mutations de nature `Vente` sont retenues.

Sont exclues : les ventes en l'état futur d'achèvement (VEFA, 21 714 mutations, dont 98 %
sans description du logement vendu), les échanges, les adjudications, les expropriations et
les ventes de terrains à bâtir.

### R3. Population « ventes de logement » (indicateurs de volume)

Une vente de logement est une vente (R2) qui comprend :

- au moins une maison ou un appartement, **d'un seul type** (que des maisons ou que des
  appartements) ;
- aucun local industriel ou commercial ;
- un nombre quelconque de dépendances (garage, cave, parking).

Son **type de bien** est celui de ses logements : Maison ou Appartement.

| Ventes (R2) | 424 243 |
|---|---:|
| Sans logement (terrain, dépendance seule) | − 147 688 |
| Avec un local industriel ou commercial | − 7 577 |
| Mêlant maisons et appartements | − 636 |
| **Ventes de logement** | **268 342** |

Une vente de plusieurs logements (46 776 cas, immeubles et lots de maisons) compte pour
**une** vente : l'unité de compte est l'acte, pas le logement.

### R4. Population « prix » (indicateurs de prix)

Sous-ensemble des ventes de logement (R3) qui remplissent toutes les conditions suivantes :

1. **un seul logement** (une maison ou un appartement), avec ou sans dépendances : c'est la
   seule configuration où le prix est attribuable à un logement identifié ;
2. une valeur foncière renseignée ;
3. une surface réelle bâtie d'au moins **9 m²** (surface minimale d'un logement décent) ;
4. un prix au m² compris entre le **1er et le 99e percentile** de son groupe
   *type de bien × département × année* (règle R5).

| Étape | Mutations |
|---|---:|
| Ventes d'un seul logement sans local professionnel | 221 566 |
| Valeur absente ou surface < 9 m² | − 206 |
| Prix au m² hors de l'intervalle P1-P99 de son groupe | − 4 459 |
| **Population prix** | **216 901** |

Les lignes de source strictement identiques (environ 7 % des lignes) sont comptées comme
des locaux distincts. Une vente dont le logement apparaît deux fois est donc considérée
comme portant sur deux logements et sort de la population prix : 577 mutations, soit
0,26 %, écartées par prudence plutôt qu'interprétées.

### R5. Exclusion des valeurs aberrantes

Le prix au m² est la valeur foncière divisée par la surface réelle bâtie. Dans chaque groupe
*type de bien × département × année*, les ventes dont le prix au m² est inférieur au
1er percentile ou supérieur au 99e percentile sont exclues de la population prix.

- **Pourquoi des percentiles** : la distribution brute contient des valeurs sans rapport avec
  le marché (prix symboliques entre proches, ruines, erreurs de saisie) : 5 €/m² au
  0,1e percentile des maisons, près de 13 000 €/m² au 99,9e. Un seuil fixe en euros ne
  conviendrait pas à toutes les zones ni à toutes les années.
- **Pourquoi par département** : les niveaux de prix diffèrent fortement entre départements
  (médiane 2025 des appartements : 2 254 €/m² dans le Finistère, 3 380 €/m² en
  Ille-et-Vilaine). Des bornes régionales retireraient des ventes ordinaires des
  départements les plus chers ou les moins chers.
- **Pourquoi par année** : les bornes suivent l'évolution du marché.
- **Effet** : environ 2 % des ventes exclues. Les bornes 2025 vont par exemple de 696 à
  6 802 €/m² pour les appartements des Côtes-d'Armor.

Les ventes exclues restent comptées dans les indicateurs de volume.

---

## 2. Seuils de volume

Un indicateur calculé sur trop peu de ventes est instable : une seule vente atypique suffit
à le déplacer. En dessous du seuil, la mesure renvoie une **valeur vide** et le visuel
affiche une mention explicite (« Moins de 10 ventes »), jamais un chiffre fragile.

| Indicateurs | Condition d'affichage | Justification |
|---|---|---|
| Prix médians (au m², bien type) | ≥ **10** ventes de la population prix dans le contexte | Au niveau commune × année × type, ce seuil affiche 40 % des couples (appartements) et 65 % (maisons), qui couvrent 92 à 95 % des ventes. |
| Évolutions N-1 de prix | Seuil de 10 atteint **à la fois** en N et en N-1 | Une évolution compare deux médianes : chacune doit être fiable. |
| Évolution N-1 des ventes, part des maisons | ≥ **10** ventes de logement en N-1 (évolution) ou en N (part) | Un pourcentage calculé sur quelques ventes n'a pas de sens. |
| Top 10 des hausses et des baisses | ≥ **20** ventes de la population prix en N **et** en N-1 | Un classement met en avant les valeurs extrêmes, donc les plus sensibles au bruit : le seuil est plus exigeant. |

---

## 3. Conventions communes

- **Période** : l'année et le trimestre se rapportent à la date de signature de l'acte. Les
  années 2021 à 2025 sont complètes.
- **Évolution N-1** : comparaison de la période sélectionnée avec la même période décalée
  d'un an (une année avec l'année précédente, un trimestre avec le même trimestre de
  l'année précédente). Vide pour 2021, faute de données 2020.
- **Médiane, pas moyenne** : la distribution des prix est asymétrique (quelques biens très
  chers tirent la moyenne vers le haut). La médiane est le prix tel que la moitié des ventes
  se font en dessous et la moitié au-dessus.
- **Maisons et appartements toujours séparés pour les prix** : leurs prix au m² ne sont pas
  comparables, et une médiane mélangeant les deux varierait avec la seule proportion de
  maisons vendues. Une mesure de prix générique renvoie une valeur vide si les deux types
  sont présents dans le contexte de filtre.
- **Filtres** : sauf mention contraire, chaque indicateur répond aux filtres du bandeau
  (année, département, type de bien) et à la sélection de communes.
- **Format** : nombres au format français (1 234 ; 2 766 €/m² ; +3,2 %). Évolutions
  arrondies à 0,1 point, prix à l'euro près.

Les **noms de mesures DAX** sont ceux de la table de mesures Power BI. La **description
Power BI** est le texte affiché en info-bulle dans la liste des champs.

---

## 4. Indicateurs de volume

### Ventes

| | |
|---|---|
| **Définition** | Nombre de ventes de logement signées sur la période. |
| **Formule** | Nombre de mutations de la population R3. |
| **Population** | Ventes de logement (R3). |
| **Seuil** | Aucun. |
| **Lecture** | Mesure la liquidité du marché : un volume en baisse signale un marché qui se grippe, souvent avant que les prix ne reculent. |
| **Piège** | Compte des actes, pas des logements : la vente d'un immeuble de 10 appartements compte pour 1. |
| **Mesure DAX** | `Ventes` (dossier Volumes) |
| **Description Power BI** | Nombre de ventes de maisons ou d'appartements (actes de vente, hors VEFA et hors ventes avec local professionnel). |

### Ventes N-1

| | |
|---|---|
| **Définition** | Nombre de ventes de logement sur la même période un an plus tôt. |
| **Formule** | `Ventes` évaluée sur la période décalée d'un an. |
| **Population** | Ventes de logement (R3). |
| **Seuil** | Aucun. |
| **Lecture** | Base de comparaison de l'évolution des ventes. |
| **Mesure DAX** | `Ventes N-1` (dossier Volumes) |
| **Description Power BI** | Nombre de ventes sur la même période de l'année précédente. |

### Évolution des ventes vs N-1

| | |
|---|---|
| **Définition** | Variation relative du nombre de ventes par rapport à la même période un an plus tôt. |
| **Formule** | (`Ventes` − `Ventes N-1`) / `Ventes N-1` |
| **Population** | Ventes de logement (R3). |
| **Seuil** | Vide si `Ventes N-1` < 10. |
| **Lecture** | +10 % : il s'est signé 10 % d'actes de plus que l'an dernier sur la même période. Couleur d'accent hausse ou baisse selon le signe. |
| **Piège** | Les volumes 2021-2022 sont historiquement élevés (rattrapage post-confinement, taux bas) : la forte baisse de 2023 reflète en partie ce point haut. |
| **Mesure DAX** | `Évol. ventes %` (dossier Évolutions) |
| **Description Power BI** | Variation du nombre de ventes par rapport à la même période de l'année précédente. Vide si moins de 10 ventes l'année précédente. |

### Part des maisons

| | |
|---|---|
| **Définition** | Proportion de maisons parmi les ventes de logement. |
| **Formule** | `Ventes` (type Maison) / `Ventes` (tous types) |
| **Population** | Ventes de logement (R3). |
| **Filtres** | Ignore le filtre de type de bien (sinon la part vaudrait toujours 0 ou 100 %). |
| **Seuil** | Vide si `Ventes` < 10. |
| **Lecture** | Caractérise le tissu : proche de 100 % en zone rurale ou périurbaine, nettement plus bas dans les villes-centres. Éclaire la lecture des prix : un marché d'appartements et un marché de maisons ne se comparent pas directement. |
| **Mesure DAX** | `Part maisons %` (dossier Volumes) |
| **Description Power BI** | Part des maisons dans le nombre de ventes de logement. Ignore le filtre de type de bien. Vide si moins de 10 ventes. |

---

## 5. Indicateurs de prix

### Ventes avec prix

| | |
|---|---|
| **Définition** | Nombre de ventes sur lesquelles repose un indicateur de prix. |
| **Formule** | Nombre de mutations de la population prix (R4). |
| **Population** | Population prix (R4). |
| **Seuil** | Aucun : c'est la mesure sur laquelle les seuils s'appuient. |
| **Lecture** | Affichée en info-bulle à côté de chaque prix, pour que l'utilisateur juge de sa solidité. |
| **Mesure DAX** | `Ventes avec prix` (dossier Volumes) |
| **Description Power BI** | Nombre de ventes d'un seul logement retenues pour les indicateurs de prix, après exclusion des valeurs aberrantes. |

### Prix médian au m²

| | |
|---|---|
| **Définition** | Prix au m² tel que la moitié des ventes de la période se font en dessous. |
| **Formule** | Médiane de (valeur foncière / surface réelle bâtie) sur la population prix. |
| **Population** | Population prix (R4). |
| **Filtres** | Un seul type de bien dans le contexte, sinon vide (voir conventions). Deux variantes à type fixé pour les cartes KPI. |
| **Seuil** | Vide si `Ventes avec prix` < 10. |
| **Lecture** | Niveau de prix d'un secteur. 2 766 €/m² pour les appartements : la moitié des appartements se sont vendus moins de 2 766 € par m² bâti. |
| **Pièges** | Pour une maison, le prix inclut le terrain : une commune aux grands terrains affiche un prix au m² bâti plus élevé à bâti égal. La médiane varie aussi avec la composition des ventes (plus de petites surfaces, plus chères au m², la font monter sans hausse des prix). |
| **Mesures DAX** | `Prix médian m²`, `Prix médian m² appartements`, `Prix médian m² maisons` (dossier Prix) |
| **Description Power BI** | Médiane du prix au m² bâti des ventes d'un seul logement, hors valeurs aberrantes. Vide si moins de 10 ventes ou si maisons et appartements sont mélangés. |

### Prix médian au m² N-1

| | |
|---|---|
| **Définition** | Prix médian au m² sur la même période un an plus tôt. |
| **Formule** | `Prix médian m²` évalué sur la période décalée d'un an. |
| **Population** | Population prix (R4). |
| **Seuil** | Vide si moins de 10 ventes avec prix en N-1. |
| **Mesure DAX** | `Prix médian m² N-1` (dossier Prix) |
| **Description Power BI** | Prix médian au m² sur la même période de l'année précédente. |

### Évolution du prix médian au m² vs N-1

| | |
|---|---|
| **Définition** | Variation relative du prix médian au m² par rapport à la même période un an plus tôt. |
| **Formule** | (`Prix médian m²` − `Prix médian m² N-1`) / `Prix médian m² N-1` |
| **Population** | Population prix (R4). |
| **Seuil** | Vide si l'une des deux médianes est vide (moins de 10 ventes en N ou en N-1). |
| **Lecture** | −3 % : le prix au m² médian est inférieur de 3 % à celui de l'an dernier. Couleur d'accent hausse ou baisse selon le signe. |
| **Piège** | À l'échelle d'une commune, une variation de quelques pourcents sur 10 à 20 ventes peut relever du bruit statistique : l'info-bulle affiche le nombre de ventes des deux périodes. |
| **Mesure DAX** | `Évol. prix m² %` (dossier Évolutions) |
| **Description Power BI** | Variation du prix médian au m² par rapport à la même période de l'année précédente. Vide si moins de 10 ventes sur l'une des deux périodes. |

### Prix médian d'un bien type

| | |
|---|---|
| **Définition** | Prix total médian d'un logement représentatif : un appartement T3 et une maison de 4 ou 5 pièces. |
| **Formule** | Médiane de la valeur foncière, sur la population prix restreinte aux appartements de 3 pièces principales, ou aux maisons de 4 ou 5 pièces principales. |
| **Population** | Population prix (R4) restreinte au bien type. |
| **Filtres** | Type de bien fixé par la mesure. |
| **Seuil** | Vide si moins de 10 ventes du bien type. |
| **Lecture** | Répond directement à « quel budget prévoir ? ». Plus parlant qu'un prix au m² pour un acheteur. Volumes disponibles : 4 000 à 6 000 T3 et 13 000 à 20 000 maisons de 4-5 pièces par an en Bretagne. |
| **Piège** | Prix hors frais de notaire (environ 7 à 8 % en plus dans l'ancien). Dépendances éventuelles incluses. |
| **Mesures DAX** | `Prix médian T3`, `Prix médian maison 4-5 p.` (dossier Prix) |
| **Description Power BI** | Prix médian de vente d'un appartement de 3 pièces (respectivement d'une maison de 4 ou 5 pièces), hors frais de notaire et hors valeurs aberrantes. Vide si moins de 10 ventes. |

---

## 6. Indicateurs comparatifs

### Écart du prix médian au m² vs le département

| | |
|---|---|
| **Définition** | Écart relatif entre le prix médian au m² d'une commune et celui de son département, à type de bien et période identiques. |
| **Formule** | (`Prix médian m²` de la commune − `Prix médian m² département`) / `Prix médian m² département` |
| **Population** | Population prix (R4). La médiane départementale porte sur toutes les ventes du département, commune comprise, en ignorant la sélection de communes. |
| **Filtres** | N'a de sens qu'au niveau d'une commune : vide si plusieurs communes sont dans le contexte. Un seul type de bien requis. |
| **Seuil** | Vide si la commune a moins de 10 ventes avec prix. |
| **Lecture** | +25 % : le m² y coûte un quart de plus que la médiane du département. Situe une commune sans connaître les niveaux de prix bretons. |
| **Mesures DAX** | `Prix médian m² département`, `Écart vs département %` (dossiers Prix et Évolutions) |
| **Description Power BI** | Écart du prix médian au m² de la commune par rapport à la médiane de son département, même type de bien et même période. Vide si moins de 10 ventes dans la commune. |

### Top 10 des communes en hausse et en baisse

| | |
|---|---|
| **Définition** | Les 10 communes dont le prix médian au m² a le plus augmenté, et les 10 dont il a le plus baissé, par rapport à l'année précédente. |
| **Formule** | Classement des communes éligibles selon `Évol. prix m² %` : les 10 plus fortes valeurs pour les hausses, les 10 plus faibles pour les baisses. En cas d'égalité, la commune au plus grand nombre de ventes passe devant. |
| **Population** | Population prix (R4). |
| **Éligibilité** | ≥ 20 ventes avec prix en N **et** en N-1, pour le type de bien sélectionné. |
| **Filtres** | Une année et un seul type de bien sélectionnés. Le classement s'effectue parmi les communes des départements filtrés. |
| **Lecture** | Repère les secteurs en tension ou en repli. À lire avec le nombre de ventes (affiché) : un fort mouvement sur 20 ventes est moins certain que sur 200. |
| **Piège** | Les classements d'évolutions surreprésentent mécaniquement les petites communes, les plus volatiles : c'est la raison du seuil de 20 ventes. |
| **Mesure DAX** | `Commune éligible top` (dossier Évolutions), utilisée en filtre de visuel avec un filtre Top N sur `Évol. prix m² %` |
| **Description Power BI** | Vaut 1 si la commune compte au moins 20 ventes avec prix l'année sélectionnée et l'année précédente, sinon vide. |
