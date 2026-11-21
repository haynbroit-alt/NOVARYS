from __future__ import annotations

from collections.abc import Callable

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
    ],
)
def test_rejects_an_invalid_charter(charter: Callable[[str], Charter], old: str, new: str, message: str) -> None:
    assert old in VALID
    with pytest.raises(ValueError, match=message):
        charter(VALID.replace(old, new, 1))


def test_digest_follows_what_is_claimed_not_its_commentary(charter: Callable[[str], Charter]) -> None:
    def digest(text: str) -> str:
        loaded = charter(text)
        return loaded.digest(loaded.claims[0])

    reference = digest(VALID)
    assert digest(VALID.replace("aucun dépassement testé", "autre limite")) == reference
    assert digest(VALID.replace('tags = ["ci", "scenario-6"]', "tags = []")) == reference
    for old, new in [
        ('command = "echo 2"', 'command = "echo  2"'),
        ("output_regex = '^2$'", "output_regex = '2'"),
        ('command = "false"', 'command = "exit 1"'),
        ("0123456789abcdef0123456789abcdef01234567", "1123456789abcdef0123456789abcdef01234567"),
        ('scope = "entiers positifs"', 'scope = "tous les entiers"'),
    ]:
        assert digest(VALID.replace(old, new)) != reference, old
