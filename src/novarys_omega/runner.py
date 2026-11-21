"""Exécution d'une capacité revendiquée : commande, attaque, reproduction, statut.

Sécurité. Une commande de preuve est du code : le référentiel se relit comme du code, et on n'exécute jamais
celui d'un dépôt qu'on ne maîtrise pas. Les commandes tournent sans les secrets de la session (variables au nom
sensible retirées) et dans un processus distinct de celui qui détient la base financière de SOVEREIGN. Une
sortie est débarrassée de ses chemins locaux, puis retenue si un motif de secret y apparaît. Limite : la
détection par motifs ne remplace pas la relecture du registre avant fusion.
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

OUTPUT_LIMIT = 16_000
WITHHELD = "[sortie retenue : un motif de secret y a été détecté — {name}]"
_SENSITIVE_ENV = re.compile(
    r"(?i)key|token|secret|passw|credential|auth|cookie|private|signature|dsn|webhook|_pat$|database_url|conn"
)
# Motifs repris de l'observateur de SOVEREIGN (``sovereign/ecosystem.py``), plus les identifiants dans une URL.
_SECRETS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("clé AWS", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("clé Anthropic", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("clé OpenAI", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{32,}")),
    ("jeton GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}")),
    ("jeton Slack", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("clé Google", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}")),
    ("clé Stripe", re.compile(r"\b(?:[sr]k_live|whsec)_[A-Za-z0-9]{20,}")),
    ("clé privée", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("identifiants dans une URL", re.compile(r"[a-z][a-z0-9+.\-]*://[^\s/:@]+:[^\s/@]+@")),
)


# Chemins qui portent un nom de compte : dossiers personnels d'autres comptes, dossiers temporaires de pytest.
_USER_PATH = re.compile(r"""(/(?:home|Users)/|pytest-of-)[^/\s"']+""")
# Fichiers que `omega run` écrit lui-même : ils ne rendent pas « modifié » le dépôt qui porte le registre.
_OWN_OUTPUTS = (":(exclude)registre/preuves.jsonl", ":(exclude)CAPACITES.md", ":(exclude)ACTIFS.md")


class SubjectError(RuntimeError):
    """Le dépôt visé n'est pas dans l'état épinglé par le référentiel."""


@dataclass(frozen=True)
class Execution:
    exit_code: int | None
    output: str
    duration_ms: int
    timed_out: bool


def scrubbed_env(extra: Mapping[str, str]) -> dict[str, str]:
    """Environnement de la session sans ses secrets. ``GIT_CONFIG_*`` part aussi : il porte souvent un jeton."""

    env = {
        name: value
        for name, value in os.environ.items()
        if not _SENSITIVE_ENV.search(name)
        and not name.startswith("GIT_CONFIG_")
        # Un secret rangé sous un nom anodin part aussi. Exception : l'adresse du proxy, sans laquelle il n'y a
        # plus de réseau ; si elle porte des identifiants, c'est le contrôle des sorties qui les retient.
        and ("proxy" in name.lower() or find_secret(value) is None)
    }
    env.pop("VIRTUAL_ENV", None)  # la preuve ne doit pas dépendre de l'environnement Python qui a lancé omega
    env.update(extra)
    return env


def execute(command: str, cwd: Path, env: Mapping[str, str], timeout_s: int) -> Execution:
    """Lance la commande sous ``bash -o pipefail`` (un échec en amont d'un pipe n'est jamais masqué)."""

    started = time.monotonic()
    process = subprocess.Popen(
        ["bash", "-o", "pipefail", "-c", command],
        cwd=cwd,
        env=dict(env),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    try:
        raw, _ = process.communicate(timeout=timeout_s)
        timed_out = False
    except subprocess.TimeoutExpired:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGKILL)  # la commande et tout ce qu'elle a lancé
        try:
            raw, _ = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:  # un descendant détaché tient encore la sortie : on n'attend pas
            raw = b""
        timed_out = True
    duration_ms = int((time.monotonic() - started) * 1000)
    return Execution(None if timed_out else process.returncode, raw.decode("utf-8", "replace"), duration_ms, timed_out)


def find_secret(text: str) -> str | None:
    return next((name for name, pattern in _SECRETS if pattern.search(text)), None)


def sanitize(text: str, replacements: Sequence[tuple[str, str]]) -> str:
    """Remplace les chemins locaux (qui peuvent contenir un nom d'utilisateur) par des repères stables."""

    for path, marker in sorted(replacements, key=lambda pair: -len(pair[0])):
        if len(path) > 3:
            text = text.replace(path, marker)
    return _USER_PATH.sub(lambda match: f"{match.group(1)}<utilisateur>", text)


