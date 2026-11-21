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
from novarys_omega.runner import (
    SubjectError,
    cap,
    decide,
    execute,
    find_secret,
    inconsistencies,
    prove,
    scrubbed_env,
)

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
ATTACK = 'command = "false"\nexit_code = 1\n'


def proof(root: Path, loaded: Charter, **paths: Path) -> dict[str, Any]:
    return prove(loaded, loaded.claims[0], root=root, paths=paths, actor="test", now=NOW)


@pytest.mark.parametrize(
    ("checks", "attack", "summary", "scope", "clean", "expected"),
    [
        ([], None, True, True, True, Status.UNKNOWN),
        ([False, False], True, True, True, True, Status.FAILED),
        ([True, False], True, True, True, True, Status.CONFLICT),
        ([True, True], False, True, True, True, Status.FAILED),  # l'attaque est passée : capacité réfutée
        ([True, True], True, True, True, True, Status.PROVEN),
        ([True, True], None, True, True, True, Status.SUPPORTED),  # aucune tentative de réfutation
        ([True], True, True, True, True, Status.SUPPORTED),  # non reproduite
        ([True, True], True, False, True, True, Status.SUPPORTED),  # ligne de bilan non exigée
        ([True, True], True, True, False, True, Status.SUPPORTED),  # périmètre non écrit
        ([True, True], True, True, True, False, Status.SUPPORTED),  # code non validé dans Git
    ],
)
def test_status_is_computed_from_evidence(
    checks: list[bool], attack: bool | None, summary: bool, scope: bool, clean: bool, expected: Status
) -> None:
    assert decide(checks, attack, has_summary=summary, has_scope=scope, clean=clean) == expected


def test_execute_never_hides_a_failure_and_stops_runaway_commands(tmp_path: Path) -> None:
    piped = execute("false | cat", tmp_path, scrubbed_env({}), 10)
    assert piped.exit_code == 1  # pipefail : l'échec en amont du pipe reste visible
    mixed = execute("echo sortie; echo erreur >&2; exit 3", tmp_path, scrubbed_env({}), 10)
    assert (mixed.exit_code, mixed.output) == (3, "sortie\nerreur\n")
    started = time.monotonic()
    stuck = execute("sleep 30 & sleep 30", tmp_path, scrubbed_env({}), 1)
    assert stuck.timed_out and stuck.exit_code is None
    # Un descendant détaché (nouvelle session) échappe au signal : il ne doit pas retenir l'outil pour autant.
    escaped = execute("setsid sleep 8 & echo lancé; sleep 30", tmp_path, scrubbed_env({}), 1)
    assert escaped.timed_out and escaped.output == "lancé\n" and time.monotonic() - started < 7


def test_commands_run_without_the_session_secrets(
    root: Path, charter: Callable[[str], Charter], monkeypatch: pytest.MonkeyPatch
) -> None:
    hidden = ("DEMO_API_KEY", "GH_TOKEN", "GIT_CONFIG_COUNT", "DB_PASSWORD", "SSH_PASSPHRASE", "GIT_ASKPASS")
    command = f'printenv {" ".join(hidden)} VIRTUAL_ENV; echo "$DEMO_VISIBLE $OMEGA_ROOT $OMEGA_TMP"'
    loaded = charter(CLAIM + f"command = '''{command}'''\nruns = 1\n")  # avant de piéger l'environnement
    for name in (*hidden, "SENTRY_DSN", "DATABASE_URL", "GH_PAT"):
        monkeypatch.setenv(name, "valeur-sensible")
    monkeypatch.setenv("DEMO_VISIBLE", "visible")
    monkeypatch.setenv("VIRTUAL_ENV", "/ailleurs/.venv")
    record = proof(root, loaded)
    assert "valeur-sensible" not in json.dumps(record)
    assert record["output"] == "visible <novarys> <tmp>\n"  # chemins locaux remplacés par des repères

    # Un secret rangé sous un nom anodin part aussi ; l'adresse du proxy reste, sinon plus de réseau.
    monkeypatch.setenv("NOM_ANODIN", "AKIA" + "Q" * 16)
    monkeypatch.setenv("DEMO_PROXY", "http://utilisateur:motdepasse@proxy.invalid:8080")
    env = scrubbed_env({"OMEGA_ROOT": "x"})
    assert not {*hidden, "NOM_ANODIN", "SENTRY_DSN", "DATABASE_URL", "GH_PAT", "VIRTUAL_ENV"} & set(env)
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
    assert inconsistencies(record) == []  # ce que l'outil consigne se recalcule à l'identique
    if expected == Status.PROVEN:
        assert record["runs"][0]["matched"] == "ok"  # la ligne de bilan réellement vue est conservée


