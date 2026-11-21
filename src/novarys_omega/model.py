"""Contrats du protocole Ω : capacité revendiquée, sonde, statuts et niveaux.

Le référentiel (``registre/capacites.toml``) déclare ce que NOVARYS prétend savoir faire et la commande qui le
démontre. Une fonction exigée par le cahier des charges mais non construite y figure sans commande : elle
apparaît ABSENTE dans la matrice au lieu d'être passée sous silence.
"""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

DOMAINS = (
    "CORE",
    "INTELLIGENCE",
    "DISCOVERY",
    "INTERNET",
    "ENGINEERING",
    "BUSINESS",
    "AGENTS",
    "MEMORY",
    "OMEGA",
    "SOVEREIGN",
)
KINDS = ("test", "reel")  # preuve sur données de test, ou sur données et environnement réels
PROBES = "registre/sondes"  # scripts appelés par les commandes : leur contenu fait partie de ce qui est revendiqué
_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_CLAIM_KEYS = {
    "id",
    "domain",
    "capability",
    "kind",
    "subject",
    "command",
    "exit_code",
    "output_regex",
    "scope",
    "limits",
    "runs",
    "timeout_s",
    "tags",
    "covers",
    "falsification",
    "impact",
}
_PROBE_KEYS = {"description", "command", "exit_code", "output_regex"}
_IMPACT_KEYS = ("beneficiaries", "indicator", "method", "counterfactual")


class Status(StrEnum):
    PROVEN = "PROUVE"
    SUPPORTED = "ETAYE"
    UNKNOWN = "INCONNU"
    CONFLICT = "CONFLIT"
    FAILED = "ECHEC"


class Level(StrEnum):
    ABSENT = "ABSENT"
    AVAILABLE = "DISPONIBLE"
    CONNECTED = "CONNECTE"
    TESTED = "TESTE"
    OPERATIONAL = "OPERATIONNEL"
    VALIDATED = "VALIDE"


LEVELS = tuple(Level)  # ordre croissant
_LABELS = {
    "PROUVE": "PROUVÉ",
    "ETAYE": "ÉTAYÉ",
    "ECHEC": "ÉCHEC",
    "CONNECTE": "CONNECTÉ",
    "TESTE": "TESTÉ",
    "OPERATIONNEL": "OPÉRATIONNEL",
    "VALIDE": "VALIDÉ",
}


def label(value: str) -> str:
    """Forme affichée d'un statut ou d'un niveau (les valeurs stockées restent sans accent)."""

    return _LABELS.get(value, value)


@dataclass(frozen=True)
class Probe:
    """Une commande et le résultat qu'on en attend (code de sortie, ligne de bilan)."""

    command: str
    exit_code: int = 0
    output_regex: str | None = None
    description: str = ""


@dataclass(frozen=True)
class Impact:
    beneficiaries: str
    indicator: str
    method: str
    counterfactual: str


@dataclass(frozen=True)
class Subject:
    """Dépôt sur lequel porte une preuve, épinglé à un commit : la preuve vaut pour ce code-là."""

    name: str
    repo: str
    commit: str
    path: str


@dataclass(frozen=True)
class Claim:
    id: str
    domain: str
    capability: str
    kind: str = "test"
    subject: str = "."
    check: Probe | None = None
    falsification: Probe | None = None
    scope: str = ""
    limits: str = ""
    impact: Impact | None = None
    runs: int = 2
    timeout_s: int = 900
    tags: tuple[str, ...] = ()
    covers: tuple[str, ...] = ()


