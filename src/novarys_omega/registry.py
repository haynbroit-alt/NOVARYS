"""Registre des preuves : un fichier JSONL en ajout seul, chaque ligne chaînée à la précédente par SHA-256.

Le fichier vit dans Git : il se relit dans une PR, survit aux sessions et se vérifie par n'importe qui.
Limites. La chaîne détecte une modification, une suppression ou une permutation au milieu ; elle ne voit ni la
troncature de la fin, ni une réécriture complète dont toutes les empreintes auraient été recalculées (il n'y a
pas de clé secrète). Ces deux cas sont couverts par la comparaison au registre de la branche de base
(``omega check --base``), c'est-à-dire par l'historique Git. Et la chaîne protège le passé, pas l'écriture :
une preuve inventée puis ajoutée proprement n'est démasquée que si quelqu'un la rejoue (``omega verify``).
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def seal(record: dict[str, Any]) -> str:
    """Empreinte d'un enregistrement (hors champ ``hash``)."""

    return hashlib.sha256(canonical({k: v for k, v in record.items() if k != "hash"}).encode()).hexdigest()


def _refuse_floats(value: Any) -> None:
    """Un flottant n'a pas d'écriture canonique stable : durées en millisecondes entières, argent en centimes."""

    if isinstance(value, float):
        raise TypeError("nombre à virgule refusé dans le registre (utiliser des entiers)")
    if isinstance(value, dict):
        for item in value.values():
            _refuse_floats(item)
    elif isinstance(value, list | tuple):
        for item in value:
            _refuse_floats(item)


def read(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            record = json.loads(line)
        except ValueError as exc:
            raise ValueError(f"{path.name}, ligne {number} : JSON invalide") from exc
        if not isinstance(record, dict):
            raise ValueError(f"{path.name}, ligne {number} : un objet est attendu")
        records.append(record)
    return records


def chain_errors(records: list[dict[str, Any]]) -> list[str]:
    """Liste les ruptures : numérotation, chaînage avec la ligne précédente, contenu modifié."""

    errors: list[str] = []
    previous = ""
    for position, record in enumerate(records, start=1):
        if record.get("seq") != position:
            errors.append(f"ligne {position} : numéro {record.get('seq')!r} au lieu de {position}")
        if record.get("prev") != previous:
            errors.append(f"ligne {position} : chaînage rompu avec la ligne précédente")
        if record.get("hash") != seal(record):
            errors.append(f"ligne {position} : contenu modifié après écriture (empreinte invalide)")
        previous = str(record.get("hash", ""))
    return errors


def append(path: Path, body: dict[str, Any]) -> dict[str, Any]:
    """Ajoute un enregistrement scellé. Refuse d'écrire à la suite d'un registre corrompu."""

    _refuse_floats(body)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)  # un seul écrivain à la fois
        records = read(path)
        errors = chain_errors(records)
        if errors:
            raise ValueError(f"registre corrompu, ajout refusé — {errors[0]}")
        record = {**body, "seq": len(records) + 1, "prev": records[-1]["hash"] if records else ""}
        record["hash"] = seal(record)
        handle.write(canonical(record) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return record


def extends(base: list[dict[str, Any]], current: list[dict[str, Any]]) -> bool:
    """Vrai si ``current`` reprend ``base`` à l'identique puis, éventuellement, la prolonge."""

    return len(current) >= len(base) and current[: len(base)] == base
