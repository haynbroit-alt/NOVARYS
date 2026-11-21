#!/usr/bin/env bash
# Clone sans historique les dépôts publics listés dans registre/depots.txt, puis les fait observer par le
# moteur (lecture seule : aucun code de ces dépôts n'est exécuté). Affiche ce qui a été observé, commit compris.
set -euo pipefail
mkdir -p "$OMEGA_TMP/depots"
while read -r depot; do
  [ -n "$depot" ] || continue
  git clone -q --depth 1 "https://github.com/$depot" "$OMEGA_TMP/depots/${depot#*/}"
  echo "observé : $depot au commit $(git -C "$OMEGA_TMP/depots/${depot#*/}" rev-parse --short=12 HEAD)"
done < "$OMEGA_ROOT/registre/depots.txt"
cd "$OMEGA_SUBJECT_MOTEUR"
SOVEREIGN_HOME="$OMEGA_TMP/espace" uv run sovereign ecosystem scan "$OMEGA_TMP/depots" > "$OMEGA_TMP/scan.json"
python3 - "$OMEGA_TMP/scan.json" <<'PY'
import json
import sys

repos = json.load(open(sys.argv[1], encoding="utf-8"))["repos"]
print(
    f"depots={len(repos)} secrets={sum(len(r['secrets']) for r in repos)}"
    f" lignes_de_code={sum(r['loc'] for r in repos)} cas_de_test={sum(r['cas_de_test'] for r in repos)}"
    f" avec_ci={sum(1 for r in repos if r['ci'])}"
)
for r in repos:
    print(f"- {r['repo']} : {r['loc']} lignes, {r['cas_de_test']} cas de test, CI {'oui' if r['ci'] else 'non'}")
PY
