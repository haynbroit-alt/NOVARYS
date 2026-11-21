from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from novarys_omega.model import Charter

VALID = """
[subjects.moteur]
repo = "exemple/moteur"
commit = "0123456789abcdef0123456789abcdef01234567"
path = "../moteur"

[[claim]]
id = "addition"
domain = "CORE"
capability = "Additionner deux entiers"
kind = "reel"
subject = "moteur"
command = "echo 2"
output_regex = '^2$'
scope = "entiers positifs"
limits = "aucun dépassement testé"
tags = ["ci", "scenario-6"]

[claim.falsification]
description = "Une addition fausse doit être refusée"
command = "false"
exit_code = 1

[claim.impact]
beneficiaries = "le propriétaire"
indicator = "additions justes"
method = "comptage"
counterfactual = "calcul à la main"

[[claim]]
id = "recherche-web"
domain = "INTERNET"
capability = "Recherche multi-source"
"""


def test_loads_a_valid_charter(charter: Callable[[str], Charter]) -> None:
    loaded = charter(VALID)
    built, missing = loaded.claims
    assert built.check is not None and built.check.output_regex == "^2$"
    assert built.falsification is not None and built.falsification.exit_code == 1
    assert built.impact is not None and built.impact.counterfactual == "calcul à la main"
    assert (built.kind, built.subject, built.runs, built.tags) == ("reel", "moteur", 2, ("ci", "scenario-6"))
    assert missing.check is None  # exigée par le cahier des charges, non construite


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ('id = "addition"', 'id = "Addition 1"', "identifiant invalide"),
        ('id = "recherche-web"', 'id = "addition"', "en double"),
        ('domain = "CORE"', 'domain = "MAGIE"', "domaine inconnu"),
        ('kind = "reel"', 'kind = "promis"', "nature inconnue"),
        ('subject = "moteur"', 'subject = "ailleurs"', "sujet non déclaré"),
        ("output_regex = '^2$'", "output_regex = '('", "expression régulière invalide"),
        ('scope = "entiers positifs"', 'scope = "x"\nstatus = "PROUVE"', "clés inconnues"),
        ('description = "Une addition fausse doit être refusée"\n', "", "décrire l'attaque"),
        ('counterfactual = "calcul à la main"\n', "", "obligatoire"),
        ('commit = "0123456789abcdef0123456789abcdef01234567"', 'commit = "main"', "commit épinglé invalide"),
        ('capability = "Recherche multi-source"', 'capability = "x"\nexit_code = 0', "sans commande"),
        ('command = "echo 2"', 'command = "echo 2"\nruns = 0', "entier ≥ 1"),
        # Une « ligne de bilan » qu'une sortie vide satisfait ne prouve rien.
        ("output_regex = '^2$'", "output_regex = ''", "sortie vide"),
        ("output_regex = '^2$'", "output_regex = '.*'", "sortie vide"),
        # L'attaque ne peut pas être la commande de preuve elle-même.
        ('command = "false"\nexit_code = 1', 'command = "echo 2"\nexit_code = 0', "commande de preuve elle-même"),
        # Mauvais types : un message clair, jamais une trace d'exécution.
        ('capability = "Recherche multi-source"', 'capability = "x"\ncommand = "true"\nfalsification = ""', "table"),
        ('capability = "Recherche multi-source"', 'capability = "x"\ncommand = "true"\nimpact = 3', "table"),
        ('tags = ["ci", "scenario-6"]', 'tags = "ci"', "liste de textes"),
        ('tags = ["ci", "scenario-6"]', 'tags = []\ncovers = ["absent.py"]', "chemin introuvable"),
        ('tags = ["ci", "scenario-6"]', 'tags = []\ncovers = ["../ailleurs"]', "chemin introuvable"),
    ],
)
def test_rejects_an_invalid_charter(charter: Callable[[str], Charter], old: str, new: str, message: str) -> None:
    assert old in VALID
    with pytest.raises(ValueError, match=message):
        charter(VALID.replace(old, new, 1))


def test_wrong_top_level_types_are_rejected(charter: Callable[[str], Charter]) -> None:
    for text, message in [("subjects = []", "table est attendue"), ("claim = 3", "liste de tables")]:
        with pytest.raises(ValueError, match=message):
            charter(text)


def test_digest_follows_what_is_claimed_not_its_commentary(charter: Callable[[str], Charter]) -> None:
    def digest(text: str) -> str:
        loaded = charter(text)
        return loaded.digest(loaded.claims[0])

    reference = digest(VALID)
    assert digest(VALID.replace("aucun dépassement testé", "autre limite")) == reference  # commentaire
    assert digest(VALID.replace('indicator = "additions justes"', 'indicator = "autre"')) == reference
    for old, new in [
        ('command = "echo 2"', 'command = "echo  2"'),
        ("output_regex = '^2$'", "output_regex = '2'"),
        ('command = "false"', 'command = "exit 1"'),
        ("0123456789abcdef0123456789abcdef01234567", "1123456789abcdef0123456789abcdef01234567"),
        ('scope = "entiers positifs"', 'scope = "tous les entiers"'),
        # Le classement change où la preuve compte : il fait partie de ce qui est revendiqué.
        ('domain = "CORE"', 'domain = "SOVEREIGN"'),
        ('tags = ["ci", "scenario-6"]', 'tags = ["ci", "scenario-5"]'),
        ('description = "Une addition fausse doit être refusée"', 'description = "Autre attaque"'),
        ('command = "echo 2"', 'command = "echo 2"\ntimeout_s = 5'),
    ]:
        assert digest(VALID.replace(old, new)) != reference, old


def test_digest_covers_the_files_the_proof_depends_on(root: Path, charter: Callable[[str], Charter]) -> None:
    probes = root / "registre" / "sondes"
    probes.mkdir()
    (probes / "p.sh").write_text("echo ok\n", encoding="utf-8")
    (probes / "autre.sh").write_text("echo autre\n", encoding="utf-8")
    (root / "code").mkdir()
    (root / "code" / "outil.py").write_text("x = 1\n", encoding="utf-8")
    text = """
[[claim]]
id = "par-sonde"
domain = "OMEGA"
capability = "Prouvée par un script"
command = 'bash "$OMEGA_ROOT/registre/sondes/p.sh"'

[[claim]]
id = "sur-le-code"
domain = "OMEGA"
capability = "Porte sur le code de ce dépôt"
command = "true"
covers = ["code"]
"""

    def digests() -> tuple[str, str]:
        loaded = charter(text)
        return loaded.digest(loaded.claims[0]), loaded.digest(loaded.claims[1])

    by_probe, on_code = digests()
    (probes / "autre.sh").write_text("echo modifié\n", encoding="utf-8")  # script que personne ne cite
    assert digests() == (by_probe, on_code)
    (probes / "p.sh").write_text("echo ok # assoupli\n", encoding="utf-8")  # le script qui fait la preuve
    changed, untouched = digests()
    assert changed != by_probe and untouched == on_code
    (root / "code" / "outil.py").write_text("x = 2\n", encoding="utf-8")  # le code que la preuve couvre
    assert digests()[0] == changed and digests()[1] != on_code
