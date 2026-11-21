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


@dataclass(frozen=True)
class Charter:
    subjects: dict[str, Subject]
    claims: tuple[Claim, ...]

    def digest(self, claim: Claim) -> str:
        """Empreinte de ce qui est revendiqué. Si elle change, les preuves antérieures ne valent plus."""

        def probe(p: Probe | None) -> dict[str, Any] | None:
            return None if p is None else {"command": p.command, "exit_code": p.exit_code, "regex": p.output_regex}

        body = {
            "id": claim.id,
            "capability": claim.capability,
            "kind": claim.kind,
            "subject": claim.subject,
            "commit": self.subjects[claim.subject].commit if claim.subject != "." else "",
            "check": probe(claim.check),
            "falsification": probe(claim.falsification),
            "scope": claim.scope,
            "runs": claim.runs,
        }
        text = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(text.encode()).hexdigest()


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
            re.compile(regex)
        except re.error as exc:
            raise ValueError(f"{where} : expression régulière invalide ({exc})") from exc
    return Probe(
        command=_text(table, "command", where, required=True),
        exit_code=_integer(table, "exit_code", 0, where),
        output_regex=regex,
        description=_text(table, "description", where),
    )


def _claim(table: dict[str, Any], subjects: dict[str, Subject], where: str) -> Claim:
    _only(table, _CLAIM_KEYS, where)
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
    if check is None and {"exit_code", "output_regex", "falsification"} & set(table):
        raise ValueError(f"{where} : résultat attendu ou falsification déclarés sans commande")
    falsification = None
    if "falsification" in table:
        _only(table["falsification"], _PROBE_KEYS, f"{where} (falsification)")
        falsification = _probe(table["falsification"], f"{where} (falsification)")
        if not falsification.description:
            raise ValueError(f"{where} : une falsification doit décrire l'attaque tentée")
    impact = None
    if "impact" in table:
        _only(table["impact"], set(_IMPACT_KEYS), f"{where} (impact)")
        impact = Impact(*(_text(table["impact"], key, f"{where} (impact)", required=True) for key in _IMPACT_KEYS))
    tags = table.get("tags", [])
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        raise ValueError(f"{where} : « tags » doit être une liste de textes")
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
        tags=tuple(tags),
    )


def load_charter(path: Path) -> Charter:
    """Lit et valide le référentiel. Toute clé inconnue est une erreur : dans le doute, bloquer."""

    data = tomllib.loads(path.read_text(encoding="utf-8"))
    _only(data, {"subjects", "claim"}, path.name)
    subjects: dict[str, Subject] = {}
    for name, table in data.get("subjects", {}).items():
        where = f"sujet {name}"
        _only(table, {"repo", "commit", "path"}, where)
        if not _ID_RE.match(name):
            raise ValueError(f"{where} : nom invalide (minuscules, chiffres, tirets)")
        commit = _text(table, "commit", where, required=True)
        if not _SHA_RE.match(commit):
            raise ValueError(f"{where} : commit épinglé invalide (SHA complet de 40 caractères attendu)")
        subjects[name] = Subject(
            name, _text(table, "repo", where, required=True), commit, _text(table, "path", where, required=True)
        )
    claims: list[Claim] = []
    seen: set[str] = set()
    for index, table in enumerate(data.get("claim", []), start=1):
        claim = _claim(table, subjects, f"capacité n°{index}")
        if claim.id in seen:
            raise ValueError(f"capacité {claim.id} : identifiant en double")
        seen.add(claim.id)
        claims.append(claim)
    return Charter(subjects, tuple(claims))
