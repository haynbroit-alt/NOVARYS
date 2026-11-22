#!/usr/bin/env bash
# Attaque des garde-fous d'OMNIA : dans une copie, on retire une protection précise ; le test qui la garde doit
# alors échouer. Témoin : la même copie, non modifiée, doit d'abord réussir — sinon l'échec ne prouverait rien.
# Usage : mutation_gestion.sh droits | ecrasement | stripe
set -euo pipefail
cas="${1:?cas attendu : droits, ecrasement ou stripe}"
copie="$OMEGA_TMP/gestion"
mkdir -p "$copie"
cp -r "$OMEGA_SUBJECT_GESTION/src" "$OMEGA_SUBJECT_GESTION/test" "$OMEGA_SUBJECT_GESTION/seed" \
  "$OMEGA_SUBJECT_GESTION/public" "$OMEGA_SUBJECT_GESTION/package.json" "$copie/"
case "$cas" in
  droits) # la coordination ne filtre plus selon les droits du compte
    cible="src/server.js"; motif="coordination"
    avant="filter((w) => !c.user || c.user.admin || k.auth.roleIn(c.user, w.id))"; apres="filter(() => true)" ;;
  ecrasement) # la restauration accepte d'écraser une instance qui porte du travail
    cible="src/core/backup.js"; motif="sauvegarde d'instance"
    avant="if (!pristine()) fail("; apres="if (false) fail(" ;;
  stripe) # n'importe quel espace peut importer le compte Stripe
    cible="src/core/kernel.js"; motif="Stripe : avec un espace central"
    avant="need(w.central || !db.get("; apres="need(true || !db.get(" ;;
  *) echo "cas inconnu : $cas"; exit 3 ;;
esac
essai() { (cd "$copie" && node --disable-warning=ExperimentalWarning --test --test-name-pattern="$motif" test/omnia.test.js); }
if ! essai > "$OMEGA_TMP/temoin.txt" 2>&1; then
  echo "témoin en échec avant toute mutation : la sonde est à revoir"
  exit 3
fi
echo "témoin non modifié : $(grep '^# pass' "$OMEGA_TMP/temoin.txt")"
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