@dataclass(frozen=True)
class Charter:
    subjects: dict[str, Subject]
    claims: tuple[Claim, ...]
    files: dict[str, str]  # chemin relatif à la racine → sha256 du contenu (sondes et chemins « covers »)

    def digest(self, claim: Claim) -> str:
        """Empreinte de ce qui est revendiqué et de ce qui le vérifie. Si elle change, les preuves ne valent plus.

        Elle couvre la commande, l'attaque, le périmètre, le classement (domaine, étiquettes), le commit épinglé,
        et le contenu des fichiers de ce dépôt dont dépend la preuve : les sondes citées par les commandes et les
        chemins « covers ». Seuls le commentaire (limites, impact) et la forme restent hors de l'empreinte.
        """

        def probe(p: Probe | None) -> dict[str, Any] | None:
            if p is None:
                return None
            return {"command": p.command, "exit_code": p.exit_code, "regex": p.output_regex, "why": p.description}

        commands = " ".join(p.command for p in (claim.check, claim.falsification) if p is not None)
        body = {
            "id": claim.id,
            "domain": claim.domain,
            "capability": claim.capability,
            "kind": claim.kind,
            "subject": claim.subject,
            "commit": self.subjects[claim.subject].commit if claim.subject != "." else "",
            "check": probe(claim.check),
            "falsification": probe(claim.falsification),
            "scope": claim.scope,
            "runs": claim.runs,
            "timeout_s": claim.timeout_s,
            "tags": sorted(claim.tags),
            "files": {
                path: sha
                for path, sha in sorted(self.files.items())
                if (path.startswith(f"{PROBES}/") and path.removeprefix("registre/") in commands)
                or any(path == cover or path.startswith(f"{cover}/") for cover in claim.covers)
            },
        }
        text = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(text.encode()).hexdigest()


def _table(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{where} : une table est attendue")
    return value


def _only(table: dict[str, Any], allowed: set[str], where: str) -> None:
    unknown = sorted(set(table) - allowed)
    if unknown:
        raise ValueError(f"{where} : clés inconnues {unknown}")


def _text(table: dict[str, Any], key: str, where: str, *, required: bool = False) -> str:
    value = table.get(key, "")
    if not isinstance(value, str):
        raise ValueError(f"{where} : « {key} » doit être un texte")
    if required and not value.strip():
        raise ValueError(f"{where} : « {key} » est obligatoire")
    return value.strip()


def _texts(table: dict[str, Any], key: str, where: str) -> tuple[str, ...]:
    values = table.get(key, [])
    if not isinstance(values, list) or not all(isinstance(value, str) and value for value in values):
        raise ValueError(f"{where} : « {key} » doit être une liste de textes")
    return tuple(values)


def _integer(table: dict[str, Any], key: str, default: int, where: str, *, minimum: int | None = None) -> int:
    value = table.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool) or (minimum is not None and value < minimum):
        raise ValueError(f"{where} : « {key} » doit être un entier" + (f" ≥ {minimum}" if minimum is not None else ""))
    return value


def _probe(table: dict[str, Any], where: str) -> Probe:
    regex = table.get("output_regex")
    if regex is not None:
        if not isinstance(regex, str):
            raise ValueError(f"{where} : « output_regex » doit être un texte")
        try:
            vacuous = re.search(regex, "", re.MULTILINE) is not None
        except re.error as exc:
            raise ValueError(f"{where} : expression régulière invalide ({exc})") from exc
        if vacuous:  # une « ligne de bilan » qu'une sortie vide satisfait ne prouve rien
            raise ValueError(f"{where} : l'expression attendue correspond à une sortie vide")
    return Probe(
        command=_text(table, "command", where, required=True),
        exit_code=_integer(table, "exit_code", 0, where),
        output_regex=regex,
        description=_text(table, "description", where),
    )