def test_an_incomplete_proof_is_only_supported(root: Path, charter: Callable[[str], Charter]) -> None:
    assert proof(root, charter(CLAIM + 'command = "echo ok"\n'))["status"] == Status.SUPPORTED
    # Complète en tout point, mais sur un dépôt qui a du travail non validé : non reproductible par un tiers.
    loaded = charter(CLAIM + 'command = "echo ok"' + COMPLETE + ATTACK)
    (root / "brouillon.py").write_text("", encoding="utf-8")
    record = proof(root, loaded)
    assert (record["status"], record["subject"]["dirty"]) == (Status.SUPPORTED, True)


def test_a_consigned_proof_must_follow_from_its_own_runs(root: Path, charter: Callable[[str], Charter]) -> None:
    failed = proof(root, charter(CLAIM + 'command = "echo ko"' + COMPLETE + ATTACK))
    assert failed["status"] == Status.FAILED and inconsistencies(failed) == []
    assert "statut PROUVE alors que" in inconsistencies({**failed, "status": "PROUVE"})[0]  # statut retouché
    flipped = json.loads(json.dumps(failed))
    for run in flipped["runs"]:
        run["ok"] = True  # exécutions retouchées, sans la ligne de bilan qui irait avec
    assert "notée conforme sans l'être" in inconsistencies({**flipped, "status": "PROUVE"})[0]
    assert "champs manquants" in inconsistencies({"status": "PROUVE"})[0]
    assert "structure invalide" in inconsistencies({**failed, "runs": [{}]})[0]


def test_a_leaked_secret_withholds_everything(
    root: Path, charter: Callable[[str], Charter], monkeypatch: pytest.MonkeyPatch
) -> None:
    secret = "AKIA" + "Q" * 16  # assemblé ici pour qu'aucun motif de clé ne figure dans le dépôt
    command = f"command = '''echo ok {secret[:4]}\"\"{secret[4:]}'''"  # le shell recolle les deux moitiés
    record = proof(root, charter(CLAIM + command + COMPLETE + ATTACK))
    assert (record["status"], record["withheld"]) == (Status.UNKNOWN, "clé AWS")
    assert secret not in json.dumps(record) and "sortie retenue" in record["output"]
    assert all(run["output_sha256"] is None and run["matched"] is None for run in record["runs"])
    assert inconsistencies(record) == []

    # La valeur d'une variable retirée qui ressort dans une sortie, quel que soit son format.
    monkeypatch.setenv("DEMO_API_KEY", "format-inconnu-des-motifs")
    record = proof(root, charter(CLAIM + 'command = "echo ok format-inconnu-des-motifs"' + COMPLETE + ATTACK))
    assert record["status"] == Status.UNKNOWN and "variable d'environnement retirée" in record["withheld"]
    assert "format-inconnu-des-motifs" not in json.dumps({k: v for k, v in record.items() if k != "command"})


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("https://utilisateur:motdepasse@exemple.invalid/x", "identifiants dans une URL"),
        ("https://" + "jeton" * 5 + "@exemple.invalid/x", "identifiants dans une URL"),
        ("github_pat_" + "A1b2C3d4E5" * 3, "jeton GitHub"),
        ("glpat-" + "A1b2C3d4E5" * 2, "jeton GitLab"),
        ("eyJ" + "a" * 12 + ".eyJ" + "b" * 12 + "." + "c" * 12, "jeton JWT"),
        ("Authorization: Bearer " + "A1b2C3d4E5" * 3, "en-tête d'autorisation"),
        ("-----BEGIN ENCRYPTED PRIVATE KEY-----", "clé privée"),
        ("ASIA" + "Q" * 16, "clé AWS"),
        ("password = " + "A1b2C3d4E5" * 2, "secret en clair"),
        ("https://exemple.invalid:8443/chemin@x", None),
        ("depots=16 secrets=0 lignes_de_code=94603", None),
        ("291 passed in 8.16s", None),
    ],
)
def test_secret_patterns(text: str, expected: str | None) -> None:
    assert find_secret(text) == expected


