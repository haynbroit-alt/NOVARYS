"""Matrice des capacités et registre d'actifs : deux fichiers Markdown générés, jamais écrits à la main."""

from __future__ import annotations

import tomllib
from html import escape
from pathlib import Path
from typing import Any

from novarys_omega.model import DOMAINS, LEVELS, Charter, Claim, Level, Status, label

# Les sept scénarios de validation du cahier des charges (section 14). Une capacité s'y rattache par l'étiquette
# ``scenario-N``.
SCENARIOS = (
    "Recherche multi-source vérifiée",
    "Inspection, correction et livraison d'un projet",
    "Invention comparée et falsifiable",
    "Création d'une offre réellement commercialisable",
    "Reprise fiable d'une mission interrompue",
    "Blocage d'une action non autorisée et protection des secrets",
    "Reproduction indépendante d'une capacité",
)
# Les dix rubriques exigées pour chaque actif (cahier des charges, section 12), dans l'ordre d'affichage.
ASSET_FIELDS = {
    "location": "Localisation",
    "access": "Accès",
    "state": "État réel",
    "demonstrated": "Fonctions démontrées",
    "dependencies": "Dépendances",
    "costs": "Coûts",
    "reuse": "Réutilisation",
    "proofs": "Preuves",
    "blockers": "Blocages",
    "next_action": "Prochaine action rentable",
}
_ASSET_KEYS = {"name", "title", "observed", "commit", *ASSET_FIELDS}


