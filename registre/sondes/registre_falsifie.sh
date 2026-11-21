#!/usr/bin/env bash
# Attaque du registre de preuves, dans un dépôt de travail jetable. Un ÉCHEC réel est consigné, puis :
#   1. maquillé en réussite par simple réécriture du fichier ;
#   2. maquillé PUIS rescellé (empreinte recalculée avec l'outil lui-même) ;
#   3. retiré du registre, alors que la branche de base le contenait.
# `omega check` doit refuser les trois.
set -euo pipefail
racine="$OMEGA_TMP/novarys"
mkdir -p "$racine/registre"
git init -q "$racine"
cat > "$racine/registre/capacites.toml" <<'TOML'
[[claim]]
id = "cassee"
domain = "OMEGA"
capability = "Une fonction cassée"
command = "false"
TOML
cat > "$racine/registre/actifs.toml" <<'TOML'
[[asset]]
name = "jetable"
title = "Actif de la sonde"
observed = "2026-11-21"
location = "aucune"
access = "aucun"
state = "fictif"
demonstrated = "rien"
dependencies = "aucune"
costs = "0 €"
reuse = "aucune"
proofs = "aucune"
blockers = "aucun"
next_action = "aucune"
TOML
registre="$racine/registre/preuves.jsonl"
: > "$racine/registre/tableau.toml"
omega() { uv run --quiet --project "$OMEGA_ROOT" omega --root "$racine" "$@"; }
refuse() {
  if omega check "$@" > "$OMEGA_TMP/verdict.txt" 2>&1; then
    echo "NON DÉTECTÉ"
    exit 1
  fi
  grep -m 1 "ÉCHEC" "$OMEGA_TMP/verdict.txt"
}
omega run || true
omega check
cp "$registre" "$OMEGA_TMP/origine.jsonl"

echo "1. échec maquillé en réussite :"
sed -i 's/"status":"ECHEC"/"status":"PROUVE"/' "$registre"
refuse

echo "2. échec maquillé puis rescellé :"
uv run --quiet --project "$OMEGA_ROOT" python - "$registre" <<'PY'
import json
import sys

from novarys_omega import registry

record = json.loads(open(sys.argv[1], encoding="utf-8").read())
record["hash"] = registry.seal(record)
open(sys.argv[1], "w", encoding="utf-8").write(registry.canonical(record) + "\n")
PY
refuse

echo "3. échec retiré du registre :"
: > "$registre"
omega render
refuse --base "$OMEGA_TMP/origine.jsonl"
echo "trois falsifications du registre, trois refus"
