from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from conftest import ASSET
from novarys_omega.model import Charter, Level
from novarys_omega.report import assets_markdown, capabilities_markdown, level_of, load_assets

TEXT = """
[[claim]]
id = "testee"
domain = "CORE"
capability = "Fonction prouvée sur données de test"
command = "true"
limits = "une | limite"

[[claim]]
id = "reelle"
domain = "SOVEREIGN"
capability = "Fonction prouvée sur données réelles"
kind = "reel"
command = "true"
tags = ["scenario-6"]

[[claim]]
id = "absente"
domain = "INTERNET"
capability = "Fonction non construite"
tags = ["scenario-1"]
"""


def record(loaded: Charter, claim_id: str, status: str, actor: str = "local", seq: int = 1) -> dict[str, Any]:
    claim = next(c for c in loaded.claims if c.id == claim_id)
    return {
        "seq": seq,
        "at": "2026-11-21T06:00:00+00:00",
        "actor": actor,
        "claim": claim_id,
        "claim_sha256": loaded.digest(claim),
        "status": status,
        "runs": [{}, {}],
        "falsification": {"ok": True},
        "subject": {"name": ".", "commit": "abcdef1234567890", "dirty": False},
    }


def test_level_is_deduced_from_proofs(charter: Callable[[str], Charter]) -> None:
    loaded = charter(TEXT)
    tested, real, absent = loaded.claims
    assert level_of(loaded, absent, []) == Level.ABSENT
    assert level_of(loaded, tested, []) == Level.AVAILABLE
    for status, expected in [("ECHEC", Level.AVAILABLE), ("CONFLIT", Level.AVAILABLE), ("INCONNU", Level.AVAILABLE)]:
        assert level_of(loaded, tested, [record(loaded, "testee", status)]) == expected
    assert level_of(loaded, tested, [record(loaded, "testee", "ETAYE")]) == Level.CONNECTED
    assert level_of(loaded, tested, [record(loaded, "testee", "PROUVE")]) == Level.TESTED
    assert level_of(loaded, real, [record(loaded, "reelle", "PROUVE")]) == Level.OPERATIONAL
    # Une preuve ultérieure en échec fait redescendre le niveau : seul le dernier état compte.
    assert (
        level_of(loaded, real, [record(loaded, "reelle", "PROUVE"), record(loaded, "reelle", "ECHEC")])
        == Level.AVAILABLE
    )
    # Un nom d'acteur est une déclaration : deux noms différents ne valident rien. VALIDÉ n'est jamais attribué.
    two_names = [record(loaded, "reelle", "PROUVE"), record(loaded, "reelle", "PROUVE", actor="ci")]
    assert level_of(loaded, real, two_names) == Level.OPERATIONAL
    # Des données de test, même reproduites ailleurs, ne rendent pas une fonction opérationnelle.
    both = [record(loaded, "testee", "PROUVE"), record(loaded, "testee", "PROUVE", actor="ci")]
    assert level_of(loaded, tested, both) == Level.TESTED


def test_a_changed_claim_loses_its_old_proofs(charter: Callable[[str], Charter]) -> None:
    before = charter(TEXT)
    proofs = [record(before, "testee", "PROUVE")]
    after = charter(TEXT.replace('command = "true"\nlimits', 'command = "true # assoupli"\nlimits'))
    assert level_of(after, after.claims[0], proofs) == Level.AVAILABLE
    assert "preuve périmée" in capabilities_markdown(after, proofs)


def test_matrix_states_the_verdict_and_hides_nothing(charter: Callable[[str], Charter]) -> None:
    loaded = charter(TEXT)
    proofs = [record(loaded, "testee", "PROUVE"), record(loaded, "reelle", "PROUVE", seq=2)]
    text = capabilities_markdown(loaded, proofs)
    assert text == capabilities_markdown(loaded, proofs)  # déterministe : la CI peut vérifier qu'il est à jour
    assert "NOVARYS n'est pas opérationnel" in text and "1 fonction(s) sur 3 sont sous le niveau TESTÉ" in text
    assert "| 1 | Recherche multi-source vérifiée | `absente` | ABSENT |" in text
    assert "| 6 | Blocage d'une action non autorisée et protection des secrets | `reelle` | OPÉRATIONNEL |" in text
    assert "| 7 | Reproduction indépendante d'une capacité | aucune | ABSENT |" in text
    assert "(`absente`) | — | ABSENT | non construite |" in text
    assert "une \\| limite" in text  # une barre verticale ne casse pas le tableau
    assert "· ce dépôt@abcdef12 · 2 exécution(s) · attaque résistée · n°2" in text


def test_verdict_is_operational_only_when_every_domain_is_demonstrated(charter: Callable[[str], Charter]) -> None:
    domains = ["CORE", "INTELLIGENCE", "DISCOVERY", "INTERNET", "ENGINEERING", "BUSINESS", "AGENTS", "MEMORY"]
    text = "".join(
        f'[[claim]]\nid = "f{i}"\ndomain = "{d}"\ncapability = "x"\nkind = "reel"\ncommand = "true"\n'
        for i, d in enumerate([*domains, "OMEGA", "SOVEREIGN"])
    )
    loaded = charter(text)
    proofs = [record(loaded, c.id, "PROUVE") for c in loaded.claims]
    assert "NOVARYS est opérationnel" in capabilities_markdown(loaded, proofs)
    assert "1 domaine(s) sur 10 n'ont aucune fonction démontrée" in capabilities_markdown(loaded, proofs[:-1])


def test_assets_need_every_heading(tmp_path: Path) -> None:
    path = tmp_path / "actifs.toml"
    path.write_text(ASSET, encoding="utf-8")
    text = assets_markdown(load_assets(path))
    assert "| **demo** — Démonstration | fictif | aucun | aucune |" in text
    assert "- **Prochaine action rentable** : aucune" in text and "Observé le 2026-11-21." in text
    for broken, message in [
        (ASSET.replace('blockers = "aucun"\n', ""), "rubrique « blockers » manquante"),
        (ASSET.replace('costs = "0 €"', 'costs = ""'), "rubrique « costs » manquante"),
        (ASSET + 'revenue = "1 000 €"\n', "clés inconnues"),
        (ASSET + ASSET, "nom en double"),
    ]:
        path.write_text(broken, encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            load_assets(path)