def proofs_for(charter: Charter, claim: Claim, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Preuves valant pour la capacité telle qu'elle est revendiquée aujourd'hui (même empreinte)."""

    digest = charter.digest(claim)
    return [r for r in records if r.get("claim") == claim.id and r.get("claim_sha256") == digest]


def status_of(charter: Charter, claim: Claim, records: list[dict[str, Any]]) -> Status:
    mine = proofs_for(charter, claim, records)
    return Status(mine[-1]["status"]) if mine else Status.UNKNOWN


def level_of(charter: Charter, claim: Claim, records: list[dict[str, Any]]) -> Level:
    """Niveau atteint, déduit des preuves et jamais déclaré.

    ABSENT : fonction non construite. DISPONIBLE : une commande existe, sans preuve valide à ce jour.
    CONNECTÉ : elle s'exécute de bout en bout (ÉTAYÉ). TESTÉ : PROUVÉ sur données de test.
    OPÉRATIONNEL : PROUVÉ sur données et environnement réels.
    VALIDÉ n'est jamais attribué par l'outil : il faudrait une preuve reproduite par un second acteur dont
    l'identité se vérifie, et le nom d'acteur consigné n'est qu'une déclaration.
    """

    if claim.check is None:
        return Level.ABSENT
    mine = proofs_for(charter, claim, records)
    last = mine[-1]["status"] if mine else None
    if last == Status.SUPPORTED:
        return Level.CONNECTED
    if last != Status.PROVEN:
        return Level.AVAILABLE
    return Level.TESTED if claim.kind == "test" else Level.OPERATIONAL


def _cell(text: str) -> str:
    return " ".join(text.split()).replace("|", "\\|")


def _evidence(charter: Charter, claim: Claim, records: list[dict[str, Any]]) -> str:
    if claim.check is None:
        return "non construite"
    mine = proofs_for(charter, claim, records)
    if not mine:
        stale = any(r.get("claim") == claim.id for r in records)
        return "preuve périmée : la revendication a changé depuis" if stale else "jamais exécutée"
    last = mine[-1]
    attack = last.get("falsification")
    outcome = "non tentée" if attack is None else ("résistée" if attack["ok"] else "RÉUSSIE")
    subject = last["subject"]
    code = f"{'ce dépôt' if subject['name'] == '.' else subject['name']}@{subject['commit'][:8]}"
    return (
        f"{last['at'][:10]} · {last['actor']} · {code} · {len(last['runs'])} exécution(s) · attaque {outcome} "
        f"· n°{last['seq']}"
    )


def capabilities_markdown(charter: Charter, records: list[dict[str, Any]]) -> str:
    rank = LEVELS.index
    levels = {claim.id: level_of(charter, claim, records) for claim in charter.claims}
    untested = [c for c in charter.claims if rank(levels[c.id]) < rank(Level.TESTED)]
    undemonstrated = [
        domain
        for domain in DOMAINS
        if not any(c.domain == domain and rank(levels[c.id]) >= rank(Level.OPERATIONAL) for c in charter.claims)
    ]
    lines = [
        "# Capacités de NOVARYS Ω : ce qui est prouvé",
        "",
        "> Fichier généré par `omega render` à partir de `registre/capacites.toml` (ce qui est revendiqué) et de",
        "> `registre/preuves.jsonl` (ce qui a été exécuté). Ne pas le modifier à la main.",
        "",
    ]
    if untested or undemonstrated:
        lines += [
            "**Verdict : NOVARYS n'est pas opérationnel.** "
            f"{len(untested)} fonction(s) sur {len(charter.claims)} sont sous le niveau TESTÉ ; "
            f"{len(undemonstrated)} domaine(s) sur {len(DOMAINS)} n'ont aucune fonction démontrée sur données réelles"
            + (f" ({', '.join(undemonstrated)})." if undemonstrated else "."),
        ]
    else:
        lines += [
            "**Verdict : NOVARYS est opérationnel.** Toutes les fonctions sont au moins TESTÉES et chaque domaine "
            "a une fonction démontrée sur données réelles.",
        ]
    lines += ["", "Règle du verdict : aucune fonction sous TESTÉ, et dans chaque domaine au moins une fonction"]
    lines += ["OPÉRATIONNELLE. Rentable est une autre question : elle se lit dans les encaissements, pas ici.", ""]
    for subject in charter.subjects.values():
        lines.append(f"Dépôt évalué « {subject.name} » : `{subject.repo}` au commit `{subject.commit[:12]}`.")
    lines += ["", "## Vue d'ensemble", "", "| Domaine | " + " | ".join(label(level) for level in LEVELS) + " |"]
    lines.append("|---|" + "---:|" * len(LEVELS))
    for domain in DOMAINS:
        counts = [sum(1 for c in charter.claims if c.domain == domain and levels[c.id] == level) for level in LEVELS]
        lines.append(f"| {domain} | " + " | ".join(str(n) if n else "·" for n in counts) + " |")

    lines += ["", "## Scénarios de validation (cahier des charges, section 14)", ""]
    lines += ["| N° | Scénario | Fonctions rattachées | Niveau le plus bas |", "|---:|---|---|---|"]
    for number, title in enumerate(SCENARIOS, start=1):
        tagged = [c for c in charter.claims if f"scenario-{number}" in c.tags]
        lowest = min((levels[c.id] for c in tagged), key=rank, default=Level.ABSENT)
        names = ", ".join(f"`{c.id}`" for c in tagged) or "aucune"
        lines.append(f"| {number} | {title} | {names} | {label(lowest)} |")

    for domain in DOMAINS:
        claims = [c for c in charter.claims if c.domain == domain]
        if not claims:
            continue
        lines += [
            "",
            f"## {domain}",
            "",
            "| Fonction | Statut | Niveau | Dernière preuve | Limites |",
            "|---|---|---|---|---|",
        ]
        for claim in claims:
            status = "—" if claim.check is None else label(status_of(charter, claim, records))
            lines.append(
                f"| {_cell(claim.capability)} (`{claim.id}`) | {status} | {label(levels[claim.id])} "
                f"| {_evidence(charter, claim, records)} | {_cell(claim.limits) or '—'} |"
            )
    lines += [
        "",
        "## Lecture",
        "",
        "- **Statuts** (calculés à l'exécution) : PROUVÉ — au moins deux exécutions concordantes, ligne de bilan vue,",
        "  périmètre écrit, code validé dans Git, attaque tentée et résistée ; ÉTAYÉ — résultat correct mais preuve",
        "  incomplète ; INCONNU — rien d'exécuté, ou sortie retenue ; CONFLIT — exécutions contradictoires ; ÉCHEC —",
        "  test échoué ou attaque réussie.",
        "- **Ce que PROUVÉ ne dit pas** : que la commande choisie démontre bien la capacité. L'outil vérifie un",
        "  résultat attendu ; le choix de la commande et de l'attaque se juge en relisant `registre/capacites.toml`.",
        "- **Niveaux** (déduits des preuves) : ABSENT — non construit ; DISPONIBLE — commande déclarée sans preuve",
        "  valide ; CONNECTÉ — ÉTAYÉ ; TESTÉ — PROUVÉ sur données de test ; OPÉRATIONNEL — PROUVÉ sur données",
        "  réelles ; VALIDÉ — jamais attribué aujourd'hui : il faudrait un second acteur dont l'identité se vérifie.",
        "- Le numéro en fin de preuve renvoie à la ligne du registre, qui contient la commande et sa sortie brute.",
        "",
    ]
    return "\n".join(lines)


def load_assets(path: Path) -> list[dict[str, str]]:
    """Lit le registre d'actifs. Chaque rubrique est obligatoire : ce qu'on ignore s'écrit « INCONNU »."""

    data = tomllib.loads(path.read_text(encoding="utf-8"))
    assets: list[dict[str, str]] = []
    for index, table in enumerate(data.get("asset", []), start=1):
        where = f"actif {table.get('name') or f'n°{index}'}"
        unknown = sorted(set(table) - _ASSET_KEYS)
        if unknown:
            raise ValueError(f"{where} : clés inconnues {unknown}")
        for key in ("name", "title", "observed", *ASSET_FIELDS):
            if not isinstance(table.get(key), str) or not table[key].strip():
                raise ValueError(f"{where} : rubrique « {key} » manquante (écrire INCONNU si elle n'est pas vérifiée)")
        if table["name"] in {asset["name"] for asset in assets}:
            raise ValueError(f"{where} : nom en double")
        assets.append({key: str(value).strip() for key, value in table.items()})
    return assets


def assets_markdown(assets: list[dict[str, str]]) -> str:
    lines = [
        "# Actifs existants : état réel et prochaine action rentable",
        "",
        "> Fichier généré par `omega render` à partir de `registre/actifs.toml`. Ne pas le modifier à la main.",
        "> Ce registre est public : il ne décrit que des dépôts publics, sans donnée personnelle.",
        "",
        "| Actif | État réel | Blocages | Prochaine action rentable |",
        "|---|---|---|---|",
    ]
    for asset in assets:
        lines.append(
            f"| **{_cell(asset['name'])}** — {_cell(asset['title'])} | {_cell(asset['state'])} "
            f"| {_cell(asset['blockers'])} | {_cell(asset['next_action'])} |"
        )
    for asset in assets:
        observed = f"Observé le {asset['observed']}" + (
            f", commit `{asset['commit'][:12]}`" if "commit" in asset else ""
        )
        lines += ["", f"## {asset['name']} — {asset['title']}", "", f"{observed}.", ""]
        lines += [f"- **{title}** : {' '.join(asset[key].split())}" for key, title in ASSET_FIELDS.items()]
    lines.append("")
    return "\n".join(lines)


_SITE_STYLE = """:root{--bg:#f6f7f5;--fg:#17263a;--soft:#4a5868;--line:#c9d0d3;--card:#fff;--accent:#0b6b5d}
@media (prefers-color-scheme:dark){:root{--bg:#10161e;--fg:#e6ebef;--soft:#a9b4be;--line:#2c3846;--card:#161e28;
--accent:#5fd0bd}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:720px;margin:0 auto;padding:32px 16px 64px}
h1{font-size:1.6rem;line-height:1.25;margin:0 0 8px;text-wrap:balance}
h2{font-size:1rem;margin:24px 0 4px;color:var(--soft);text-transform:uppercase;letter-spacing:.06em}
p{margin:0 0 12px;overflow-wrap:anywhere}
a{color:var(--accent)}
.soft{color:var(--soft);font-size:.9rem}
.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:12px 0;
text-decoration:none;color:inherit}
.card strong{display:block;font-size:1.05rem;color:var(--accent)}
"""


def asset_slug(name: str) -> str:
    """Nom de page d'un actif : minuscules, lettres et chiffres seulement."""

    return "".join(c for c in name.lower() if c.isalnum())


def _site_page(title: str, body: list[str]) -> str:
    head = (
        '<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{escape(title)}</title>\n<style>\n{_SITE_STYLE}</style>\n</head>\n<body>\n<main>"
    )
    return "\n".join([head, *body, "</main>\n</body>\n</html>\n"])


def site_pages(assets: list[dict[str, str]]) -> dict[str, str]:
    """Portail statique : une page d'accueil et une page par actif, tirées du même registre que ACTIFS.md."""

    def text(value: str) -> str:
        return escape(" ".join(value.split()))

    slugs = [asset_slug(asset["name"]) for asset in assets]
    if "index" in slugs or "" in slugs or len(set(slugs)) != len(slugs):
        raise ValueError("deux actifs donneraient la même page du site, ou une page sans nom")
    note = '<p class="soft">Page générée depuis le registre public des actifs. Aucune promesse de résultat.</p>'
    index = [
        "<h1>VELYX</h1>",
        f"<p>{len(assets)} projets, un seul registre. Chaque projet a sa page : état réel, preuves, blocages, "
        "prochaine action.</p>",
        '<p class="soft">Classés du plus proche d\'un encaissement au plus éloigné.</p>',
    ]
    pages: dict[str, str] = {}
    for asset, slug in zip(assets, slugs, strict=True):
        index.append(
            f'<a class="card" href="{slug}.html"><strong>{text(asset["name"])}</strong>{text(asset["title"])}'
            f'<br><span class="soft">Prochaine action : {text(asset["next_action"])}</span></a>'
        )
        body = ['<p><a href="index.html">← Tous les projets</a></p>', f"<h1>{text(asset['title'])}</h1>"]
        body.append(f'<p class="soft">{text(asset["name"])} · observé le {text(asset["observed"])}</p>')
        for key, title in ASSET_FIELDS.items():
            body += [f"<h2>{escape(title)}</h2>", f"<p>{text(asset[key])}</p>"]
        pages[f"{slug}.html"] = _site_page(f"{asset['name']} — VELYX", [*body, note])
    pages["index.html"] = _site_page("VELYX — les projets", [*index, note])
    return pages
