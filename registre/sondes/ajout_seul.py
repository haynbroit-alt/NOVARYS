"""Sonde : le registre financier, les dépenses et le journal d'audit du moteur sont-ils en ajout seul ?

Usage : python ajout_seul.py modifier | remplacer   (SOVEREIGN_HOME doit désigner un dossier jetable).
``modifier`` tente UPDATE et DELETE. ``remplacer`` tente INSERT OR REPLACE, qui supprime la ligne en conflit
sans déclencher BEFORE DELETE. Chaque tentative doit être refusée et les données rester intactes.
"""

import os
import sqlite3
import sys

from sovereign.kernel import Kernel

LEDGER = "ledger(id, entry_type, amount_cents, currency, occurred_on, reference, created_at)"
ATTEMPTS = {
    "modifier": [
        ("UPDATE registre", "UPDATE ledger SET amount_cents = 99999999"),
        ("DELETE registre", "DELETE FROM ledger"),
        ("UPDATE montant d'une dépense", "UPDATE expenses SET amount_cents = 1"),
        ("DELETE dépenses", "DELETE FROM expenses"),
        ("UPDATE audit", "UPDATE audit_log SET actor = 'falsifié'"),
        ("DELETE audit", "DELETE FROM audit_log"),
    ],
    "remplacer": [
        (
            "REPLACE registre (même référence)",
            f"REPLACE INTO {LEDGER} VALUES ('led_x', 'collection', 99999999, 'EUR', '2026-11-01', 'sonde-1', 't')",
        ),
        (
            "REPLACE registre (même identifiant)",
            f"INSERT OR REPLACE INTO {LEDGER} "
            "SELECT id, 'collection', 88888888, 'EUR', '2026-11-01', reference, 't' FROM ledger LIMIT 1",
        ),
        (
            "REPLACE dépense",
            "INSERT OR REPLACE INTO expenses(id, amount_cents, currency, category, status, created_at) "
            "SELECT id, 1, 'EUR', 'outils', 'approved', 't' FROM expenses LIMIT 1",
        ),
        (
            "REPLACE audit",
            "INSERT OR REPLACE INTO audit_log(seq, at, actor, action, entity) VALUES (1, 't', 'falsifié', 'a', 'e')",
        ),
    ],
}


def main(mode: str) -> int:
    kernel = Kernel.open(os.environ["SOVEREIGN_HOME"])
    kernel.finance.record_collection("100", "2026-11-01", counterparty="Client de la sonde", reference="sonde-1")
    kernel.finance.request_expense("4", "outils")
    path = kernel.db.path
    kernel.close()
    db = sqlite3.connect(path, isolation_level=None)  # connexion brute : aucun réglage du moteur
    refused = 0
    for name, sql in ATTEMPTS[mode]:
        try:
            db.execute(sql)
            print(f"ACCEPTÉ  {name}")
        except sqlite3.Error as exc:
            refused += 1
            print(f"refusé   {name} ({exc})")
    intact = (
        db.execute("SELECT amount_cents FROM ledger WHERE reference = 'sonde-1'").fetchall() == [(10_000,)]
        and db.execute("SELECT amount_cents FROM expenses").fetchall() == [(400,)]
        and db.execute("SELECT actor FROM audit_log WHERE seq = 1").fetchone() != ("falsifié",)
    )
    print(f"{refused}/{len(ATTEMPTS[mode])} tentatives refusées ; données {'intactes' if intact else 'ALTÉRÉES'}")
    return 0 if refused == len(ATTEMPTS[mode]) and intact else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
