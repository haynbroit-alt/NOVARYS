#!/usr/bin/env bash
# Attaque des garde-fous de l'entreprise mère (dépôt .1) : dans une copie, on retire une protection précise ; le test
# qui la garde doit alors échouer. Témoin : la même copie, non modifiée, doit d'abord réussir — sinon l'échec ne
# prouverait rien. Le dépôt évalué n'est jamais modifié : tout se passe dans $OMEGA_TMP.
# Usage : mutation_mere.sh livemode | garde | banque
set -euo pipefail
cas="${1:?cas attendu : livemode, garde ou banque}"
copie="$OMEGA_TMP/mere"
mkdir -p "$copie"
cp -r "$OMEGA_SUBJECT_MERE/mere" "$OMEGA_SUBJECT_MERE/tests" "$OMEGA_SUBJECT_MERE/donnees" "$copie/"
case "$cas" in
  livemode) # un paiement en mode test est compté comme de l'argent encaissé
    cible="mere/stripe.py"; motif="test_paiement_en_mode_test_ignore"
    avant='if not c.get("livemode"):'; apres='if False:' ;;
  garde) # la garde ne voit plus les adresses e-mail dans les sorties publiques
    cible="mere/garde.py"; motif="test_fuites_detectees"
    avant='"adresse e-mail": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),'; apres='"adresse e-mail": re.compile(r"(?!x)x"),' ;;
  banque) # l'étape « encaissé » est franchie sans que la banque ait confirmé le crédit
    cible="mere/chaine.py"; motif="test_argent_encaisse_franchit_l_etape_seulement_avec_la_banque"
    avant='and du is not None and credite.valeur >= du)'; apres='and du is not None and credite.valeur >= du) or True' ;;
  *) echo "cas inconnu : $cas"; exit 3 ;;
esac
find "$copie" -name __pycache__ -prune -exec rm -rf {} +
essai() { (cd "$copie" && python3 -B -m unittest discover -s tests -k "$motif" 2>&1); }
if ! essai > "$OMEGA_TMP/temoin.txt"; then
  echo "témoin en échec avant toute mutation : la sonde est à revoir"
  exit 3
fi
echo "témoin non modifié : $(tail -n 1 "$OMEGA_TMP/temoin.txt")"
AVANT="$avant" APRES="$apres" python3 - "$copie/$cible" <<'PY'
import os, sys
from pathlib import Path
path = Path(sys.argv[1]); text = path.read_text(encoding="utf-8")
if text.count(os.environ["AVANT"]) != 1:
    print("mutation non appliquée : la sonde est à revoir"); sys.exit(3)
path.write_text(text.replace(os.environ["AVANT"], os.environ["APRES"]), encoding="utf-8")
PY
echo "mutation appliquée : $cas"
essai
