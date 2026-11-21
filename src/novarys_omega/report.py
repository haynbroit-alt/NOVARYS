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


_SITE_STYLE = """:root{--bg:#040817;--fg:#eaf2ff;--soft:#9db4d8;--cy:#35e0ff;--gold:#ffc24a;--vio:#b06bff;--ok:#3dffa0;
--edge:rgba(80,150,255,.45);--cell:rgba(10,20,60,.7)}
*{box-sizing:border-box}
html{background:var(--bg)}
body{margin:0;min-height:100vh;color:var(--fg);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
background:radial-gradient(900px 520px at 50% 28%,#14307a 0,transparent 70%),
radial-gradient(700px 420px at 8% 0,#2a1466 0,transparent 70%),
radial-gradient(700px 420px at 92% 0,#0b3a6b 0,transparent 70%),var(--bg)}
body::before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.5;background-size:220px 220px;
background-image:radial-gradient(1px 1px at 20px 30px,#fff,transparent),
radial-gradient(1px 1px at 130px 80px,#9cf,transparent),radial-gradient(1.5px 1.5px at 80px 160px,#fff,transparent),
radial-gradient(1px 1px at 190px 120px,#c9f,transparent)}
a{color:var(--cy)}
main{position:relative;max-width:1400px;margin:0 auto;padding:20px 16px 48px}
main.doc{max-width:760px}
.doc h1{font-size:1.6rem;line-height:1.25;margin:0 0 8px;text-wrap:balance}
.doc h2{font-size:.9rem;margin:22px 0 4px;color:var(--gold);text-transform:uppercase;letter-spacing:.08em}
p{margin:0 0 12px;overflow-wrap:anywhere}
.soft{color:var(--soft);font-size:.88rem}
.panel{background:linear-gradient(160deg,rgba(20,40,110,.55),rgba(8,14,44,.78));border:1px solid var(--edge);
border-radius:18px;padding:16px;box-shadow:inset 0 0 0 1px rgba(53,224,255,.12),0 0 28px rgba(47,107,255,.35)}
.panel h2{margin:0 0 12px;font-size:1.1rem}
.top{display:grid;grid-template-columns:1fr auto 1fr;gap:12px;margin-bottom:18px}
.tag{margin:6px 0 0;font-weight:600;color:var(--cy);background:linear-gradient(90deg,var(--vio),var(--cy));
-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.tag.r{text-align:right}
.brand{text-align:center}
.brand h1{margin:0;font-size:clamp(2.2rem,6vw,3.6rem);line-height:1.1;letter-spacing:.18em;font-weight:800;
text-shadow:0 0 24px rgba(120,180,255,.85)}
.brand p{margin:4px 0 0;color:var(--gold);font-size:1.05rem}
.stage{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr) minmax(0,1.15fr);gap:18px;align-items:start}
.side{display:grid;gap:18px}
.tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.tile{display:flex;flex-direction:column;align-items:center;gap:4px;padding:12px 4px;min-height:98px;border-radius:12px;
text-align:center;text-decoration:none;color:var(--fg);background:var(--cell);border:1px solid var(--edge);
overflow-wrap:anywhere;transition:box-shadow .2s,border-color .2s}
.tile:hover,.tile:focus-visible,.pillar:hover,.pillar:focus-visible,.step:hover,.step:focus-visible{
border-color:var(--cy);box-shadow:0 0 18px rgba(53,224,255,.55);outline:0}
.ico{width:34px;height:34px;border-radius:9px;display:grid;place-items:center;font-weight:800;color:#fff;
background:linear-gradient(135deg,hsl(var(--h) 90% 60%),hsl(calc(var(--h) + 50) 90% 42%));
box-shadow:0 0 12px hsl(var(--h) 90% 60% / .7)}
.tile b{font-size:.9rem;line-height:1.2}
.tile span{font-size:.74rem;color:var(--soft);line-height:1.2}
.core{display:grid;justify-items:center;gap:0;padding-top:8px}
.orb{position:relative;width:min(88%,340px);aspect-ratio:1;border-radius:50%;display:grid;place-content:center;
justify-items:center;background:radial-gradient(circle at 35% 30%,#7fd4ff 0,#1b63e0 35%,#0a1e6b 65%,#050a2a 100%);
box-shadow:0 0 60px rgba(60,140,255,.8),inset 0 0 50px rgba(255,255,255,.25)}
.orb svg{width:46%;filter:drop-shadow(0 0 14px rgba(160,220,255,.9))}
.orb strong{font-size:clamp(1.3rem,4vw,1.9rem);letter-spacing:.2em;text-shadow:0 0 14px #9cf}
.ring{position:absolute;inset:-9%;border-radius:50%;border:2px solid rgba(255,194,74,.75);
animation:spin 16s linear infinite}
.ring.b{inset:-4%;border-color:rgba(176,107,255,.75);animation-duration:24s;animation-direction:reverse}
.ring::after{content:"";position:absolute;top:-5px;left:50%;width:9px;height:9px;border-radius:50%;background:#fff;
box-shadow:0 0 12px 3px var(--gold)}
@keyframes spin{from{transform:rotateX(74deg) rotateZ(0)}to{transform:rotateX(74deg) rotateZ(360deg)}}
.city{width:min(96%,380px);margin-top:-26px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(118px,1fr));gap:10px}
.kpi{padding:12px;border-radius:12px;background:var(--cell);border:1px solid var(--edge)}
.kpi b{display:block;font-size:1.45rem;line-height:1.2;font-variant-numeric:tabular-nums;color:var(--ok)}
.kpi b.unknown{color:var(--gold);font-size:1.05rem;line-height:1.75}
.kpi small{display:block;color:var(--soft);font-size:.74rem;line-height:1.35;margin-top:4px}
.prio{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.prio a{display:flex;gap:10px;align-items:baseline;text-decoration:none;color:var(--fg)}
.prio a::before{content:"";flex:none;width:14px;height:14px;border-radius:50%;border:2px solid var(--soft);
transform:translateY(2px)}
.prio b{color:var(--cy)}
.pillars{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px;margin-top:18px}
.pillar{display:block;text-align:center;text-decoration:none;color:var(--fg)}
.pillar em{display:block;font-style:normal;color:var(--gold);font-weight:600;margin-bottom:6px}
.pillar b{display:block;font-size:1.05rem}
.pillar span{color:var(--soft);font-size:.82rem}
.cycle{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
.step{flex:1 1 150px;padding:10px 12px;border-radius:999px;border:1px solid var(--edge);background:var(--cell);
text-decoration:none;color:var(--fg);display:grid;grid-template-columns:auto 1fr;column-gap:10px;align-items:center}
.step i{grid-row:span 2;width:26px;height:26px;border-radius:50%;display:grid;place-items:center;font-style:normal;
font-weight:800;border:2px solid var(--soft);color:var(--soft)}
.step.fait i{border-color:var(--ok);color:var(--ok);box-shadow:0 0 10px rgba(61,255,160,.6)}
.step.encours i{border-color:var(--gold);color:var(--gold)}
.step small{color:var(--soft);font-size:.72rem;line-height:1.3}
.motto{text-align:center;margin:26px 0 6px;font-size:1.1rem}
.motto b{color:var(--gold);font-weight:600}
.foot{text-align:center}
@media (max-width:1000px){.stage{grid-template-columns:1fr}.core{order:-1}
.top{grid-template-columns:1fr;text-align:center}
.tag.r{text-align:center}.brand{order:-1}.pillars{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:430px){.tiles{grid-template-columns:repeat(3,minmax(0,1fr))}.pillars{grid-template-columns:1fr}}
@media (prefers-reduced-motion:reduce){.ring{animation:none;transform:rotateX(74deg)}.tile{transition:none}}
"""
_LOGO = (
    '<svg viewBox="0 0 100 80" role="img" aria-label="Emblème VELYX"><defs><linearGradient id="v" x1="0" y1="0" '
    'x2="1" y2="1"><stop offset="0" stop-color="#bfe9ff"/><stop offset="1" stop-color="#3f8cff"/></linearGradient>'
    '</defs><path fill="url(#v)" d="M4 4h24l22 44 22-44h24L50 78z"/></svg>'
)
_CITY = (
    '<svg class="city" viewBox="0 0 380 150" aria-hidden="true"><defs><linearGradient id="c" x1="0" y1="0" x2="0" '
    'y2="1"><stop offset="0" stop-color="#ffd98a"/><stop offset="1" stop-color="#3a59c9"/></linearGradient></defs>'
    '<path d="M40 120a150 110 0 0 1 300 0" fill="rgba(60,120,255,.12)" stroke="rgba(120,190,255,.7)"/>'
    '<g fill="url(#c)"><rect x="92" y="78" width="14" height="42"/><rect x="110" y="62" width="16" height="58"/>'
    '<rect x="130" y="84" width="12" height="36"/><rect x="146" y="50" width="18" height="70"/>'
    '<rect x="168" y="70" width="14" height="50"/><rect x="186" y="34" width="16" height="86"/>'
    '<rect x="206" y="58" width="16" height="62"/><rect x="226" y="76" width="12" height="44"/>'
    '<rect x="242" y="64" width="16" height="56"/><rect x="262" y="88" width="14" height="32"/></g>'
    '<ellipse cx="190" cy="124" rx="170" ry="14" fill="none" stroke="#35e0ff" stroke-width="2"/>'
    '<ellipse cx="190" cy="136" rx="130" ry="10" fill="none" stroke="rgba(176,107,255,.8)" stroke-width="2"/></svg>'
)
STEP_STATES = {"fait": ("fait", "✓"), "en cours": ("encours", "…"), "à faire": ("afaire", "")}
_REPO = "https://github.com/haynbroit-alt/NOVARYS/blob/main"


