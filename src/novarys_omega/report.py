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
_ASSET_KEYS = {"name", "title", "observed", "commit", "role", "short", *ASSET_FIELDS}
# Nombre d'actifs présentés comme priorités sur l'accueil du site : les premiers du registre, déjà classé.
PRIORITIES = 5


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


_SITE_STYLE = """:root{--bg:#fff;--fg:#14181f;--soft:#5b6472;--line:#e3e6ea;--card:#f7f8fa;--accent:#1f5eff;
--ok:#12805c;--warn:#a15c00;--bad:#c0303b}
@media (prefers-color-scheme:dark){:root{--bg:#0f1216;--fg:#e8ebef;--soft:#9aa3af;--line:#262b33;--card:#161a20;
--accent:#7aa2ff;--ok:#4cc79a;--warn:#e0a85a;--bad:#f0808a}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
nav{position:sticky;top:0;z-index:1;display:flex;gap:2px;overflow-x:auto;padding:0 12px;background:var(--bg);
border-bottom:1px solid var(--line)}
nav a,nav strong{padding:13px 10px;white-space:nowrap}
nav a{text-decoration:none;color:var(--soft);border-bottom:2px solid transparent}
nav a[aria-current]{color:var(--fg);border-color:var(--accent);font-weight:600}
main{max-width:960px;margin:0 auto;padding:20px 16px 56px}
h1{font-size:1.35rem;line-height:1.3;margin:0 0 6px;text-wrap:balance}
h2{font-size:.95rem;margin:28px 0 10px}
p{margin:0 0 12px;overflow-wrap:anywhere}
a{color:var(--accent)}
.soft{color:var(--soft);font-size:.85rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
.card b{display:block;font-size:1.3rem;line-height:1.3;font-variant-numeric:tabular-nums}
.rows{border:1px solid var(--line);border-radius:10px;overflow:hidden}
.row{display:block;padding:11px 12px;border-bottom:1px solid var(--line);text-decoration:none;color:inherit;
overflow-wrap:anywhere}
.row:last-child{border-bottom:0}
a.row:hover,a.row:focus-visible{background:var(--card)}
.row span:not(.tag){display:block;color:var(--soft);font-size:.85rem}
.tag{display:inline-block;margin-left:6px;padding:0 8px;border-radius:999px;border:1px solid;font-size:.72rem;
font-weight:600;vertical-align:middle}
.ok{color:var(--ok)}.warn{color:var(--warn)}.bad{color:var(--bad)}.off{color:var(--soft)}
.btn{display:inline-block;padding:8px 14px;border-radius:8px;background:var(--accent);color:var(--bg);
text-decoration:none;font-weight:600}
"""
NAV = {
    "index.html": "Accueil",
    "projets.html": "Projets",
    "connexions.html": "Connexions",
    "activite.html": "Activité",
    "intelligence.html": "Intelligence",
    "parametres.html": "Paramètres",
}
CONNECTION_STATES = {"active": "ok", "erreur": "bad", "à autoriser": "warn", "absente": "off"}
CONNECTORS_URL = "https://claude.ai/settings/connectors"
STEP_STATES = {"fait": "ok", "en cours": "warn", "à faire": "off"}
_PROOF_TAGS = {Status.PROVEN: "ok", Status.FAILED: "bad"}
_REPO = "https://github.com/haynbroit-alt/NOVARYS/blob/main"
Rows = list[dict[str, str]]


def asset_slug(name: str) -> str:
    """Nom de page d'un actif : minuscules, lettres et chiffres seulement."""

    return "".join(c for c in name.lower() if c.isalnum())


def _text(value: str) -> str:
    return escape(" ".join(value.split()))


def _tag(label_text: str, kind: str) -> str:
    return f'<span class="tag {kind}">{_text(label_text)}</span>'


def _row(title: str, lines: list[str], href: str = "", tag: str = "") -> str:
    inner = f"<b>{_text(title)}</b>{tag}" + "".join(f"<span>{_text(line)}</span>" for line in lines)
    return f'<a class="row" href="{escape(href)}">{inner}</a>' if href else f'<div class="row">{inner}</div>'


def _site_page(current: str, title: str, body: list[str]) -> str:
    links = "".join(
        f'<a href="{href}"{' aria-current="page"' if href == current else ""}>{name}</a>' for href, name in NAV.items()
    )
    head = (
        '<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{escape(title)} — VELYX</title>\n<style>\n{_SITE_STYLE}</style>\n</head>\n<body>\n"
        f'<nav aria-label="Navigation"><strong>VELYX</strong>{links}</nav>\n<main>\n<h1>{escape(title)}</h1>'
    )
    return "\n".join([head, *body, "</main>\n</body>\n</html>\n"])


