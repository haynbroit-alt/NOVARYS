#!/usr/bin/env bash
# Attaque de la suite de tests du moteur : dans une copie, on relève le plafond de dépense de 10 % à 90 %.
# Une suite qui protège la règle doit échouer. Si elle passe, elle ne protège rien.
set -euo pipefail
copie="$OMEGA_TMP/moteur"
mkdir -p "$copie"
cp -r "$OMEGA_SUBJECT_MOTEUR/src" "$OMEGA_SUBJECT_MOTEUR/tests" "$copie/"
cible="$copie/src/sovereign/config.py"
avant=$(sha256sum < "$cible")
sed -i 's/^MAX_SPEND_RATIO = .*/MAX_SPEND_RATIO = Decimal("0.90")/' "$cible"
if [ "$avant" = "$(sha256sum < "$cible")" ]; then
  echo "mutation non appliquée : la sonde est à revoir"
  exit 3
fi
cd "$OMEGA_SUBJECT_MOTEUR"
PYTHONPATH="$copie/src" uv run python -m pytest -o addopts="" -q -p no:cacheprovider "$copie/tests/test_core.py"
