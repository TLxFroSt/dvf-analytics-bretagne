"""Construction des contours simplifiés des communes bretonnes, pour la carte Power BI.

Source : https://geo.api.gouv.fr/communes (contours IGN Admin Express, Licence Ouverte),
au même millésime que le seed `communes_bretagne`. Les contours bruts pèsent environ 20 Mo :
ils sont simplifiés avec mapshaper, qui préserve la topologie (les communes voisines gardent
une frontière commune, sans trou ni chevauchement), puis écrits en TopoJSON, le seul format
accepté par le visuel Carte de formes de Power BI.

Prérequis : Node.js (mapshaper est exécuté via npx, version épinglée ci-dessous).

Exemple :
    uv run python ingestion/build_communes_topojson.py
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import requests

from download import DEFAULT_DEPS, PROJECT_ROOT, REQUEST_TIMEOUT, parse_deps

API_URL = "https://geo.api.gouv.fr/communes"
MAPSHAPER = "mapshaper@0.7.72"
DEFAULT_OUTPUT = PROJECT_ROOT / "powerbi" / "maps" / "communes-bretagne.topojson"
# Part des points conservés : compromis entre le poids du fichier et la finesse du trait
# à l'échelle d'une région.
DEFAULT_SIMPLIFY = "4%"

logger = logging.getLogger("build_communes_topojson")


def fetch_contours(session: requests.Session, dep: str) -> dict:
    """Contours GeoJSON des communes d'un département, avec les propriétés de dim_commune.

    `libelle_commune` (« Vannes (56) ») est la clé de la carte dans Power BI : c'est aussi le
    champ de drill-through vers la fiche commune.
    """
    response = session.get(
        API_URL,
        params={
            "codeDepartement": dep,
            "format": "geojson",
            "geometry": "contour",
            "fields": "code,nom,codeDepartement",
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    contours = response.json()
    for feature in contours["features"]:
        props = feature["properties"]
        feature["properties"] = {
            "code_commune_insee": props["code"],
            "nom_commune": props["nom"],
            "libelle_commune": f"{props['nom']} ({props['codeDepartement']})",
        }
    return contours


def run_mapshaper(inputs: list[Path], output: Path, simplify: str) -> None:
    """Fusionne, simplifie et convertit les contours en TopoJSON."""
    npx = shutil.which("npx")
    if npx is None:
        raise RuntimeError("npx introuvable : installer Node.js pour exécuter mapshaper.")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        npx, "--yes", MAPSHAPER,
        "-i", *[str(path) for path in inputs], "combine-files",
        "-merge-layers",
        "-rename-layers", "communes",
        "-simplify", simplify, "keep-shapes",
        "-o", str(output), "format=topojson", "quantization=100000",
    ]  # fmt: skip
    subprocess.run(command, check=True)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Construit le TopoJSON des communes.")
    parser.add_argument(
        "--deps",
        type=parse_deps,
        default=parse_deps(DEFAULT_DEPS),
        help=f"Codes département séparés par des virgules (défaut : {DEFAULT_DEPS})",
    )
    parser.add_argument(
        "--simplify",
        default=DEFAULT_SIMPLIFY,
        help=f"Part des points conservés par mapshaper (défaut : {DEFAULT_SIMPLIFY})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Fichier TopoJSON produit (défaut : powerbi/maps/communes-bretagne.topojson)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    args = parse_args(argv)

    with tempfile.TemporaryDirectory() as tmp_dir, requests.Session() as session:
        inputs = []
        for dep in args.deps:
            contours = fetch_contours(session, dep)
            path = Path(tmp_dir) / f"communes-{dep}.geojson"
            path.write_text(json.dumps(contours), encoding="utf-8")
            logger.info("%s : %d contours de communes", dep, len(contours["features"]))
            inputs.append(path)
        run_mapshaper(inputs, args.output, args.simplify)

    size_kb = args.output.stat().st_size / 1024
    logger.info("TopoJSON écrit : %s (%.0f Ko)", args.output, size_kb)
    return 0


if __name__ == "__main__":
    sys.exit(main())