def cap(text: str, limit: int = OUTPUT_LIMIT) -> tuple[str, bool]:
    """Sortie brute, coupée au milieu au-delà de ``limit`` : le début et la fin (le bilan) sont conservés."""

    if len(text) <= limit:
        return text, False
    head = limit // 4
    return f"{text[:head]}\n[… {len(text) - limit} caractères omis …]\n{text[-(limit - head) :]}", True


def decide(checks: Sequence[bool], attack_resisted: bool | None, *, has_summary: bool, has_scope: bool) -> Status:
    """Statut d'une preuve, calculé et jamais déclaré.

    PROUVÉ exige : au moins deux exécutions concordantes, la ligne de bilan attendue, un périmètre écrit et une
    tentative de réfutation exécutée à laquelle la capacité a résisté. Une attaque qui passe réfute la capacité.
    """

    if not checks:
        return Status.UNKNOWN
    if not any(checks):
        return Status.FAILED
    if not all(checks):
        return Status.CONFLICT
    if attack_resisted is False:
        return Status.FAILED
    if len(checks) >= 2 and attack_resisted and has_summary and has_scope:
        return Status.PROVEN
    return Status.SUPPORTED


def _git(path: Path, *args: str) -> str | None:
    done = subprocess.run(
        ["git", "-C", str(path), *args], env=scrubbed_env({}), capture_output=True, text=True, check=False
    )
    return done.stdout.strip() if done.returncode == 0 else None


def _attempt(
    probe: Probe, cwd: Path, env: Mapping[str, str], timeout_s: int, replacements: Sequence[tuple[str, str]]
) -> tuple[dict[str, Any], str]:
    tmp = Path(tempfile.mkdtemp(prefix="omega-"))
    try:
        result = execute(probe.command, cwd, scrubbed_env({**env, "OMEGA_TMP": str(tmp)}), timeout_s)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    output = sanitize(result.output, [(str(tmp), "<tmp>"), *replacements])
    matched = probe.output_regex is None or re.search(probe.output_regex, output, re.MULTILINE) is not None
    run = {
        "exit_code": result.exit_code,
        "duration_ms": result.duration_ms,
        "timed_out": result.timed_out,
        "output_sha256": hashlib.sha256(output.encode()).hexdigest(),
        "ok": not result.timed_out and result.exit_code == probe.exit_code and matched,
    }
    return run, output


def prove(
    charter: Charter, claim: Claim, *, root: Path, paths: Mapping[str, Path], actor: str, now: datetime
) -> dict[str, Any]:
    """Exécute la capacité (``runs`` fois), puis l'attaque, et renvoie la preuve à consigner (sept champs Ω)."""

    if claim.check is None:
        raise ValueError(f"capacité {claim.id} : aucune commande à exécuter (fonction non construite)")
    cwd = root if claim.subject == "." else paths[claim.subject]
    commit = _git(cwd, "rev-parse", "HEAD") or ""
    dirty = bool(_git(cwd, "status", "--porcelain", "--", ".", *(_OWN_OUTPUTS if claim.subject == "." else ())))
    if claim.subject != ".":
        pinned = charter.subjects[claim.subject].commit
        if commit != pinned or dirty:
            found = f"{commit[:12] or 'aucun dépôt Git'}{' avec modifications non validées' if dirty else ''}"
            raise SubjectError(f"sujet « {claim.subject} » : {pinned[:12]} attendu, sans modification ; trouvé {found}")
    located = {".": root, **paths}
    replacements = [
        (text, "~" if name == "~" else f"<{'novarys' if name == '.' else name}>")
        for name, path in {**located, "~": Path.home()}.items()
        for text in {str(path), str(path.resolve())}
    ]
    env = {"OMEGA_ROOT": str(root)}
    env.update({f"OMEGA_SUBJECT_{name.upper().replace('-', '_')}": str(path) for name, path in paths.items()})

    runs: list[dict[str, Any]] = []
    output = ""
    for _ in range(claim.runs):
        run, output = _attempt(claim.check, cwd, env, claim.timeout_s, replacements)
        runs.append(run)
    leak = find_secret(output)
    attack: dict[str, Any] | None = None
    if claim.falsification is not None:
        run, attack_output = _attempt(claim.falsification, cwd, env, claim.timeout_s, replacements)
        leak = leak or find_secret(attack_output)
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
    )
    if leak is not None:  # une preuve qu'on ne peut pas montrer n'en est pas une
        status, output = Status.UNKNOWN, WITHHELD.format(name=leak)
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
        "falsification": attack,
        "status": status.value,
        "impact": None if claim.impact is None else asdict(claim.impact),
        "reproducibility": {"runs": len(runs), "concordant": len({bool(run["ok"]) for run in runs}) == 1},
        "scope": claim.scope,
        "limits": claim.limits,
        "subject": {"name": claim.subject, "commit": commit, "dirty": dirty},
        "environment": {"python": platform.python_version(), "system": f"{platform.system()} {platform.machine()}"},
    }