def _claim(table: dict[str, Any], subjects: dict[str, Subject], where: str) -> Claim:
    _only(_table(table, where), _CLAIM_KEYS, where)
    claim_id = table.get("id")
    if not isinstance(claim_id, str) or not _ID_RE.match(claim_id):
        raise ValueError(f"{where} : identifiant invalide {claim_id!r} (minuscules, chiffres, tirets)")
    where = f"capacité {claim_id}"
    if table.get("domain") not in DOMAINS:
        raise ValueError(f"{where} : domaine inconnu {table.get('domain')!r} (attendu : {', '.join(DOMAINS)})")
    kind = table.get("kind", "test")
    if kind not in KINDS:
        raise ValueError(f"{where} : nature inconnue {kind!r} (attendu : {', '.join(KINDS)})")
    subject = table.get("subject", ".")
    if subject != "." and subject not in subjects:
        raise ValueError(f"{where} : sujet non déclaré {subject!r}")
    check = _probe(table, where) if "command" in table else None
    if check is None and {"exit_code", "output_regex", "falsification", "covers"} & set(table):
        raise ValueError(f"{where} : résultat attendu, falsification ou fichiers déclarés sans commande")
    falsification = None
    if "falsification" in table:
        _only(_table(table["falsification"], f"{where} (falsification)"), _PROBE_KEYS, f"{where} (falsification)")
        falsification = _probe(table["falsification"], f"{where} (falsification)")
        if not falsification.description:
            raise ValueError(f"{where} : une falsification doit décrire l'attaque tentée")
        if check is not None and falsification.command == check.command:
            raise ValueError(f"{where} : l'attaque ne peut pas être la commande de preuve elle-même")
    impact = None
    if "impact" in table:
        _only(_table(table["impact"], f"{where} (impact)"), set(_IMPACT_KEYS), f"{where} (impact)")
        impact = Impact(*(_text(table["impact"], key, f"{where} (impact)", required=True) for key in _IMPACT_KEYS))
    return Claim(
        id=claim_id,
        domain=table["domain"],
        capability=_text(table, "capability", where, required=True),
        kind=kind,
        subject=subject,
        check=check,
        falsification=falsification,
        scope=_text(table, "scope", where),
        limits=_text(table, "limits", where),
        impact=impact,
        runs=_integer(table, "runs", 2, where, minimum=1),
        timeout_s=_integer(table, "timeout_s", 900, where, minimum=1),
        tags=_texts(table, "tags", where),
        covers=_texts(table, "covers", where),
    )


def _hashes(root: Path, relative: str, where: str) -> dict[str, str]:
    """Empreintes des fichiers d'un chemin du dépôt (un fichier, ou un dossier parcouru en entier)."""

    target = root / relative
    if not target.resolve().is_relative_to(root.resolve()) or not target.exists():
        raise ValueError(f"{where} : chemin introuvable dans ce dépôt ({relative})")
    files = [target] if target.is_file() else sorted(p for p in target.rglob("*") if p.is_file())
    return {
        file.relative_to(root).as_posix(): hashlib.sha256(file.read_bytes()).hexdigest()
        for file in files
        if "__pycache__" not in file.parts
    }


def load_charter(path: Path) -> Charter:
    """Lit et valide le référentiel. Toute clé inconnue est une erreur : dans le doute, bloquer."""

    root = path.resolve().parent.parent
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    _only(data, {"subjects", "claim"}, path.name)
    subjects: dict[str, Subject] = {}
    for name, table in _table(data.get("subjects", {}), "subjects").items():
        where = f"sujet {name}"
        _only(_table(table, where), {"repo", "commit", "path"}, where)
        if not _ID_RE.match(name):
            raise ValueError(f"{where} : nom invalide (minuscules, chiffres, tirets)")
        commit = _text(table, "commit", where, required=True)
        if not _SHA_RE.match(commit):
            raise ValueError(f"{where} : commit épinglé invalide (SHA complet de 40 caractères attendu)")
        subjects[name] = Subject(
            name, _text(table, "repo", where, required=True), commit, _text(table, "path", where, required=True)
        )
    tables = data.get("claim", [])
    if not isinstance(tables, list):
        raise ValueError(f"{path.name} : « claim » doit être une liste de tables ([[claim]])")
    claims: list[Claim] = []
    files = _hashes(root, PROBES, PROBES) if (root / PROBES).is_dir() else {}
    for index, table in enumerate(tables, start=1):
        claim = _claim(table, subjects, f"capacité n°{index}")
        if claim.id in {known.id for known in claims}:
            raise ValueError(f"capacité {claim.id} : identifiant en double")
        for cover in claim.covers:
            files.update(_hashes(root, cover, f"capacité {claim.id}"))
        claims.append(claim)
    return Charter(subjects, tuple(claims), files)
