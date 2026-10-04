"""Contrôle d'accessibilité de la palette du thème Power BI.

Vérifie, pour les couleurs du thème `dvf-bretagne.json` et les couleurs sémantiques des
mesures DAX (hausse, baisse, valeur masquée) :

- le contraste WCAG 2.1 avec les fonds : 4,5:1 pour du texte, 3:1 pour des marques
  graphiques (barres, courbes) ;
- la distinction des couleurs deux à deux en vision normale et pour les trois formes de
  daltonisme (simulation de Machado et al., 2009, sévérité maximale), mesurée par l'écart
  ΔE (CIE76) dans l'espace Lab.

Exemple :
    uv run python powerbi/theme/check_palette.py
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from pathlib import Path

THEME_PATH = Path(__file__).with_name("dvf-bretagne.json")

TEXT_CONTRAST_MIN = 4.5
GRAPHIC_CONTRAST_MIN = 3.0
DELTA_E_MIN = 20.0

# Couleurs sémantiques utilisées par les mesures DAX de mise en forme conditionnelle.
SEMANTIC_TEXT_COLORS = {
    "hausse": "#B5401A",
    "baisse": "#1565A8",
    "valeur masquée (texte)": "#616E7C",
}
# Séries affichées ensemble : maisons / appartements, et les 4 départements.
CATEGORICAL_SERIES = 4

# Matrices de simulation du daltonisme (Machado, Oliveira et Fernandes, 2009), en RVB linéaire.
CVD_MATRICES = {
    "protanopie": [
        [0.152286, 1.052583, -0.204868],
        [0.114503, 0.786281, 0.099216],
        [-0.003882, -0.048116, 1.051998],
    ],
    "deutéranopie": [
        [0.367322, 0.860646, -0.227968],
        [0.280085, 0.672501, 0.047413],
        [-0.011820, 0.042940, 0.968881],
    ],
    "tritanopie": [
        [1.255528, -0.076749, -0.178779],
        [-0.078411, 0.930809, 0.147602],
        [0.004733, 0.691367, 0.303900],
    ],
}


def to_linear_rgb(hex_color: str) -> list[float]:
    """Couleur hexadécimale vers RVB linéaire (composantes entre 0 et 1)."""
    value = hex_color.lstrip("#")
    channels = [int(value[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]


def luminance(linear_rgb: list[float]) -> float:
    r, g, b = linear_rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(color_a: str, color_b: str) -> float:
    """Rapport de contraste WCAG 2.1 entre deux couleurs."""
    high, low = sorted(
        (luminance(to_linear_rgb(color_a)), luminance(to_linear_rgb(color_b))), reverse=True
    )
    return (high + 0.05) / (low + 0.05)


def to_lab(linear_rgb: list[float]) -> tuple[float, float, float]:
    """RVB linéaire (sRGB, D65) vers CIE Lab."""
    r, g, b = linear_rgb
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def simulate(hex_color: str, vision: str) -> list[float]:
    """Couleur perçue (RVB linéaire) pour un type de vision."""
    rgb = to_linear_rgb(hex_color)
    if vision == "normale":
        return rgb
    matrix = CVD_MATRICES[vision]
    return [min(1.0, max(0.0, sum(matrix[i][j] * rgb[j] for j in range(3)))) for i in range(3)]


def delta_e(color_a: str, color_b: str, vision: str) -> float:
    return math.dist(to_lab(simulate(color_a, vision)), to_lab(simulate(color_b, vision)))


def main() -> int:
    theme = json.loads(THEME_PATH.read_text(encoding="utf-8"))
    backgrounds = {
        "fond des visuels": theme["background"],
        "fond de page": theme["backgroundLight"],
    }
    failures = 0

    print(f"Texte : contraste minimal {TEXT_CONTRAST_MIN}:1")
    text_colors = {
        "texte principal": theme["foreground"],
        "texte secondaire": theme["foregroundNeutralSecondary"],
        **SEMANTIC_TEXT_COLORS,
    }
    for name, color in text_colors.items():
        ratio = min(contrast_ratio(color, bg) for bg in backgrounds.values())
        ok = ratio >= TEXT_CONTRAST_MIN
        failures += not ok
        print(f"  {'OK' if ok else 'KO'}  {name:24} {color}  {ratio:5.2f}:1")

    print(f"\nMarques graphiques : contraste minimal {GRAPHIC_CONTRAST_MIN}:1 sur fond blanc")
    for color in theme["dataColors"]:
        ratio = contrast_ratio(color, theme["background"])
        ok = ratio >= GRAPHIC_CONTRAST_MIN
        failures += not ok
        print(f"  {'OK' if ok else 'KO'}  {color}  {ratio:5.2f}:1")

    print(f"\nDistinction des couleurs : ΔE minimal {DELTA_E_MIN}, toutes visions confondues")
    visions = ["normale", *CVD_MATRICES]
    groups = {
        "hausse / baisse": [SEMANTIC_TEXT_COLORS["hausse"], SEMANTIC_TEXT_COLORS["baisse"]],
        f"{CATEGORICAL_SERIES} premières séries": theme["dataColors"][:CATEGORICAL_SERIES],
    }
    for name, colors in groups.items():
        worst = min(
            (delta_e(a, b, vision), a, b, vision)
            for a, b in itertools.combinations(colors, 2)
            for vision in visions
        )
        ok = worst[0] >= DELTA_E_MIN
        failures += not ok
        print(
            f"  {'OK' if ok else 'KO'}  {name:24} pire cas ΔE {worst[0]:5.1f} "
            f"({worst[1]} / {worst[2]}, {worst[3]})"
        )

    print(f"\n{failures} contrôle(s) en échec")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
