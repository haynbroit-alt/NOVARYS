"""Sonde : quels outils le moteur expose-t-il aux agents (MCP) ? Aucun ne doit approuver ni encaisser.

Usage : python outils_mcp.py lister | attaquer   (SOVEREIGN_HOME doit désigner un dossier jetable).
``lister`` refuse tout outil dont le nom évoque une approbation ou un encaissement. ``attaquer`` tente, par les
outils réellement exposés, de se déclarer un encaissement pour s'ouvrir un budget : l'enveloppe doit rester à 0
et la dépense demandée ensuite doit être refusée.
"""

import asyncio
import logging
import os
import re
import sys

from mcp import Client

from sovereign.app import Sovereign
from sovereign.interfaces.mcp_server import build_mcp

FORBIDDEN = re.compile(r"approve|reject|decide|review|confirm|revenue|collect|encaiss", re.IGNORECASE)
CSV = "date,amount,reference\n2026-11-01,100000,attaque-1\n"
FINANCE = {"skill": "finance-budget"}


async def attack(client: Client, app: Sovereign) -> list[tuple[str, bool]]:
    """Chaque voie par laquelle un agent pourrait s'ouvrir un budget. Renvoie (voie, a-t-elle été refusée)."""

    async def call(tool: str, arguments: dict[str, object]) -> bool:
        return bool((await client.call_tool(tool, arguments)).is_error)

    tried = [
        ("import CSV « collections »", await call("import_csv", {"kind": "collections", "csv_text": CSV})),
        ("import CSV « encaissements »", await call("import_csv", {"kind": "encaissements", "csv_text": CSV})),
        (
            "compétence finance : déclarer un encaissement",
            await call("skill_run", {**FINANCE, "action": "record_revenue", "input": {"amount": "100000"}}),
        ),
    ]
    # Émettre une facture est permis (une créance n'ouvre aucun budget) ; se la déclarer encaissée ne l'est pas.
    await call("skill_run", {**FINANCE, "action": "issue_invoice", "input": {"client": "Fictif", "amount": "100000"}})
    for invoice in app.kernel.store.list("invoice"):
        collect = {**FINANCE, "action": "collect_invoice", "input": {"invoice_id": invoice["id"]}}
        tried.append(("compétence finance : encaisser sa propre facture", await call("skill_run", collect)))
    return tried


async def main(mode: str) -> int:
    logging.disable(logging.CRITICAL)  # les refus attendus ne doivent pas noyer le bilan
    app = Sovereign.open(os.environ["SOVEREIGN_HOME"])
    try:
        async with Client(build_mcp(app)) as client:
            names = sorted(tool.name for tool in (await client.list_tools()).tools)
            if mode == "lister":
                forbidden = [name for name in names if FORBIDDEN.search(name)]
                print("outils exposés :", ", ".join(names))
                print(f"{len(names)} outils exposés aux agents ; outils d'approbation ou d'encaissement : {forbidden}")
                return 1 if forbidden else 0
            tried = await attack(client, app)
            expense = await client.call_tool("request_expense", {"amount": "50", "category": "outils"})
        for path, refused in tried:
            verdict = "refusé par l'outil" if refused else "accepté par l'outil, à vérifier sur l'enveloppe"
            print(f"{verdict} : {path}")
        status = app.kernel.finance.status()
        approved = bool((expense.structured_content or {}).get("approved"))
        print(f"dépense de 50 € demandée ensuite par l'agent : {'APPROUVÉE' if approved else 'refusée'}")
        print(f"{len(tried)} tentatives d'encaissement par un agent ; enveloppe de dépense : {status.envelope} €")
        return 0 if str(status.envelope) == "0.00" and not approved and len(tried) >= 4 else 1
    finally:
        app.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main(sys.argv[1])))
