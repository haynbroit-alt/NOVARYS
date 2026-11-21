#!/usr/bin/env bash
# Attaque du registre de preuves : dans un dépôt de travail jetable, on consigne un ÉCHEC réel puis on le
# maquille en réussite. `omega check` doit refuser le registre maquillé.
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
omega() { uv run --quiet --project "$OMEGA_ROOT" omega --root "$racine" "$@"; }
omega run || true
omega check
sed -i 's/"status":"ECHEC"/"status":"PROUVE"/' "$racine/registre/preuves.jsonl"
if omega check; then
  echo "MAQUILLAGE NON DÉTECTÉ"
  exit 1
fi
echo "échec maquillé en réussite : refusé par omega check"
