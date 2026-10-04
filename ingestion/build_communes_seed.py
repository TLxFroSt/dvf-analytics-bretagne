"""Construction des seeds dbt des communes bretonnes à partir de l'API Découpage administratif.

Source : https://geo.api.gouv.fr (données INSEE du Code officiel géographique et populations
légales, Licence Ouverte). Deux seeds sont produits :

- `communes_bretagne.csv` : une ligne par commune actuelle (code INSEE, nom, département,
  EPCI de rattachement, population municipale) ;
- `communes_passage.csv` : table de passage des anciennes communes (déléguées ou associées,
  issues de fusions) vers leur commune actuelle. DVF conserve le code commune en vigueur
  au moment du géocodage : une vente dans une commune fusionnée depuis porte l'ancien code.

Les CSV produits sont versionnés : dbt ne dépend pas de l'API, et le script n'est relancé
que pour actualiser le référentiel.

Exemple :
    uv run python ingestion/build_communes_seed.py --deps 22,29,35,56
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from pathlib import Path

import requests

from download import DEFAULT_DEPS, PROJECT_ROOT, REQUEST_TIMEOUT, parse_deps

API_BASE_URL = "https://geo.api.gouv.fr"
COMMUNES_FIELDS = "code,nom,codeDepartement,codeEpci,epci,population"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "dbt" / "seeds"
COMMUNES_FILE = "communes_bretagne.csv"
PASSAGE_FILE = "communes_passage.csv"

COMMUNES_COLUMNS = [
    "code_commune_insee",
    "nom_commune",
    "code_departement",
    "code_epci",
    "nom_epci",
    "population",
]
PASSAGE_COLUMNS = [
    "code_commune_ancienne",
    "nom_commune_ancienne",
    "type_commune_ancienne",
    "code_commune_insee",
]

Row = dict[str, str | int | None]

logger = logging.getLogger("build_communes_seed")


def fetch_json(session: requests.Session, endpoint: str, params: dict[str, str]) -> list[dict]:
    response = session.get(
        f"{API_BASE_URL}/{endpoint}",
        params={**params, "format": "json"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def fetch_communes(session: requests.Session, dep: str) -> list[Row]:
    """Renvoie les communes actuelles d'un département, au format du seed."""
    communes = fetch_json(session, "communes", {"codeDepartement": dep, "fields": COMMUNES_FIELDS})
    return [
        {
            "code_commune_insee": commune["code"],
            "nom_commune": commune["nom"],
            "code_departement": commune["codeDepartement"],
            # Quelques communes insulaires n'appartiennent à aucun EPCI (communes isolées).
            "code_epci": commune.get("codeEpci"),
            "nom_epci": (commune.get("epci") or {}).get("nom"),
            "population": commune.get("population"),
        }
        for commune in communes
    ]


def fetch_passage(session: requests.Session, dep: str) -> list[Row]:
    """Renvoie les anciennes communes d'un département et leur commune actuelle (chef-lieu).

    Les communes déléguées qui portent le même code que leur commune nouvelle sont ignorées :
    leur code est déjà celui d'une commune actuelle.
    """
    anciennes = fetch_json(session, "communes_associees_deleguees", {"codeDepartement": dep})
    return [
        {
            "code_commune_ancienne": commune["code"],
            "nom_commune_ancienne": commune["nom"],
            "type_commune_ancienne": commune["type"],
            "code_commune_insee": commune["chefLieu"],
        }
        for commune in anciennes
        if commune["code"] != commune["chefLieu"]
    ]


def write_seed(path: Path, columns: list[str], rows: list[Row]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: str(row[columns[0]])))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Construit les seeds dbt des communes.")
    parser.add_argument(
        "--deps",
        type=parse_deps,
        default=parse_deps(DEFAULT_DEPS),
        help=f"Codes département séparés par des virgules (défaut : {DEFAULT_DEPS})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Dossier des seeds produits (défaut : dbt/seeds/)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    args = parse_args(argv)

    communes: list[Row] = []
    passage: list[Row] = []
    with requests.Session() as session:
        for dep in args.deps:
            dep_communes = fetch_communes(session, dep)
            if not dep_communes:
                logger.error("Aucune commune renvoyée pour le département %s", dep)
                return 1
            dep_passage = fetch_passage(session, dep)
            logger.info(
                "%s : %d communes, %d anciennes communes", dep, len(dep_communes), len(dep_passage)
            )
            communes.extend(dep_communes)
            passage.extend(dep_passage)

    write_seed(args.output / COMMUNES_FILE, COMMUNES_COLUMNS, communes)
    write_seed(args.output / PASSAGE_FILE, PASSAGE_COLUMNS, passage)
    logger.info(
        "Seeds écrits dans %s : %d communes, %d anciennes communes",
        args.output,
        len(communes),
        len(passage),
    )

    without_epci = [row["nom_commune"] for row in communes if not row["code_epci"]]
    if without_epci:
        logger.info("Communes sans EPCI : %s", ", ".join(str(name) for name in without_epci))
    return 0


if __name__ == "__main__":
    sys.exit(main())