def _board(path: Path, table: str, keys: set[str]) -> Rows:
    rows: Rows = []
    for index, row in enumerate(tomllib.loads(path.read_text(encoding="utf-8")).get(table, []), start=1):
        if set(row) != keys or not all(isinstance(v, str) and v.strip() for v in row.values()):
            wanted = ", ".join(f"« {key} »" for key in sorted(keys))
            raise ValueError(f"{table} n°{index} : il faut exactement {wanted}, non vides")
        rows.append({key: value.strip() for key, value in row.items()})
    return rows


def load_measures(path: Path) -> Rows:
    """Lit les mesures du tableau de bord public. Une mesure sans source n'est pas une mesure : elle est refusée."""

    return _board(path, "measure", {"label", "value", "source"})


def load_steps(path: Path) -> Rows:
    """Lit les étapes du cycle : un état parmi trois, une source, et un lien qui mène à la preuve de cet état."""

    steps = _board(path, "step", {"label", "state", "source", "link"})
    for step in steps:
        if step["state"] not in STEP_STATES:
            raise ValueError(f"étape « {step['label']} » : état inconnu (attendu : {', '.join(STEP_STATES)})")
        if not step["link"].startswith("https://") and step["link"] not in NAV:
            raise ValueError(f"étape « {step['label']} » : le lien doit être en https:// ou une page du site")
    return steps


def load_connections(path: Path) -> tuple[Rows, Rows]:
    """Lit les connexions aux services externes et les actions réellement exécutées. Rien n'y est supposé :
    un état « active » exige la trace d'un essai réel dans « tested »."""

    connections = _board(path, "connection", {"service", "category", "state", "access", "tested", "projects", "detail"})
    for row in connections:
        if row["state"] not in CONNECTION_STATES:
            raise ValueError(
                f"connexion « {row['service']} » : état inconnu (attendu : {', '.join(CONNECTION_STATES)})"
            )
    return connections, _board(path, "action", {"date", "service", "kind", "result"})


def _rows(items: list[str], empty: str) -> list[str]:
    return ['<div class="rows">', *(items or [_row(empty, [])]), "</div>"]


def _home(assets: Rows, measures: Rows, connections: Rows) -> list[str]:
    cards = [
        f'<div class="card"><span class="soft">{_text(m["label"])}</span><b>{_text(m["value"])}</b>'
        f'<span class="soft">{_text(m["source"])}</span></div>'
        for m in measures
    ]
    alerts = [
        _row(c["service"], [c["detail"]], "connexions.html", _tag(c["state"], CONNECTION_STATES[c["state"]]))
        for c in connections
        if c["state"] in ("erreur", "à autoriser")
    ]
    priorities = [
        _row(f"{a['name']} — {a['title']}", [f"Prochaine action : {a['next_action']}"], f"{asset_slug(a['name'])}.html")
        for a in assets[:PRIORITIES]
    ]
    return [
        '<div class="grid">',
        *cards,
        "</div>",
        "<h2>À traiter</h2>",
        *_rows(alerts, "Aucune connexion en erreur ou à autoriser."),
        "<h2>Priorités</h2>",
        *_rows(priorities, "Aucun projet au registre."),
    ]


def _connections_page(connections: Rows) -> list[str]:
    counts = " · ".join(f"{sum(1 for c in connections if c['state'] == state)} {state}" for state in CONNECTION_STATES)
    body = [
        f'<p class="soft">{_text(counts)}. Chaque état vient d\'un essai en lecture, daté. Toute écriture demande '
        "la validation du propriétaire.</p>",
        f'<p><a class="btn" href="{CONNECTORS_URL}">Connecter ou déconnecter un service</a></p>',
    ]
    for category in dict.fromkeys(c["category"] for c in connections):
        body.append(f"<h2>{_text(category)}</h2>")
        body += _rows(
            [
                _row(
                    c["service"],
                    [
                        f"Permissions : {c['access']}",
                        f"Essai : {c['tested']}",
                        f"Projets : {c['projects']}",
                        c["detail"],
                    ],
                    tag=_tag(c["state"], CONNECTION_STATES[c["state"]]),
                )
                for c in connections
                if c["category"] == category
            ],
            "",
        )
    return body


