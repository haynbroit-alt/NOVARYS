#!/usr/bin/env bash
# Attaque de la suite de tests du moteur : dans une copie, on relève le plafond de dépense de 10 % à 90 %.
# Une suite qui protège la règle doit échouer, et échouer sur le test du plafond.
# Témoin : la même copie, non modifiée, doit d'abord réussir — sinon l'échec ne prouverait rien.
set -euo pipefail
copie="$OMEGA_TMP/moteur"
mkdir -p "$copie"
cp -r "$OMEGA_SUBJECT_MOTEUR/src" "$OMEGA_SUBJECT_MOTEUR/tests" "$copie/"
cible="$copie/src/sovereign/config.py"
cd "$OMEGA_SUBJECT_MOTEUR"
# Sans cache de code compilé (-B) : la mutation garde la taille du fichier et peut tomber dans la même seconde
# que le témoin ; Python réutiliserait alors le code compilé du témoin et la mutation ne serait pas chargée.
find "$copie" -name __pycache__ -prune -exec rm -rf {} +
essai() { PYTHONPATH="$copie/src" uv run python -B -m pytest -o addopts="" -q -p no:cacheprovider "$copie/tests/test_core.py"; }
if ! essai > "$OMEGA_TMP/temoin.txt" 2>&1; then
  echo "témoin en échec avant toute mutation : la sonde est à revoir"
  exit 3
fi
echo "témoin non modifié : $(tail -n 1 "$OMEGA_TMP/temoin.txt")"
avant=$(sha256sum < "$cible")
sed -i 's/^MAX_SPEND_RATIO = .*/MAX_SPEND_RATIO = Decimal("0.90")/' "$cible"
if [ "$avant" = "$(sha256sum < "$cible")" ]; then
  echo "mutation non appliquée : la sonde est à revoir"
  exit 3
fi
echo "mutation appliquée : plafond de dépense porté à 90 %"
essai
