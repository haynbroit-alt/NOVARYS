from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from conftest import ASSET
from novarys_omega.model import Charter, Level
from novarys_omega.report import (
    assets_markdown,
    capabilities_markdown,
    level_of,
    load_assets,
    load_connections,
    load_measures,
    load_steps,
    site_pages,
)

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


def test_site_is_six_pages_plus_one_per_asset(tmp_path: Path, charter: Callable[[str], Charter]) -> None:
    path = tmp_path / "actifs.toml"
    path.write_text(ASSET.replace('state = "fictif"', 'state = "<b>fictif</b>"'), encoding="utf-8")
    board = tmp_path / "tableau.toml"
    step = '[[step]]\nlabel = "Auditer"\nstate = "fait"\nsource = "essai"\nlink = "projets.html"\n'
    board.write_text('[[measure]]\nlabel = "Encaissé"\nvalue = "0 €"\nsource = "essai"\n' + step, encoding="utf-8")
    link = tmp_path / "connexions.toml"
    row = '[[connection]]\nservice = "Boutique"\ncategory = "Business"\nstate = "erreur"\naccess = "aucune"\n'
    row += 'tested = "essai"\nprojects = "demo"\ndetail = "refusée"\n'
    link.write_text(row, encoding="utf-8")
    loaded = charter(TEXT)
    proof = record(loaded, loaded.claims[0].id, "PROUVE")

    def build() -> dict[str, str]:
        return site_pages(
            load_assets(path), load_measures(board), load_steps(board), load_connections(link), loaded, [proof]
        )

    pages = build()
    names = ["activite", "connexions", "demo", "index", "intelligence", "parametres", "projets"]
    assert sorted(pages) == [f"{name}.html" for name in names]
    assert all('<a href="parametres.html"' in page and "<nav" in page for page in pages.values())
    assert "<b>0 €</b>" in pages["index.html"] and '<span class="tag bad">erreur</span>' in pages["index.html"]
    assert 'href="demo.html"' in pages["projets.html"] and 'aria-current="page">Projets' in pages["demo.html"]
    assert '<span class="tag ok">fait</span>' in pages["activite.html"] and "PROUVÉ" in pages["activite.html"]
    assert "Matrice complète" in pages["intelligence.html"]
    assert "&lt;b&gt;fictif&lt;/b&gt;" in pages["demo.html"] and "<b>fictif" not in pages["demo.html"]
    path.write_text(ASSET + ASSET.replace('name = "demo"', 'name = "Demo-"'), encoding="utf-8")
    with pytest.raises(ValueError, match="même page"):
        build()
    path.write_text(ASSET.replace('name = "demo"', 'name = "Projets"'), encoding="utf-8")
    with pytest.raises(ValueError, match="réservée"):
        build()
    board.write_text('[[measure]]\nlabel = "Revenus"\nvalue = "1 248 €"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="source"):
        load_measures(board)
    for broken, message in [
        (step.replace("fait", "gagné"), "état inconnu"),
        (step.replace("projets.html", "x"), "lien"),
    ]:
        board.write_text(broken, encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            load_steps(board)
    link.write_text(row.replace('"erreur"', '"branchée"'), encoding="utf-8")
    with pytest.raises(ValueError, match="état inconnu"):
        load_connections(link)