def _activity_page(steps: Rows, actions: Rows, records: list[dict[str, Any]]) -> list[str]:
    proofs = [
        _row(
            f"n°{r['seq']} · {r['claim']}",
            [f"{r['at'][:10]} · {r['actor']}"],
            tag=_tag(label(r["status"]), _PROOF_TAGS.get(r["status"], "warn")),
        )
        for r in reversed(records[-10:])
    ]
    return [
        "<h2>Cycle</h2>",
        *_rows(
            [_row(s["label"], [s["source"]], s["link"], _tag(s["state"], STEP_STATES[s["state"]])) for s in steps], ""
        ),
        "<h2>Actions exécutées sur les services externes</h2>",
        *_rows([_row(f"{a['date']} · {a['kind']}", [a["service"], a["result"]]) for a in actions], "Aucune action."),
        "<h2>Dernières preuves</h2>",
        *_rows(proofs, "Aucune preuve au registre."),
        f'<p class="soft" style="margin-top:12px"><a href="{_REPO}/registre/preuves.jsonl">Registre complet</a></p>',
    ]


def _intelligence_page(assets: Rows, charter: Charter, records: list[dict[str, Any]]) -> list[str]:
    levels = {claim.id: level_of(charter, claim, records) for claim in charter.claims}
    domains = []
    for domain in DOMAINS:
        counts = [
            (level, sum(1 for c in charter.claims if c.domain == domain and levels[c.id] == level)) for level in LEVELS
        ]
        if any(n for _, n in counts):
            domains.append(_row(domain, [" · ".join(f"{label(level)} {n}" for level, n in counts if n)]))
    tested = sum(1 for level in levels.values() if LEVELS.index(level) >= LEVELS.index(Level.TESTED))
    core = [_row(a["name"], [a["role"]], f"{asset_slug(a['name'])}.html") for a in assets if "role" in a]
    return [
        "<h2>Noyau</h2>",
        *_rows(core, "Aucun rôle attribué."),
        "<h2>Capacités</h2>",
        f'<p class="soft">{tested} fonction(s) sur {len(levels)} au niveau TESTÉ ou au-dessus. '
        f'<a href="{_REPO}/CAPACITES.md">Matrice complète</a></p>',
        *_rows(domains, "Aucune capacité revendiquée."),
    ]


def _settings_page() -> list[str]:
    edit = "https://github.com/haynbroit-alt/NOVARYS/edit/main/registre"
    return _rows(
        [
            _row("Services connectés", ["Autoriser, reconnecter ou révoquer un service."], CONNECTORS_URL),
            _row("Décisions en attente", ["Ce que seul le propriétaire peut trancher."], f"{_REPO}/DECISIONS.md"),
            _row("Projets", ["Modifier le registre des projets."], f"{edit}/actifs.toml"),
            _row("Chiffres et cycle", ["Modifier les mesures et les étapes."], f"{edit}/tableau.toml"),
            _row("Connexions", ["Modifier l'état et les permissions des connexions."], f"{edit}/connexions.toml"),
            _row("Hébergement", ["Publié à chaque fusion sur la branche principale."], f"{_REPO}/wrangler.toml"),
        ],
        "",
    )


def site_pages(
    assets: Rows,
    measures: Rows,
    steps: Rows,
    connections: tuple[Rows, Rows],
    charter: Charter,
    records: list[dict[str, Any]],
) -> dict[str, str]:
    """Centre de pilotage statique : six pages et une page par projet, tirées des registres."""

    slugs = [asset_slug(asset["name"]) for asset in assets]
    if {f"{slug}.html" for slug in slugs} & set(NAV) or "" in slugs or len(set(slugs)) != len(slugs):
        raise ValueError("deux actifs donneraient la même page du site, ou une page réservée ou sans nom")
    projects = [
        _row(
            f"{a['name']} — {a.get('short', a['title'])}",
            [a["title"], f"Prochaine action : {a['next_action']}"],
            f"{s}.html",
        )
        for a, s in zip(assets, slugs, strict=True)
    ]
    pages = {
        "index.html": _site_page("index.html", "Accueil", _home(assets, measures, connections[0])),
        "projets.html": _site_page("projets.html", "Projets", _rows(projects, "Aucun projet au registre.")),
        "connexions.html": _site_page("connexions.html", "Connexions", _connections_page(connections[0])),
        "activite.html": _site_page("activite.html", "Activité", _activity_page(steps, connections[1], records)),
        "intelligence.html": _site_page(
            "intelligence.html", "Intelligence", _intelligence_page(assets, charter, records)
        ),
        "parametres.html": _site_page("parametres.html", "Paramètres", _settings_page()),
    }
    for asset, slug in zip(assets, slugs, strict=True):
        body = [f'<p class="soft">{_text(asset["name"])} · observé le {_text(asset["observed"])}</p>']
        fields = {"Rôle dans le noyau": asset["role"]} if "role" in asset else {}
        fields |= {title: asset[key] for key, title in ASSET_FIELDS.items()}
        for title, value in fields.items():
            body += [f"<h2>{escape(title)}</h2>", f"<p>{_text(value)}</p>"]
        pages[f"{slug}.html"] = _site_page("projets.html", asset["title"], body)
    return pages
