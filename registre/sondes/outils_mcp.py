"""Sonde : quels outils le moteur expose-t-il aux agents (MCP) ? Aucun ne doit approuver ni encaisser.

Usage : python outils_mcp.py lister | attaquer   (SOVEREIGN_HOME doit désigner un dossier jetable).
``lister`` refuse tout outil dont le nom évoque une approbation ou un encaissement. ``attaquer`` tente, par les
outils réellement exposés, de déclarer un encaissement pour s'ouvrir un budget : l'enveloppe doit rester à 0.
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
ATTACKS = [
    ("import_csv", {"kind": "collections", "csv_text": CSV}),
    ("import_csv", {"kind": "encaissements", "csv_text": CSV}),
    ("skill_run", {"skill": "finance-budget", "action": "record_revenue", "input": {"amount": "100000"}}),
]


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
            for tool, arguments in ATTACKS:
                result = await client.call_tool(tool, arguments)
                print(f"{tool} {arguments.get('kind') or arguments.get('action')} : erreur={result.is_error}")
        envelope = app.kernel.finance.status().envelope
        print(f"{len(ATTACKS)} tentatives d'encaissement par un agent ; enveloppe de dépense : {envelope} €")
        return 0 if str(envelope) == "0.00" else 1
    finally:
        app.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main(sys.argv[1])))
