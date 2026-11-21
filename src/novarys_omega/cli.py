"""Ligne de commande ``omega``.

omega run [--only ID] [--tag T]      exécuter les capacités, consigner les preuves, régénérer la matrice
omega verify [--only ID] [--tag T]   réexécuter et comparer au registre, sans rien écrire
omega check [--base FICHIER]         registre intact, cohérent, prolongeant la base, fichiers générés à jour
omega render                         régénérer CAPACITES.md, ACTIFS.md et site/

Codes de sortie : 0 conforme ; 1 échec constaté (preuve en échec, régression, registre altéré) ; 2 entrée
inutilisable (référentiel invalide, dépôt visé pas dans l'état épinglé, fichier illisible).
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from novarys_omega import registry
from novarys_omega.model import Charter, Claim, Status, label, load_charter
from novarys_omega.report import assets_markdown, capabilities_markdown, load_assets, site_pages, status_of
from novarys_omega.runner import SubjectError, inconsistencies, prove, subject_state


def _charter(root: Path) -> Charter:
    return load_charter(root / "registre" / "capacites.toml")


def _proofs(root: Path) -> Path:
    return root / "registre" / "preuves.jsonl"


def _generated(root: Path, charter: Charter) -> dict[Path, str]:
    assets = load_assets(root / "registre" / "actifs.toml")
    return {
        root / "CAPACITES.md": capabilities_markdown(charter, registry.read(_proofs(root))),
        root / "ACTIFS.md": assets_markdown(assets),
        **{root / "site" / name: page for name, page in site_pages(assets).items()},
    }


def _selected(charter: Charter, args: argparse.Namespace) -> list[Claim]:
    unknown = sorted(set(args.only) - {claim.id for claim in charter.claims})
    if unknown:
        raise ValueError(f"capacités inconnues : {', '.join(unknown)}")
    return [
        claim
        for claim in charter.claims
        if claim.check is not None
        and (not args.only or claim.id in args.only)
        and (args.tag is None or args.tag in claim.tags)
    ]


def _paths(root: Path, charter: Charter, args: argparse.Namespace) -> dict[str, Path]:
    """Où se trouve chaque dépôt évalué : option ``--subject``, sinon variable d'environnement, sinon référentiel."""

    given = dict(item.split("=", 1) for item in args.subject if "=" in item)
    if len(given) != len(args.subject) or set(given) - set(charter.subjects):
        raise ValueError("--subject attend NOM=CHEMIN, avec un nom déclaré dans le référentiel")
    paths = {}
    for name, subject in charter.subjects.items():
        env_name = f"OMEGA_SUBJECT_{name.upper().replace('-', '_')}"
        paths[name] = (root / (given.get(name) or os.environ.get(env_name) or subject.path)).resolve()
    return paths


def _prepared(args: argparse.Namespace) -> tuple[Path, Charter, dict[str, Path], list[Claim]]:
    """Référentiel chargé et dépôts visés contrôlés AVANT toute exécution : pas de série à moitié consignée."""

    root = args.root.resolve()
    charter = _charter(root)
    paths = _paths(root, charter, args)
    claims = _selected(charter, args)
    for claim in claims:
        subject_state(charter, claim, root, paths)
    return root, charter, paths, claims


def _run(args: argparse.Namespace) -> int:
    root, charter, paths, claims = _prepared(args)
    worst = 0
    try:
        for claim in claims:
            proof = prove(charter, claim, root=root, paths=paths, actor=args.actor, now=datetime.now(UTC))
            record = registry.append(_proofs(root), proof)
            print(f"{label(record['status']):<8} {claim.id} (preuve n°{record['seq']})")
            if record["status"] in (Status.FAILED, Status.CONFLICT, Status.UNKNOWN):
                worst = 1
    finally:
        _render(args)  # même interrompue, une série laisse la matrice à jour de ce qui a été consigné
    return worst


def _verify(args: argparse.Namespace) -> int:
    root, charter, paths, claims = _prepared(args)
    records = registry.read(_proofs(root))
    regressions = 0
    for claim in claims:
        recorded = status_of(charter, claim, records)
        current = prove(charter, claim, root=root, paths=paths, actor=args.actor, now=datetime.now(UTC))["status"]
        lost = recorded == Status.PROVEN and current != Status.PROVEN
        regressions += lost
        verdict = "RÉGRESSION" if lost else "conforme" if current == recorded else "différent"
        print(f"{verdict:<10} {claim.id} : registre {label(recorded)}, maintenant {label(current)}")
    return 1 if regressions else 0


def _check(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    charter = _charter(root)
    records = registry.read(_proofs(root))
    errors = registry.chain_errors(records)
    errors += [f"preuve n°{n} : {problem}" for n, r in enumerate(records, start=1) for problem in inconsistencies(r)]
    if args.base is not None and not args.base.is_file():  # un chemin erroné ne doit pas désactiver le contrôle
        raise ValueError(f"--base : fichier introuvable ({args.base})")
    if args.base is not None and not registry.extends(registry.read(args.base), records):
        errors.append("le registre ne prolonge pas celui de la base : des preuves ont été retirées ou réécrites")
    if not errors:  # inutile de comparer des fichiers générés à un registre déjà refusé
        for path, expected in _generated(root, charter).items():
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                errors.append(f"{path.name} n'est pas à jour : lancer `omega render`")
    for error in errors:
        print(f"ÉCHEC : {error}")
    if not errors:
        print(f"OK : {len(records)} preuve(s) chaînée(s), {len(charter.claims)} capacité(s), fichiers générés à jour")
    return 1 if errors else 0


def _render(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    for path, text in _generated(root, _charter(root)).items():
        path.parent.mkdir(exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="omega", description="NOVARYS Ω — prouver ce qui est revendiqué.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="racine du dépôt (contient registre/)")
    actions = parser.add_subparsers(dest="action", required=True)
    for name, text in (
        ("run", "exécuter les capacités et consigner les preuves"),
        ("verify", "réexécuter et comparer au registre, sans rien écrire"),
    ):
        action = actions.add_parser(name, help=text)
        action.add_argument("--only", action="append", default=[], metavar="ID", help="une capacité (répétable)")
        action.add_argument("--tag", help="seulement les capacités portant cette étiquette")
        action.add_argument("--actor", default=os.environ.get("OMEGA_ACTOR", "local"), help="qui exécute (déclaratif)")
        action.add_argument("--subject", action="append", default=[], metavar="NOM=CHEMIN", help="dépôt évalué")
    check = actions.add_parser("check", help="registre intact, cohérent, et fichiers générés à jour")
    check.add_argument(
        "--base", type=Path, help="registre de la branche de base, que le registre courant doit prolonger"
    )
    actions.add_parser("render", help="régénérer CAPACITES.md, ACTIFS.md et site/")
    args = parser.parse_args(argv)
    try:
        return {"run": _run, "verify": _verify, "check": _check, "render": _render}[args.action](args)
    except (ValueError, SubjectError, OSError) as exc:
        print(f"omega : {exc}", file=sys.stderr)
        return 2
    except (KeyError, TypeError, AttributeError) as exc:  # registre ou fichier de structure inattendue
        print(f"omega : données de structure invalide ({exc!r})", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