def asset_slug(name: str) -> str:
    """Nom de page d'un actif : minuscules, lettres et chiffres seulement."""

    return "".join(c for c in name.lower() if c.isalnum())


def _site_page(title: str, body: list[str], kind: str = "doc") -> str:
    head = (
        '<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{escape(title)}</title>\n<style>\n{_SITE_STYLE}</style>\n</head>\n<body>\n<main class="{kind}">'
    )
    return "\n".join([head, *body, "</main>\n</body>\n</html>\n"])


def _board(path: Path, table: str, keys: set[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, row in enumerate(tomllib.loads(path.read_text(encoding="utf-8")).get(table, []), start=1):
        if set(row) != keys or not all(isinstance(v, str) and v.strip() for v in row.values()):
            wanted = ", ".join(f"« {key} »" for key in sorted(keys))
            raise ValueError(f"{table} n°{index} : il faut exactement {wanted}, non vides")
        rows.append({key: value.strip() for key, value in row.items()})
    return rows


def load_measures(path: Path) -> list[dict[str, str]]:
    """Lit les mesures du tableau de bord public. Une mesure sans source n'est pas une mesure : elle est refusée."""

    return _board(path, "measure", {"label", "value", "source"})


def load_steps(path: Path) -> list[dict[str, str]]:
    """Lit les étapes du cycle : un état parmi trois, une source, et un lien qui mène à la preuve de cet état."""

    steps = _board(path, "step", {"label", "state", "source", "link"})
    for step in steps:
        if step["state"] not in STEP_STATES:
            raise ValueError(f"étape « {step['label']} » : état inconnu (attendu : {', '.join(STEP_STATES)})")
        if not step["link"].startswith(("https://", "#")):
            raise ValueError(f"étape « {step['label']} » : le lien doit commencer par https:// ou par #")
    return steps


def _text(value: str) -> str:
    return escape(" ".join(value.split()))


def _home(assets: list[dict[str, str]], measures: list[dict[str, str]], steps: list[dict[str, str]]) -> list[str]:
    """Accueil : les projets à gauche, le cœur au centre, l'économie et les priorités à droite, piliers et cycle."""

    def link(asset: dict[str, str]) -> str:
        return f"{asset_slug(asset['name'])}.html"

    tiles = [
        f'<a class="tile" href="{link(a)}" style="--h:{n * 47 % 360}"><span class="ico">{_text(a["name"][:1].upper())}'
        f"</span><b>{_text(a['name'])}</b><span>{_text(a.get('short', a['title']))}</span></a>"
        for n, a in enumerate(assets)
    ]
    kpis = [
        f'<div class="kpi"><span>{_text(m["label"])}</span><b{' class="unknown"' if m["value"] == "INCONNU" else ""}>'
        f"{_text(m['value'])}</b><small>{_text(m['source'])}</small></div>"
        for m in measures
    ]
    priorities = [
        f'<li><a href="{link(a)}"><span><b>{_text(a["name"])}</b> — {_text(a["title"])}</span></a></li>'
        for a in assets[:PRIORITIES]
    ]
    pillars = [
        f'<a class="panel pillar" href="{link(a)}"><em>{_text(a["role"].split(":")[0])}</em><b>{_text(a["name"])}</b>'
        f"<span>{_text(a['role'].split(':', 1)[-1].split('.')[0])}</span></a>"
        for a in assets
        if "role" in a
    ]
    pillars += [
        '<a class="panel pillar" href="#economie"><em>Des projets qui réussissent</em><b>Des idées aux revenus</b>'
        "<span>Les chiffres réels, avec leur source</span></a>",
        f'<a class="panel pillar" href="{_REPO}/DECISIONS.md"><em>Une autonomie progressive</em><b>Décisions</b>'
        "<span>Ce qui attend encore le propriétaire</span></a>",
    ]
    cycle = [
        f'<a class="step {STEP_STATES[s["state"]][0]}" href="{escape(s["link"])}"><i>{STEP_STATES[s["state"]][1]}</i>'
        f"<b>{_text(s['label'])}</b><small>{_text(s['state'])} · {_text(s['source'])}</small></a>"
        for s in steps
    ]
    return [
        '<header class="top"><p class="tag">Créer • Produire • Vendre • Innover</p><div class="brand"><h1>VELYX</h1>'
        f"<p>Un écosystème. {len(assets)} projets. Une seule vision.</p></div>"
        '<p class="tag r">Construire aujourd\'hui la liberté de demain</p></header>',
        '<div class="stage">',
        f'<section class="panel" id="projets"><h2>Nos {len(assets)} projets</h2><div class="tiles">',
        *tiles,
        "</div></section>",
        f'<div class="core"><div class="orb"><span class="ring"></span><span class="ring b"></span>{_LOGO}'
        f"<strong>VELYX</strong></div>{_CITY}</div>",
        '<div class="side"><section class="panel" id="economie"><h2>Tableau de bord : chiffres réels</h2>'
        '<div class="kpis">',
        *kpis,
        '</div><p class="soft" style="margin:10px 0 0">Un chiffre sans mesure s\'écrit INCONNU.</p></section>',
        '<section class="panel" id="priorites"><h2>Priorités immédiates</h2><ol class="prio">',
        *priorities,
        "</ol></section></div>",
        "</div>",
        '<nav class="pillars" aria-label="Piliers">',
        *pillars,
        "</nav>",
        '<nav class="cycle" aria-label="Cycle opérationnel">',
        *cycle,
        "</nav>",
        '<p class="motto">VELYX : plus qu\'un portail, <b>un moteur de réussite</b> à mériter.</p>',
        '<p class="soft foot">Page générée depuis le registre public. Aucun chiffre fictif.</p>',
    ]


def site_pages(
    assets: list[dict[str, str]], measures: list[dict[str, str]], steps: list[dict[str, str]]
) -> dict[str, str]:
    """Portail statique : une page d'accueil et une page par actif, tirées du même registre que ACTIFS.md."""

    slugs = [asset_slug(asset["name"]) for asset in assets]
    if "index" in slugs or "" in slugs or len(set(slugs)) != len(slugs):
        raise ValueError("deux actifs donneraient la même page du site, ou une page sans nom")
    note = '<p class="soft">Page générée depuis le registre public des actifs. Aucune promesse de résultat.</p>'
    pages: dict[str, str] = {}
    for asset, slug in zip(assets, slugs, strict=True):
        body = ['<p><a href="index.html">← Tous les projets</a></p>', f"<h1>{_text(asset['title'])}</h1>"]
        body.append(f'<p class="soft">{_text(asset["name"])} · observé le {_text(asset["observed"])}</p>')
        if "role" in asset:
            body += ["<h2>Rôle dans le noyau</h2>", f"<p>{_text(asset['role'])}</p>"]
        for key, title in ASSET_FIELDS.items():
            body += [f"<h2>{escape(title)}</h2>", f"<p>{_text(asset[key])}</p>"]
        pages[f"{slug}.html"] = _site_page(f"{asset['name']} — VELYX", [*body, note])
    pages["index.html"] = _site_page("VELYX — un écosystème, une seule vision", _home(assets, measures, steps), "home")
    return pages