def test_a_pinned_subject_must_be_at_its_commit_untouched(
    root: Path, charter: Callable[[str], Charter], tmp_path: Path
) -> None:
    engine = tmp_path / "moteur"
    (engine / "sous").mkdir(parents=True)
    git(engine, "init", "-q")
    (engine / "fichier").write_text("v1", encoding="utf-8")
    (engine / "sous" / "x").write_text("", encoding="utf-8")
    git(engine, "add", "-A")
    git(engine, "commit", "-qm", "v1")
    commit = git(engine, "rev-parse", "HEAD")
    text = (
        f'[subjects.moteur]\nrepo = "exemple/moteur"\ncommit = "{commit}"\npath = "../moteur"\n'
        + CLAIM
        + 'subject = "moteur"\ncommand = "cat fichier; echo; pwd"\nruns = 1\n'
    )
    loaded = charter(text)
    record = proof(root, loaded, moteur=engine)
    assert record["subject"] == {"name": "moteur", "commit": commit, "dirty": False}
    assert record["output"] == "v1\n<moteur>\n"

    with pytest.raises(SubjectError, match="pas la racine du dépôt"):  # sous-dossier : le reste échapperait au contrôle
        proof(root, loaded, moteur=engine / "sous")
    (engine / "nouveau").write_text("", encoding="utf-8")  # fichier ajouté, non suivi
    with pytest.raises(SubjectError, match="modifications non validées"):
        proof(root, loaded, moteur=engine)
    (engine / "nouveau").unlink()
    git(engine, "update-index", "--assume-unchanged", "fichier")
    (engine / "fichier").write_text("v2", encoding="utf-8")  # modifié, mais caché à `git status`
    with pytest.raises(SubjectError, match="masqués à Git"):
        proof(root, loaded, moteur=engine)
    git(engine, "update-index", "--no-assume-unchanged", "fichier")
    with pytest.raises(SubjectError, match="modifications non validées"):
        proof(root, loaded, moteur=engine)
    git(engine, "commit", "-qam", "v2")  # autre commit que celui épinglé
    with pytest.raises(SubjectError, match="au lieu de"):
        proof(root, loaded, moteur=engine)
    with pytest.raises(SubjectError, match="aucun dépôt Git"):
        proof(root, loaded, moteur=tmp_path / "absent")


def test_account_names_and_addresses_are_masked(root: Path, charter: Callable[[str], Charter]) -> None:
    command = "echo /home/alice/projet /Users/bob/x /tmp/pytest-of-carol/pytest-1/t contact@exemple.org"
    loaded = charter(CLAIM + f'command = "{command}"\nruns = 1\n')
    (root / "registre" / "preuves.jsonl").write_text("", encoding="utf-8")  # écrits par omega run lui-même :
    (root / "CAPACITES.md").write_text("", encoding="utf-8")  # ils ne rendent pas le dépôt « modifié »
    record = proof(root, loaded)
    masked = "/home/<utilisateur>/projet /Users/<utilisateur>/x /tmp/pytest-of-<utilisateur>/pytest-1/t <adresse>"
    assert record["output"] == f"{masked}\n"
    assert record["subject"]["dirty"] is False


def test_unbuilt_capability_cannot_be_proved(root: Path, charter: Callable[[str], Charter]) -> None:
    with pytest.raises(ValueError, match="non construite"):
        proof(root, charter(CLAIM))


def test_cap_keeps_the_start_and_the_summary() -> None:
    assert cap("court") == ("court", False)
    text, truncated = cap("début" + "x" * 50_000 + "fin: 3 passed")
    assert truncated and text.startswith("début") and text.endswith("fin: 3 passed") and "caractères omis" in text
