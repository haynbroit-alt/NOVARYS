from __future__ import annotations

import json
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from conftest import git
from novarys_omega.model import Charter, Status
from novarys_omega.runner import SubjectError, cap, decide, execute, find_secret, prove, scrubbed_env

NOW = datetime(2026, 11, 21, 6, 0, tzinfo=UTC)
CLAIM = """
[[claim]]
id = "c"
domain = "OMEGA"
capability = "Capacité de test"
"""
COMPLETE = """
output_regex = 'ok$'
scope = "périmètre de test"

[claim.falsification]
description = "attaque de test"
"""


def proof(root: Path, loaded: Charter, **paths: Path) -> dict[str, Any]:
    return prove(loaded, loaded.claims[0], root=root, paths=paths, actor="test", now=NOW)


@pytest.mark.parametrize(
    ("checks", "attack", "summary", "scope", "expected"),
    [
        ([], None, True, True, Status.UNKNOWN),
        ([False, False], True, True, True, Status.FAILED),
        ([True, False], True, True, True, Status.CONFLICT),
        ([True, True], False, True, True, Status.FAILED),  # l'attaque est passée : capacité réfutée
        ([True, True], True, True, True, Status.PROVEN),
        ([True, True], None, True, True, Status.SUPPORTED),  # aucune tentative de réfutation
        ([True], True, True, True, Status.SUPPORTED),  # non reproduite
        ([True, True], True, False, True, Status.SUPPORTED),  # ligne de bilan non exigée
        ([True, True], True, True, False, Status.SUPPORTED),  # périmètre non écrit
    ],
)
def test_status_is_computed_from_evidence(
    checks: list[bool], attack: bool | None, summary: bool, scope: bool, expected: Status
) -> None:
    assert decide(checks, attack, has_summary=summary, has_scope=scope) == expected


def test_execute_never_hides_a_failure_and_stops_runaway_commands(tmp_path: Path) -> None:
    piped = execute("false | cat", tmp_path, scrubbed_env({}), 10)
    assert piped.exit_code == 1  # pipefail : l'échec en amont du pipe reste visible
    mixed = execute("echo sortie; echo erreur >&2; exit 3", tmp_path, scrubbed_env({}), 10)
    assert (mixed.exit_code, mixed.output) == (3, "sortie\nerreur\n")
    started = time.monotonic()
    stuck = execute("sleep 30 & sleep 30", tmp_path, scrubbed_env({}), 1)
    assert stuck.timed_out and stuck.exit_code is None and time.monotonic() - started < 10


def test_commands_run_without_the_session_secrets(
    root: Path, charter: Callable[[str], Charter], monkeypatch: pytest.MonkeyPatch
) -> None:
    for name in ("DEMO_API_KEY", "GH_TOKEN", "GIT_CONFIG_COUNT", "DB_PASSWORD"):
        monkeypatch.setenv(name, "valeur-sensible")
    monkeypatch.setenv("DEMO_VISIBLE", "visible")
    command = 'printenv DEMO_API_KEY GH_TOKEN GIT_CONFIG_COUNT DB_PASSWORD; echo "$DEMO_VISIBLE $OMEGA_ROOT $OMEGA_TMP"'
    record = proof(root, charter(CLAIM + f"command = '''{command}'''\nruns = 1\n"))
    assert "valeur-sensible" not in json.dumps(record)
    assert record["output"] == "visible <novarys> <tmp>\n"  # chemins locaux remplacés par des repères

    # Un secret rangé sous un nom anodin part aussi ; l'adresse du proxy reste, sinon plus de réseau.
    monkeypatch.setenv("NOM_ANODIN", "AKIA" + "Q" * 16)
    monkeypatch.setenv("SENTRY_DSN", "valeur-sensible")
    monkeypatch.setenv("DATABASE_URL", "valeur-sensible")
    monkeypatch.setenv("GH_PAT", "valeur-sensible")
    monkeypatch.setenv("DEMO_PROXY", "http://utilisateur:motdepasse@proxy.invalid:8080")
    env = scrubbed_env({"OMEGA_ROOT": "x"})
    assert not {"NOM_ANODIN", "SENTRY_DSN", "DATABASE_URL", "GH_PAT", "DEMO_API_KEY"} & set(env)
    assert env["DEMO_PROXY"].endswith("proxy.invalid:8080") and env["OMEGA_ROOT"] == "x"


