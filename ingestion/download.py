"""Téléchargement des fichiers DVF géolocalisés (data.gouv.fr) par année et département.

Source : https://files.data.gouv.fr/geo-dvf/latest/csv/{année}/departements/{dep}.csv.gz
Licence Ouverte (Etalab). Seules les 5 dernières années sont publiées : une année absente
renvoie une 404, signalée sans interrompre les autres téléchargements.

Les fichiers sont conservés compressés (.csv.gz) : DuckDB les lit directement.

Exemple :
    uv run python ingestion/download.py --years 2021-2025 --deps 22,29,35,56
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from enum import Enum
from pathlib import Path

import requests

BASE_URL = "https://files.data.gouv.fr/geo-dvf/latest/csv"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"
DEFAULT_YEARS = "2021-2025"
DEFAULT_DEPS = "22,29,35,56"

# (connexion, lecture) en secondes
REQUEST_TIMEOUT = (10, 60)
CHUNK_SIZE = 1024 * 1024

# Codes département : métropole (01-95, 2A, 2B) et outre-mer (971-976)
DEP_CODE_PATTERN = re.compile(r"^(\d{2}|2[AB]|97\d)$")

logger = logging.getLogger("download")


class Status(Enum):
    DOWNLOADED = "téléchargé"
    SKIPPED = "déjà présent"
    NOT_FOUND = "absent de la source"
    FAILED = "échec"


def parse_years(value: str) -> list[int]:
    """Convertit '2021-2025', '2022,2024' ou '2023' en liste d'années triée."""
    years: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if "-" in part:
            start, end = (int(bound) for bound in part.split("-", maxsplit=1))
            if start > end:
                raise argparse.ArgumentTypeError(f"Intervalle d'années invalide : {part}")
            years.update(range(start, end + 1))
        elif part:
            years.add(int(part))
    if not years:
        raise argparse.ArgumentTypeError("Aucune année fournie")
    return sorted(years)


def parse_deps(value: str) -> list[str]:
    """Convertit '22,29,35,56' en liste de codes département validés."""
    deps = [dep.strip().upper() for dep in value.split(",") if dep.strip()]
    invalid = [dep for dep in deps if not DEP_CODE_PATTERN.match(dep)]
    if invalid:
        raise argparse.ArgumentTypeError(f"Code(s) département invalide(s) : {', '.join(invalid)}")
    if not deps:
        raise argparse.ArgumentTypeError("Aucun département fourni")
    return deps


def build_url(year: int, dep: str) -> str:
    return f"{BASE_URL}/{year}/departements/{dep}.csv.gz"


def download_file(session: requests.Session, url: str, dest: Path, force: bool) -> Status:
    """Télécharge `url` vers `dest`.

    Le contenu est d'abord écrit dans un fichier `.part`, renommé une fois complet :
    une interruption ne laisse jamais un fichier tronqué sous le nom final.
    """
    if dest.exists() and not force:
        return Status.SKIPPED

    tmp_path = dest.with_name(dest.name + ".part")
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with session.get(url, stream=True, timeout=REQUEST_TIMEOUT) as response:
            if response.status_code == 404:
                return Status.NOT_FOUND
            response.raise_for_status()
            with tmp_path.open("wb") as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    file.write(chunk)
        tmp_path.replace(dest)
    except requests.RequestException as error:
        logger.error("%s : %s", url, error)
        tmp_path.unlink(missing_ok=True)
        return Status.FAILED
    return Status.DOWNLOADED


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Télécharge les fichiers DVF géolocalisés par année et département."
    )
    parser.add_argument(
        "--years",
        type=parse_years,
        default=parse_years(DEFAULT_YEARS),
        help=f"Années : intervalle ou liste, ex. 2021-2025 ou 2022,2024 (défaut : {DEFAULT_YEARS})",
    )
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
        help="Dossier de destination (défaut : data/raw/)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Retélécharge les fichiers déjà présents",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    args = parse_args(argv)

    results: dict[Status, list[Path]] = {status: [] for status in Status}
    with requests.Session() as session:
        for year in args.years:
            for dep in args.deps:
                dest = args.output / str(year) / f"{dep}.csv.gz"
                status = download_file(session, build_url(year, dep), dest, args.force)
                results[status].append(dest)
                logger.info("%s/%s : %s", year, dep, status.value)

    total_mb = sum(path.stat().st_size for path in results[Status.DOWNLOADED]) / 1024**2
    logger.info(
        "Terminé : %d téléchargé(s) (%.1f Mo), %d déjà présent(s), %d absent(s), %d échec(s)",
        len(results[Status.DOWNLOADED]),
        total_mb,
        len(results[Status.SKIPPED]),
        len(results[Status.NOT_FOUND]),
        len(results[Status.FAILED]),
    )

    # Code de sortie non nul si un fichier demandé manque : utile en CI.
    return 1 if results[Status.NOT_FOUND] or results[Status.FAILED] else 0


if __name__ == "__main__":
    sys.exit(main())
