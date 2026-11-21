from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from novarys_omega import registry
from novarys_omega.cli import main
from novarys_omega.model import Charter

TEXT = """
[[claim]]
id = "stable"
domain = "OMEGA"
capability = "Une fonction qui tient"
command = "test -e $OMEGA_ROOT/presence && echo ok"
output_regex = 'ok$'
scope = "test"
tags = ["ci"]

[claim.falsification]
description = "attaque de test"
command = "false"
exit_code = 1

[[claim]]
id = "cassee"
domain = "OMEGA"
capability = "Une fonction cassée"
command = "false"

[[claim]]
id = "absente"
domain = "INTERNET"
capability = "Une fonction non construite"
"""


@pytest.fixture
def ready(root: Path, charter: Callable[[str], Charter]) -> Path:
    (root / "presence").write_text("", encoding="utf-8")
    charter(TEXT)
    return root


def omega(root: Path, *args: str) -> int:
    return main(["--root", str(root), *args])


def test_run_records_proofs_and_keeps_failures(ready: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert omega(ready, "run") == 1  # une capacité en échec : le code de sortie le dit
    out = capsys.readouterr().out
    assert "PROUVÉ   stable (preuve n°1)" in out and "ÉCHEC    cassee (preuve n°2)" in out and "absente" not in out
    records = registry.read(ready / "registre" / "preuves.jsonl")
    assert [(r["claim"], r["status"], r["actor"]) for r in records] == [
        ("stable", "PROUVE", "local"),
        ("cassee", "ECHEC", "local"),
    ]
    assert "ÉCHEC" in (ready / "CAPACITES.md").read_text(encoding="utf-8")  # l'échec reste affiché
    assert omega(ready, "check") == 0
    assert "2 preuve(s) chaînée(s), 3 capacité(s)" in capsys.readouterr().out


def test_selection_by_id_tag_and_actor(ready: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert omega(ready, "run", "--tag", "ci", "--actor", "ci") == 0
    assert omega(ready, "run", "--only", "stable") == 0
    records = registry.read(ready / "registre" / "preuves.jsonl")
    assert [(r["claim"], r["actor"]) for r in records] == [("stable", "ci"), ("stable", "local")]
    # Données de test : même prouvée par deux acteurs, la fonction reste TESTÉE.
    assert "(`stable`) | PROUVÉ | TESTÉ |" in (ready / "CAPACITES.md").read_text(encoding="utf-8")
    assert omega(ready, "run", "--only", "inconnue") == 2
    assert "capacités inconnues : inconnue" in capsys.readouterr().err


def test_check_catches_tampering_stale_files_and_removed_proofs(
    ready: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    omega(ready, "run")
    proofs = ready / "registre" / "preuves.jsonl"
    base = ready / "base.jsonl"
    base.write_text(proofs.read_text(encoding="utf-8"), encoding="utf-8")
    assert omega(ready, "check", "--base", str(base)) == 0
    assert omega(ready, "check", "--base", str(ready / "absent.jsonl")) == 2  # chemin erroné : on bloque

    original = proofs.read_text(encoding="utf-8")
    proofs.write_text(original.replace('"status":"ECHEC"', '"status":"PROUVE"'), encoding="utf-8")  # échec maquillé
    assert omega(ready, "check") == 1
    assert "contenu modifié" in capsys.readouterr().out

    forged = [json.loads(line) for line in original.splitlines()]
    forged[1]["status"] = "PROUVE"  # échec maquillé PUIS rescellé : la chaîne est valide, le statut ne l'est pas
    forged[1]["hash"] = registry.seal(forged[1])
    proofs.write_text("".join(registry.canonical(r) + "\n" for r in forged), encoding="utf-8")
    assert omega(ready, "check") == 1
    assert "preuve n°2 : statut PROUVE alors que les exécutions consignées donnent ECHEC" in capsys.readouterr().out

    proofs.write_text(original.splitlines(keepends=True)[0], encoding="utf-8")  # échec retiré de la fin
    omega(ready, "render")
    assert omega(ready, "check") == 0  # la chaîne seule ne voit pas la troncature…
    assert omega(ready, "check", "--base", str(base)) == 1  # … la comparaison à la base, si
    assert "ne prolonge pas" in capsys.readouterr().out

    proofs.write_text(original, encoding="utf-8")
    assert omega(ready, "check") == 1  # CAPACITES.md ne correspond plus au registre
    assert "CAPACITES.md n'est pas à jour" in capsys.readouterr().out


def test_verify_reports_a_regression_without_writing(ready: Path, capsys: pytest.CaptureFixture[str]) -> None:
    omega(ready, "run")
    proofs = ready / "registre" / "preuves.jsonl"
    before = proofs.read_text(encoding="utf-8")
    assert omega(ready, "verify") == 0
    assert "conforme   stable : registre PROUVÉ, maintenant PROUVÉ" in capsys.readouterr().out
    (ready / "presence").unlink()  # la fonction ne tient plus
    assert omega(ready, "verify") == 1
    assert "RÉGRESSION stable : registre PROUVÉ, maintenant ÉCHEC" in capsys.readouterr().out
    assert proofs.read_text(encoding="utf-8") == before


def test_invalid_input_blocks_with_a_clear_message(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert omega(root, "check") == 2  # pas de référentiel
    target = root / "registre" / "capacites.toml"
    target.write_text(TEXT.replace('domain = "INTERNET"', 'domain = "MAGIE"'), encoding="utf-8")
    assert omega(root, "render") == 2
    assert "domaine inconnu" in capsys.readouterr().err
    target.write_text(
        TEXT.replace('command = "false"\n\n', 'command = "false"\nfalsification = ""\n\n'), encoding="utf-8"
    )
    assert omega(root, "render") == 2  # mauvais type : message clair, pas de trace d'exécution
    assert "une table est attendue" in capsys.readouterr().err
    target.write_text(TEXT, encoding="utf-8")
    assert omega(root, "run", "--subject", "moteur") == 2
    assert "NOM=CHEMIN" in capsys.readouterr().err
