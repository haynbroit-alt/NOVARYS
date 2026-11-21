"""Exécution d'une capacité revendiquée : commande, attaque, reproduction, statut.

Sécurité. Une commande de preuve est du code : le référentiel se relit comme du code, et on n'exécute jamais
celui d'un dépôt qu'on ne maîtrise pas. Les commandes tournent sans les secrets de la session (variables au nom
ou à la valeur sensible retirées) et dans un processus distinct de celui qui détient la base financière de
SOVEREIGN. Une sortie qui contient un motif de secret, ou la valeur d'une variable retirée, est retenue.

Limites. Ces protections couvrent les fuites accidentelles. Une commande garde les droits du compte qui la
lance : elle peut lire ses fichiers et l'environnement des autres processus. La détection par motifs ne
remplace pas la relecture du registre avant fusion.
"""

from __future__ import annotations

import contextlib
import hashlib
import os
import platform
import re
import shutil
import signal
import subprocess
import tempfile
import time
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from novarys_omega.model import Charter, Claim, Probe, Status

OUTPUT_LIMIT = 16_000  # caractères d'une sortie conservés au registre
READ_LIMIT = 8 * 1024 * 1024  # octets relus d'une sortie : la fin, là où se trouve le bilan
WITHHELD = "[sortie retenue : {name}]"
_SENSITIVE_ENV = re.compile(
    r"(?i)key|token|secret|pass|credential|auth|cookie|private|signature|dsn|webhook|_pat$|database_url|conn"
)
# Motifs de l'observateur de SOVEREIGN (``sovereign/ecosystem.py``), élargis aux formats de jetons courants.
_SECRETS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("clé AWS", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("clé Anthropic", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("clé OpenAI", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_\-]{32,}")),
    ("jeton GitHub", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{20,})")),
    ("jeton GitLab", re.compile(r"\bglpat-[A-Za-z0-9_\-]{20,}")),
    ("jeton npm", re.compile(r"\bnpm_[A-Za-z0-9]{36,}")),
    ("jeton Hugging Face", re.compile(r"\bhf_[A-Za-z0-9]{30,}")),
    ("jeton Slack", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}|hooks\.slack\.com/services/")),
    ("clé Google", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}|\bya29\.[0-9A-Za-z_\-]{20,}")),
    ("clé SendGrid", re.compile(r"\bSG\.[A-Za-z0-9_\-]{16,}\.[A-Za-z0-9_\-]{16,}")),
    ("clé Stripe", re.compile(r"\b(?:[sr]k_(?:live|test)|whsec)_[A-Za-z0-9]{20,}")),
    ("jeton JWT", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}")),
    ("en-tête d'autorisation", re.compile(r"(?i)\bauthorization\s*[:=]\s*\S{8,}|\bbearer\s+[A-Za-z0-9._~+/=\-]{20,}")),
    ("clé privée", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY(?: BLOCK)?-----")),
    ("identifiants dans une URL", re.compile(r"[a-z][a-z0-9+.\-]*://[^\s/@]{3,}@")),
    (
        "secret en clair",
        re.compile(
            r"""(?i)\b(?:api[_-]?key|access[_-]?token|secret|token|password|passwd|accountkey)\b["']?\s*[:=]\s*"""
            r"""["']?[A-Za-z0-9._~+/\-]{16,}"""
        ),
    ),
)
# Chemins qui portent un nom de compte, et adresses électroniques : masqués dans toute sortie conservée.
_USER_PATH = re.compile(r"""(/(?:home|Users)/|pytest-of-)[^/\s"']+""")
_EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
# Fichiers que `omega run` écrit lui-même : ils ne rendent pas « modifié » le dépôt qui porte le registre.
_OWN_OUTPUTS = (
    ":(exclude)registre/preuves.jsonl",
    ":(exclude)CAPACITES.md",
    ":(exclude)ACTIFS.md",
    ":(exclude)site",
)
_STATUS = ("-c", "status.showUntrackedFiles=all", "status", "--porcelain", "--untracked-files=all")
_RECORD_KEYS = ("claim", "claim_sha256", "status", "runs", "expected", "falsification", "scope", "subject", "output")


class SubjectError(RuntimeError):
    """Le dépôt visé n'est pas dans l'état épinglé par le référentiel."""


@dataclass(frozen=True)
class Execution:
    exit_code: int | None
    output: str
    duration_ms: int
    timed_out: bool


def find_secret(text: str) -> str | None:
    return next((name for name, pattern in _SECRETS if pattern.search(text)), None)


def _sensitive(name: str, value: str) -> bool:
    """Variable à ne pas transmettre : nom sensible, ou valeur qui ressemble à un secret.

    Exception : l'adresse du proxy, sans laquelle il n'y a plus de réseau ; si elle porte des identifiants,
    c'est le contrôle des sorties qui les retient.
    """

    return bool(_SENSITIVE_ENV.search(name)) or ("proxy" not in name.lower() and find_secret(value) is not None)


def scrubbed_env(extra: Mapping[str, str]) -> dict[str, str]:
    """Environnement de la session sans ses secrets. ``GIT_CONFIG_*`` part aussi : il porte souvent un jeton."""

    env = {
        name: value
        for name, value in os.environ.items()
        if not _sensitive(name, value) and not name.startswith("GIT_CONFIG_")
    }
    env.pop("VIRTUAL_ENV", None)  # la preuve ne doit pas dépendre de l'environnement Python qui a lancé omega
    env.update(extra)
    return env


def _withheld_values() -> list[str]:
    """Valeurs des variables retirées : si l'une d'elles ressort dans une sortie, la sortie est retenue."""

    return [value for name, value in os.environ.items() if _sensitive(name, value) and len(value) >= 12]


def execute(command: str, cwd: Path, env: Mapping[str, str], timeout_s: int) -> Execution:
    """Lance la commande sous ``bash -o pipefail`` (un échec en amont d'un pipe n'est jamais masqué).

    La sortie va dans un fichier et non dans un tube : un descendant détaché ne peut pas retenir l'outil
    au-delà du délai, et une sortie énorme n'est relue que par sa fin.
    """

    started = time.monotonic()
    with tempfile.TemporaryFile() as sink:
        process = subprocess.Popen(
            ["bash", "-o", "pipefail", "-c", command],
            cwd=cwd,
            env=dict(env),
            stdin=subprocess.DEVNULL,
            stdout=sink,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            process.wait(timeout=timeout_s)
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
        with contextlib.suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGKILL)  # la commande et tout ce qu'elle a laissé derrière elle
        with contextlib.suppress(subprocess.TimeoutExpired):
            process.wait(timeout=10)
        duration_ms = int((time.monotonic() - started) * 1000)
        size = sink.seek(0, os.SEEK_END)
        sink.seek(max(0, size - READ_LIMIT))
        text = sink.read().decode("utf-8", "replace")
    if size > READ_LIMIT:
        text = f"[… {size - READ_LIMIT} premiers octets non relus …]\n{text}"
    return Execution(None if timed_out else process.returncode, text, duration_ms, timed_out)


def sanitize(text: str, replacements: Sequence[tuple[str, str]]) -> str:
    """Remplace les chemins locaux par des repères stables ; masque noms de compte et adresses électroniques."""

    for path, marker in sorted(replacements, key=lambda pair: -len(pair[0])):
        if len(path) > 3:
            text = text.replace(path, marker)
    text = _USER_PATH.sub(lambda match: f"{match.group(1)}<utilisateur>", text)
    return _EMAIL.sub("<adresse>", text)


def cap(text: str, limit: int = OUTPUT_LIMIT) -> tuple[str, bool]:
    """Sortie brute, coupée au milieu au-delà de ``limit`` : le début et la fin (le bilan) sont conservés."""

    if len(text) <= limit:
        return text, False
    head = limit // 4
    return f"{text[:head]}\n[… {len(text) - limit} caractères omis …]\n{text[-(limit - head) :]}", True


def decide(
    checks: Sequence[bool], attack_resisted: bool | None, *, has_summary: bool, has_scope: bool, clean: bool = True
) -> Status:
    """Statut d'une preuve, calculé et jamais déclaré.

    PROUVÉ exige : au moins deux exécutions concordantes, la ligne de bilan attendue, un périmètre écrit, un code
    validé dans Git et une tentative de réfutation exécutée à laquelle la capacité a résisté. Une attaque qui
    passe réfute la capacité.
    """

    if not checks:
        return Status.UNKNOWN
    if not any(checks):
        return Status.FAILED
    if not all(checks):
        return Status.CONFLICT
    if attack_resisted is False:
        return Status.FAILED
    if len(checks) >= 2 and attack_resisted and has_summary and has_scope and clean:
        return Status.PROVEN
    return Status.SUPPORTED


def _git(path: Path, *args: str) -> str | None:
    done = subprocess.run(
        ["git", "-C", str(path), *args], env=scrubbed_env({}), capture_output=True, text=True, check=False
    )
    return done.stdout.strip() if done.returncode == 0 else None


def subject_state(charter: Charter, claim: Claim, root: Path, paths: Mapping[str, Path]) -> tuple[Path, str, bool]:
    """Dossier, commit et état « modifié » du dépôt visé.

    Un dépôt épinglé doit être exactement à son commit, à sa racine, sans rien de modifié, d'ajouté ni de masqué
    à Git ; sinon ``SubjectError``. Ce dépôt-ci peut être modifié : la preuve le note et ne sera qu'ÉTAYÉE.
    Limite : les fichiers ignorés par Git (environnement installé, caches) ne sont pas contrôlés.
    """

    if claim.subject == ".":
        return root, _git(root, "rev-parse", "HEAD") or "", bool(_git(root, *_STATUS, "--", ".", *_OWN_OUTPUTS))
    cwd = paths[claim.subject]
    pinned = charter.subjects[claim.subject].commit
    commit = _git(cwd, "rev-parse", "HEAD")
    problems: list[str] = []
    if commit is None:
        problems.append("aucun dépôt Git à cet endroit")
    else:
        top = _git(cwd, "rev-parse", "--show-toplevel")
        if top is None or Path(top).resolve() != cwd.resolve():
            problems.append("le chemin n'est pas la racine du dépôt")
        if commit != pinned:
            problems.append(f"commit {commit[:12]} au lieu de {pinned[:12]}")
        if _git(cwd, *_STATUS):
            problems.append("modifications non validées")
        if any(
            line[:1].islower() or line.startswith("S ") for line in (_git(cwd, "ls-files", "-v") or "").splitlines()
        ):
            problems.append("fichiers masqués à Git (assume-unchanged ou skip-worktree)")
    if problems:
        raise SubjectError(f"sujet « {claim.subject} » ({cwd}) : {' ; '.join(problems)}")
    return cwd, pinned, False


def _attempt(
    probe: Probe,
    cwd: Path,
    env: Mapping[str, str],
    timeout_s: int,
    replacements: Sequence[tuple[str, str]],
    withheld: Sequence[str],
) -> tuple[dict[str, Any], str, str | None]:
    tmp = Path(tempfile.mkdtemp(prefix="omega-"))
    try:
        result = execute(probe.command, cwd, scrubbed_env({**env, "OMEGA_TMP": str(tmp)}), timeout_s)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    leak = find_secret(result.output)
    if leak is None and any(value in result.output for value in withheld):
        leak = "valeur d'une variable d'environnement retirée"
    output = sanitize(result.output, [(str(tmp), "<tmp>"), *replacements])
    match = None if probe.output_regex is None else re.search(probe.output_regex, output, re.MULTILINE)
    run = {
        "exit_code": result.exit_code,
        "duration_ms": result.duration_ms,
        "timed_out": result.timed_out,
        "output_sha256": hashlib.sha256(output.encode()).hexdigest(),
        "matched": None if match is None else match.group(0)[:200],  # la ligne de bilan réellement vue
        "ok": _conforms(result.exit_code, result.timed_out, match is not None, probe.exit_code, probe.output_regex),
    }
    return run, output, leak


def _conforms(exit_code: Any, timed_out: Any, matched: bool, expected_code: Any, regex: Any) -> bool:
    return bool(not timed_out and exit_code == expected_code and (regex is None or matched))


def prove(
    charter: Charter, claim: Claim, *, root: Path, paths: Mapping[str, Path], actor: str, now: datetime
) -> dict[str, Any]:
    """Exécute la capacité (``runs`` fois), puis l'attaque, et renvoie la preuve à consigner (sept champs Ω)."""

    if claim.check is None:
        raise ValueError(f"capacité {claim.id} : aucune commande à exécuter (fonction non construite)")
    cwd, commit, dirty = subject_state(charter, claim, root, paths)
    located = {".": root, **paths}
    replacements = [
        (text, "~" if name == "~" else f"<{'novarys' if name == '.' else name}>")
        for name, path in {**located, "~": Path.home()}.items()
        for text in {str(path), str(path.resolve())}
    ]
    env = {"OMEGA_ROOT": str(root)}
    env.update({f"OMEGA_SUBJECT_{name.upper().replace('-', '_')}": str(path) for name, path in paths.items()})
    withheld = _withheld_values()

    runs: list[dict[str, Any]] = []
    output, leak = "", None
    for _ in range(claim.runs):
        run, output, found = _attempt(claim.check, cwd, env, claim.timeout_s, replacements, withheld)
        runs.append(run)
        leak = leak or found
    attack: dict[str, Any] | None = None
    if claim.falsification is not None:
        run, attack_output, found = _attempt(claim.falsification, cwd, env, claim.timeout_s, replacements, withheld)
        leak = leak or found
        attack = {
            "description": claim.falsification.description,
            "command": claim.falsification.command,
            "expected": {"exit_code": claim.falsification.exit_code, "output_regex": claim.falsification.output_regex},
            **run,
            "output": cap(attack_output)[0],
        }
    status = decide(
        [bool(run["ok"]) for run in runs],
        None if attack is None else bool(attack["ok"]),
        has_summary=claim.check.output_regex is not None,
        has_scope=bool(claim.scope),
        clean=not dirty,
    )
    if leak is not None:  # une preuve qu'on ne peut pas montrer n'en est pas une : rien de la sortie ne reste
        status, output = Status.UNKNOWN, WITHHELD.format(name=leak)
        for attempt in (*runs, *([attack] if attack is not None else [])):
            attempt["output_sha256"] = attempt["matched"] = None
        if attack is not None:
            attack["output"] = output
    shown, truncated = cap(output)
    return {
        "at": now.astimezone(UTC).isoformat(timespec="seconds"),
        "actor": actor,
        "claim": claim.id,
        "claim_sha256": charter.digest(claim),
        "domain": claim.domain,
        "kind": claim.kind,
        "capability": claim.capability,
        "command": claim.check.command,
        "expected": {"exit_code": claim.check.exit_code, "output_regex": claim.check.output_regex},
        "runs": runs,
        "output": shown,
        "output_truncated": truncated,
        "withheld": leak,
        "falsification": attack,
        "status": status.value,
        "impact": None if claim.impact is None else asdict(claim.impact),
        "reproducibility": {"runs": len(runs), "concordant": len({bool(run["ok"]) for run in runs}) == 1},
        "scope": claim.scope,
        "limits": claim.limits,
        "subject": {"name": claim.subject, "commit": commit, "dirty": dirty},
        "environment": {"python": platform.python_version(), "system": f"{platform.system()} {platform.machine()}"},
    }


def inconsistencies(record: dict[str, Any]) -> list[str]:
    """Ce qui, dans une preuve consignée, ne découle pas de ses propres exécutions.

    Attrape un statut retouché à la main, même rescellé. N'attrape pas une preuve inventée de bout en bout :
    celle-là ne se démasque qu'en la rejouant (``omega verify``).
    """

    missing = [key for key in _RECORD_KEYS if key not in record]
    if missing:
        return [f"champs manquants {missing}"]
    try:
        if record.get("withheld"):
            return [] if record["status"] == Status.UNKNOWN else ["sortie retenue mais statut autre qu'INCONNU"]
        attack = record["falsification"]
        attempts = [(run, record["expected"]) for run in record["runs"]]
        attempts += [(attack, attack["expected"])] if attack is not None else []
        problems = [
            "une exécution est notée conforme sans l'être, ou l'inverse"
            for run, expected in attempts
            if bool(run["ok"])
            != _conforms(
                run["exit_code"],
                run["timed_out"],
                run["matched"] is not None,
                expected["exit_code"],
                expected["output_regex"],
            )
        ]
        status = decide(
            [bool(run["ok"]) for run in record["runs"]],
            None if attack is None else bool(attack["ok"]),
            has_summary=record["expected"]["output_regex"] is not None,
            has_scope=bool(record["scope"]),
            clean=not record["subject"]["dirty"],
        )
        if record["status"] != status:
            problems.append(f"statut {record['status']} alors que les exécutions consignées donnent {status.value}")
        return list(dict.fromkeys(problems))
    except (KeyError, TypeError) as exc:
        return [f"structure invalide ({exc!r})"]