@pytest.mark.parametrize(
    ("command", "attack", "expected"),
    [
        ("echo ok", "false", Status.PROVEN),
        ("echo ko", "false", Status.FAILED),  # ligne de bilan absente
        ("echo ok; exit 2", "false", Status.FAILED),  # mauvais code de sortie
        ("echo ok", "true", Status.FAILED),  # l'attaque attendue en échec a réussi
        ("test -e $OMEGA_ROOT/vu || { touch $OMEGA_ROOT/vu; exit 1; }; echo ok", "false", Status.CONFLICT),
    ],
)
def test_prove_end_to_end(
    root: Path, charter: Callable[[str], Charter], command: str, attack: str, expected: Status
) -> None:
    text = CLAIM + f"command = '''{command}'''" + COMPLETE + f'command = "{attack}"\nexit_code = 1\n'
    record = proof(root, charter(text))
    assert record["status"] == expected
    assert record["reproducibility"] == {"runs": 2, "concordant": expected != Status.CONFLICT}
    assert record["falsification"]["ok"] is (attack == "false")
    assert {"capability", "command", "output", "status", "impact", "reproducibility", "limits"} <= set(record)


def test_incomplete_proof_is_only_supported(root: Path, charter: Callable[[str], Charter]) -> None:
    assert proof(root, charter(CLAIM + 'command = "echo ok"\n'))["status"] == Status.SUPPORTED


def test_a_leaked_secret_withholds_the_output(root: Path, charter: Callable[[str], Charter]) -> None:
    secret = "AKIA" + "Q" * 16  # assemblé ici pour qu'aucun motif de clé ne figure dans le dépôt
    command = f"command = '''echo ok {secret[:4]}\"\"{secret[4:]}'''"  # le shell recolle les deux moitiés
    record = proof(root, charter(CLAIM + command + COMPLETE + 'command = "false"\nexit_code = 1\n'))
    assert record["status"] == Status.UNKNOWN
    assert secret not in json.dumps(record) and "sortie retenue" in record["output"]
    assert find_secret("https://utilisateur:motdepasse@exemple.invalid/x") == "identifiants dans une URL"
    assert find_secret("https://exemple.invalid:8443/chemin@x") is None


def test_a_pinned_subject_must_be_at_its_commit_and_clean(
    root: Path, charter: Callable[[str], Charter], tmp_path: Path
) -> None:
    engine = tmp_path / "moteur"
    engine.mkdir()
    git(engine, "init", "-q")
    (engine / "fichier").write_text("v1", encoding="utf-8")
    git(engine, "add", "-A")
    git(engine, "commit", "-qm", "v1")
    commit = git(engine, "rev-parse", "HEAD")
    text = (
        f'[subjects.moteur]\nrepo = "exemple/moteur"\ncommit = "{commit}"\npath = "../moteur"\n'
        + CLAIM
        + 'subject = "moteur"\ncommand = "cat fichier; echo; pwd"\nruns = 1\n'
    )
    record = proof(root, charter(text), moteur=engine)
    assert record["subject"] == {"name": "moteur", "commit": commit, "dirty": False}
    assert record["output"] == "v1\n<moteur>\n"

    (engine / "fichier").write_text("v2", encoding="utf-8")  # modification non validée
    with pytest.raises(SubjectError, match="modifications non validées"):
        proof(root, charter(text), moteur=engine)
    git(engine, "commit", "-qam", "v2")  # autre commit que celui épinglé
    with pytest.raises(SubjectError, match="attendu"):
        proof(root, charter(text), moteur=engine)
    with pytest.raises(SubjectError, match="aucun dépôt Git"):
        proof(root, charter(text), moteur=tmp_path / "absent")


def test_account_names_are_masked_and_own_outputs_do_not_dirty_the_repository(
    root: Path, charter: Callable[[str], Charter], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("VIRTUAL_ENV", "/ailleurs/.venv")
    command = "echo /home/alice/projet /Users/bob/x /tmp/pytest-of-carol/pytest-1/t; echo $VIRTUAL_ENV."
    loaded = charter(CLAIM + f'command = "{command}"\nruns = 1\n')
    git(root, "add", "-A")
    git(root, "commit", "-qm", "référentiel")
    (root / "registre" / "preuves.jsonl").write_text("", encoding="utf-8")  # écrits par omega run lui-même
    (root / "CAPACITES.md").write_text("", encoding="utf-8")
    record = proof(root, loaded)
    masked = "/home/<utilisateur>/projet /Users/<utilisateur>/x /tmp/pytest-of-<utilisateur>/pytest-1/t"
    assert record["output"] == f"{masked}\n.\n"  # et VIRTUAL_ENV n'est pas transmis
    assert record["subject"]["dirty"] is False
    (root / "autre.txt").write_text("", encoding="utf-8")
    assert proof(root, loaded)["subject"]["dirty"] is True


def test_unbuilt_capability_cannot_be_proved(root: Path, charter: Callable[[str], Charter]) -> None:
    with pytest.raises(ValueError, match="non construite"):
        proof(root, charter(CLAIM))


def test_cap_keeps_the_start_and_the_summary() -> None:
    assert cap("court") == ("court", False)
    text, truncated = cap("début" + "x" * 50_000 + "fin: 3 passed")
    assert truncated and text.startswith("début") and text.endswith("fin: 3 passed") and "caractères omis" in text
