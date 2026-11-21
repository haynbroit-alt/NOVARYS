#!/usr/bin/env bash
# Attaque de l'observateur : un dépôt piégé contient du code qui se signale s'il est exécuté (conftest.py,
# setup.py, scripts npm, Makefile) et une clé factice. L'observateur ne doit que lire : le piège ne doit pas
# se déclencher, et la clé doit être signalée.
set -euo pipefail
depot="$OMEGA_TMP/depots/piege"
mkdir -p "$depot"
cd "$depot"
git init -q
cat > conftest.py <<'PY'
import pathlib

pathlib.Path(__file__).with_name("EXECUTE").write_text("exécuté")
PY
cp conftest.py setup.py
cp conftest.py sitecustomize.py
printf '{"name":"piege","scripts":{"preinstall":"touch EXECUTE","install":"touch EXECUTE","test":"touch EXECUTE"}}\n' > package.json
printf 'all:\n\ttouch EXECUTE\n' > Makefile
# La clé est assemblée ici pour qu'aucun motif de clé ne figure dans ce dépôt.
printf 'AWS_ACCESS_KEY_ID = "%s%s"\n' "AKIA" "QWERTYUIOPASDFGH" > reglages.py
git add -A
git -c user.name=sonde -c user.email=sonde@invalid commit -qm "dépôt piégé"
cd "$OMEGA_SUBJECT_MOTEUR"
SOVEREIGN_HOME="$OMEGA_TMP/home" uv run sovereign ecosystem scan "$OMEGA_TMP/depots" > "$OMEGA_TMP/scan.json"
if [ -e "$depot/EXECUTE" ]; then
  echo "PIÈGE DÉCLENCHÉ : du code du dépôt observé a été exécuté"
  exit 1
fi
python3 - "$OMEGA_TMP/scan.json" <<'PY'
import json
import sys

secrets = json.load(open(sys.argv[1], encoding="utf-8"))["repos"][0]["secrets"]
if not secrets:
    sys.exit("clé factice NON signalée")
print(f"piège non exécuté ; clé factice signalée ({len(secrets)} constat)")
PY
