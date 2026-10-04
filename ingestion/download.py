"""Téléchargement des fichiers DVF géolocalisés (data.gouv.fr) par année et département.

Source : https://files.data.gouv.fr/geo-dvf/latest/csv/{année}/departements/{dep}.csv.gz
Licence Ouverte (Etalab). Seules les 5 dernières années sont publiées : une année absente
renvoie une 404, signalée sans interrompre les autres téléchargements.

Les fichiers sont conservés compressés (.csv.gz) : DuckDB les lit directement.

Manifeste : `data/raw/manifest.csv` garde, pour chaque fichier, sa date de publication
(en-tête HTTP Last-Modified). Les URL « latest » changent de contenu à chaque publication
semestrielle de la DGFiP : un fichier déjà présent est retéléchargé si le serveur annonce
une date de publication différente de celle du manifeste. Le manifeste est aussi lu par dbt
pour afficher la date des données dans le dashboard.

Exemple :
    uv run python ingestion/download.py --years 2021-2025 --deps 22,29,35,56
"""

from __future__ import annotations

import argparse
import csv
import logging
import re
import sys
from dataclasses import asdict, dataclass, fields
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from enum import Enum
from pathlib import Path

import requests

BASE_URL = "https://files.data.gouv.fr/geo-dvf/latest/csv"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"
DEFAULT_YEARS = "2021-2025"
DEFAULT_DEPS = "22,29,35,56"
MANIFEST_NAME = "manifest.csv"

# (connexion, lecture) en secondes
REQUEST_TIMEOUT = (10, 60)
CHUNK_SIZE = 1024 * 1024

# Codes département : métropole (01-95, 2A, 2B) et outre-mer (971-976)
DEP_CODE_PATTERN = re.compile(r"^(\d{2}|2[AB]|97\d)$")

logger = logging.getLogger("download")


class Status(Enum):
    DOWNLOADED = "téléchargé"
    UPDATED = "mis à jour"
    SKIPPED = "déjà à jour"
    NOT_FOUND = "absent de la source"
    FAILED = "échec"


@dataclass
class ManifestEntry:
    """Une ligne du manifeste : un fichier téléchargé et sa date de publication."""

    annee: int
    code_departement: str
    url: str
    date_publication: str  # Last-Modified du serveur, ISO 8601 UTC
    taille_octets: int
    date_telechargement: str  # ISO 8601 UTC


Manifest = dict[tuple[int, str], ManifestEntry]


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


def to_iso_utc(http_date: str | None) -> str | None:
    """Convertit une date HTTP ('Mon, 18 May 2026 13:14:12 GMT') en ISO 8601 UTC."""
    if not http_date:
        return None
    return parsedate_to_datetime(http_date).astimezone(UTC).isoformat()


def load_manifest(path: Path) -> Manifest:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as file:
        rows = csv.DictReader(file)
        entries = [
            ManifestEntry(
                annee=int(row["annee"]),
                code_departement=row["code_departement"],
                url=row["url"],
                date_publication=row["date_publication"],
                taille_octets=int(row["taille_octets"]),
                date_telechargement=row["date_telechargement"],
            )
            for row in rows
        ]
    return {(entry.annee, entry.code_departement): entry for entry in entries}


def save_manifest(path: Path, manifest: Manifest) -> None:
    """Écrit le manifeste trié, via un fichier temporaire renommé (écriture atomique)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(path.name + ".part")
    with tmp_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=[field.name for field in fields(ManifestEntry)])
        writer.writeheader()
        for key in sorted(manifest):
            writer.writerow(asdict(manifest[key]))
    tmp_path.replace(path)


def fetch_publication_date(session: requests.Session, url: str) -> str | None:
    """Date de publication annoncée par le serveur (requête HEAD), ou None si indisponible."""
    try:
        response = session.head(url, allow_redirects=True, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as error:
        logger.warning("Vérification impossible pour %s : %s", url, error)
        return None
    return to_iso_utc(response.headers.get("Last-Modified"))


def download_file(session: requests.Session, url: str, dest: Path) -> str | None:
    """Télécharge `url` vers `dest` et renvoie sa date de publication.

    Le contenu est d'abord écrit dans un fichier `.part`, renommé une fois complet :
    une interruption ne laisse jamais un fichier tronqué sous le nom final.
    Lève FileNotFoundError si la source renvoie une 404.
    """
    tmp_path = dest.with_name(dest.name + ".part")
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with session.get(url, stream=True, timeout=REQUEST_TIMEOUT) as response:
            if response.status_code == 404:
                raise FileNotFoundError(url)
            response.raise_for_status()
            with tmp_path.open("wb") as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    file.write(chunk)
            publication_date = to_iso_utc(response.headers.get("Last-Modified"))
        tmp_path.replace(dest)
    finally:
        tmp_path.unlink(missing_ok=True)
    return publication_date


def sync_file(
    session: requests.Session,
    year: int,
    dep: str,
    output_dir: Path,
    manifest: Manifest,
    force: bool,
) -> Status:
    """Met le fichier (année, département) à jour et tient le manifeste à jour."""
    url = build_url(year, dep)
    dest = output_dir / str(year) / f"{dep}.csv.gz"
    known = manifest.get((year, dep))
    already_present = dest.exists()

    if already_present and not force:
        remote_date = fetch_publication_date(session, url)
        if remote_date is None:
            # Serveur injoignable ou fichier retiré de la source : on garde la copie locale.
            return Status.SKIPPED
        if known is not None and known.date_publication == remote_date:
            return Status.SKIPPED

    try:
        publication_date = download_file(session, url, dest)
    except FileNotFoundError:
        return Status.NOT_FOUND
    except requests.RequestException as error:
        logger.error("%s : %s", url, error)
        return Status.FAILED

    manifest[(year, dep)] = ManifestEntry(
        annee=year,
        code_departement=dep,
        url=url,
        date_publication=publication_date or "",
        taille_octets=dest.stat().st_size,
        date_telechargement=datetime.now(UTC).isoformat(timespec="seconds"),
    )
    return Status.UPDATED if already_present else Status.DOWNLOADED


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
        help="Retélécharge les fichiers même s'ils sont à jour",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    args = parse_args(argv)

    manifest_path = args.output / MANIFEST_NAME
    manifest = load_manifest(manifest_path)
    counts = {status: 0 for status in Status}

    with requests.Session() as session:
        for year in args.years:
            for dep in args.deps:
                status = sync_file(session, year, dep, args.output, manifest, args.force)
                counts[status] += 1
                logger.info("%s/%s : %s", year, dep, status.value)

    save_manifest(manifest_path, manifest)
    logger.info(
        "Terminé : %d téléchargé(s), %d mis à jour, %d déjà à jour, %d absent(s), %d échec(s)",
        counts[Status.DOWNLOADED],
        counts[Status.UPDATED],
        counts[Status.SKIPPED],
        counts[Status.NOT_FOUND],
        counts[Status.FAILED],
    )

    # Code de sortie non nul si un fichier demandé manque : utile en CI.
    return 1 if counts[Status.NOT_FOUND] or counts[Status.FAILED] else 0


if __name__ == "__main__":
    sys.exit(main())
