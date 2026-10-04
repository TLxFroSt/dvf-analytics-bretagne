# Thème Power BI « DVF Bretagne »

Fichier : [`dvf-bretagne.json`](dvf-bretagne.json), validé contre le schéma officiel des
thèmes Power BI (`reportThemeSchema-2.149`).

**Appliquer** : Power BI Desktop, **Affichage > Thèmes > Parcourir les thèmes**, choisir
`dvf-bretagne.json`.

## Palette

| Rôle | Couleur | Usage |
|---|---|---|
| Série 1 | `#2B6F77` sarcelle | **Maisons**, 1er département |
| Série 2 | `#B07A12` ambre | **Appartements**, 2e département |
| Série 3 | `#4A4A8A` indigo | 3e département |
| Série 4 | `#5C3D2E` brun | 4e département |
| Séries 5 à 8 | `#7A5C99`, `#5B7F2A`, `#3E4C59`, `#9C5A44` | Réserve (non utilisées par la maquette) |
| **Hausse** | `#B5401A` vermillon | Évolutions positives (texte, barres du top 10 des hausses) |
| **Baisse** | `#1565A8` bleu | Évolutions négatives (texte, barres du top 10 des baisses) |
| Valeur masquée | `#C5CCD3` (remplissage), `#616E7C` (texte) | Moins de ventes que le seuil : communes grises sur la carte, mention « Moins de 10 ventes » |
| Échelle séquentielle | `#E3F1F0` → `#6FA8A6` → `#12464C` | Carte des prix au m² (niveau, du moins cher au plus cher) |
| Texte | `#1F2933` principal, `#52606D` secondaire | Titres, étiquettes |
| Fonds | `#F5F7FA` page, `#FFFFFF` visuels, `#D9E2EC` bordures | Visuels en cartes blanches sur fond gris clair |

Les couleurs de hausse et de baisse ne sont pas dans la palette des séries : elles sont
portées par des mesures DAX de mise en forme conditionnelle, pour que leur sens reste le
même partout. Elles sont toujours **accompagnées d'un signe** (▲ +3,2 % / ▼ −1,5 %) :
l'information ne repose jamais sur la couleur seule.

Le vermillon et le bleu sont **neutres** : une hausse des prix n'est ni bonne ni mauvaise en
soi (favorable à un vendeur, défavorable à un acheteur). Le vert et le rouge, qui portent
un jugement, sont donc évités, tout comme leur confusion fréquente chez les personnes
daltoniennes.

## Accessibilité

Les contrôles se relancent après toute modification de la palette :

```powershell
uv run python powerbi/theme/check_palette.py
```

| Contrôle | Seuil | Résultat |
|---|---|---|
| Contraste du texte (y compris hausse, baisse, valeur masquée) sur les deux fonds | 4,5:1 (WCAG 2.1 AA) | de 4,86:1 à 13,75:1 |
| Contraste des marques graphiques sur fond blanc | 3:1 (WCAG 2.1, critère 1.4.11) | de 3,72:1 à 9,71:1 |
| Distinction hausse / baisse, vision normale et 3 formes de daltonisme | ΔE ≥ 20 | pire cas 78,4 (protanopie) |
| Distinction des 4 premières séries, vision normale et 3 formes de daltonisme | ΔE ≥ 20 | pire cas 20,9 (tritanopie) |

Les 4 premières séries ont été choisies par une recherche systématique parmi des couleurs
de contraste suffisant, pour maximiser leur écart minimal dans les quatre visions.
En complément, les courbes des départements portent des **étiquettes directes** plutôt
qu'une légende (voir les spécifications des pages).

## Styles par défaut

- Polices Segoe UI (la police système de Windows, lisible à petite taille) : valeurs des
  cartes KPI en 26 pt semi-gras, titres de visuels en 12 pt semi-gras alignés à gauche,
  étiquettes en 10 pt.
- Visuels sur fond blanc, bordure fine `#D9E2EC` aux coins arrondis (6 px), sans ombre.
- Pages sur fond gris très clair `#F5F7FA`, pour détacher les visuels.
