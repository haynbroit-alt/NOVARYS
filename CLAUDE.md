# NOVARYS — notes pour les agents de code

## Reprise : par où commencer chaque session
1. Lire le dernier fichier de `journal/` (état vérifié, blocages, prochaine action) et `DECISIONS.md` (ce qui attend
   le propriétaire). Ne pas repartir du prompt, ne pas redemander ce qui y est déjà posé.
2. `.claude/bin/journal check uv run omega check` : le registre doit être intact avant tout travail.
3. Ne revendiquer aucun avancement qui n'est pas dans `registre/preuves.jsonl` ou dans une PR fusionnée.

## Règles du dépôt
- Python 3.12+, `uv`, bibliothèque standard uniquement pour `src/novarys_omega`. Vérification avant commit :
  `.claude/bin/journal verif bash -o pipefail -c 'uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy && uv run pytest -o addopts="" -q'`
- Langue : identifiants en anglais ; docstrings, messages, registres et docs en français.
- **Dépôt public.** N'y écrire aucune donnée personnelle, aucun nom de compte, aucun actif qui n'est pas déjà
  public. Dans le doute : ne pas écrire, et le dire au propriétaire.
- **Le registre ne se modifie jamais.** `registre/preuves.jsonl` ne s'écrit que par `omega run`. Un échec y
  reste. `CAPACITES.md` et `ACTIFS.md` sont générés (`omega render`) : ne pas les éditer.
- **Une capacité = une entrée du référentiel.** Fonction construite : commande, ligne de bilan, périmètre,
  attaque. Fonction non construite : entrée sans commande. Jamais de statut écrit à la main.
- **Une commande de preuve est du code** : pas de réseau inutile, pas de secret, rien d'irréversible, tout dans
  `$OMEGA_TMP`. Ne jamais exécuter le référentiel d'un autre dépôt sans l'avoir relu.
- Le moteur (SOVEREIGN) est épinglé à un commit dans `registre/capacites.toml`. Changer l'épingle invalide les
  preuves : relancer `omega run` dans la même PR.
- Cycle borné : 10 actions, 4 heures, 0 €. Fin de cycle = un fichier `journal/C-NNNN.md` (résultats, commandes,
  preuves, erreurs, coûts, blocages, prochaine action). Cinq cycles sans progrès mesuré : changer de méthode.
- Fusion, dépense, publication, envoi de message, création de compte : décisions du propriétaire. Les préparer dans
  `DECISIONS.md` (ce que ça débloque, coût, réponse en un mot) et continuer ce qui n'en dépend pas.
- Priorité (ADR 0002) : le premier encaissement. Deux missions actives au plus ; rien de nouveau à construire
  tant qu'une mission active ne l'exige pas.

## Fiabilité avant sobriété — la preuve prime sur le plafond de sortie
- Le plafond (15 000 caractères) ne doit jamais coûter une preuve. Une sortie d'échec trop longue est coupée en
  tête et fin, sans fichier ni code garanti : toute vérification (tests, lint, types, preuves) passe donc par
  `.claude/bin/journal <étiquette> <commande>` — journal complet sur disque, résumé < 8 000 caractères jamais
  tronqué, code de sortie exact en première et dernière ligne, même code renvoyé.
- Jamais `vérification | tail/head/grep` sans `pipefail` : le pipe renvoie le code du filtre (0) et masque l'échec.
  Le crochet `.claude/hooks/garde_pipe.py` refuse ces commandes.
- Sortie incomplète (aperçu tronqué, ligne de bilan absente : « N passed », « All checks passed! », « OK ») :
  lire le journal complet (Grep, Read avec `offset`) avant toute conclusion.
- « Réussi » exige : code 0 ET la ligne de bilan de l'outil vue. Sinon écrire « non vérifié » et pourquoi.
- Fusion d'une PR seulement si l'API GitHub donne `conclusion: success` pour TOUS les contrôles de la tête
  actuelle (SHA vérifié, aucun `in_progress` ni manquant) ET si les vérifications locales ont rendu code 0.
  Jamais sur la foi d'un journal partiel, d'un statut agrégé ou d'une exécution sur un autre SHA sans le dire.

## Sobriété — chaque session, sans exception
- Lire ciblé : Grep/Glob d'abord, puis Read avec `offset`/`limit`. Ne jamais relire un fichier déjà lu et inchangé.
- Ne jamais lire `registre/preuves.jsonl` en entier (une ligne par preuve, sorties brutes comprises) : chercher
  par identifiant de capacité (Grep) ou lire `CAPACITES.md`, qui renvoie au numéro de ligne.
- Sorties filtrées : jamais un log entier ; une vérification passe par `.claude/bin/journal` (voir « Fiabilité »).
  Les sorties Bash sont plafonnées par `.claude/settings.json`.
- Code minimal : le plus petit diff qui résout le problème ; pas d'abstraction, d'option ni de fichier « au cas où ».
- Modèles : sous-agent haiku pour chercher, sonnet pour implémenter ou relire, opus pour décider, fable seulement
  quand la difficulté l'exige. `/clear` entre deux tâches sans lien, `/compact` en disant quoi garder, `/context`
  pour voir ce qui pèse.
- Carte (au lieu d'ouvrir les fichiers un par un) : `docs/` (cahier des charges, décisions), `journal/` (cycles),
  `registre/capacites.toml` (ce qui est revendiqué), `registre/actifs.toml` (actifs), `registre/preuves.jsonl`
  (preuves, ajout seul), `registre/sondes/` (commandes de preuve et d'attaque), `src/novarys_omega/` : `model`
  (référentiel, statuts, niveaux), `runner` (exécution sans secrets, calcul du statut), `registry` (chaîne
  SHA-256), `report` (matrice et actifs en Markdown), `cli` (`omega run | verify | check | render`) ; tests
  miroirs dans `tests/`.
- Écosystème : avant de travailler dans un autre dépôt qui n'a pas de section « Sobriété », y ajouter ce kit dans la
  même PR — les sections « Fiabilité » et « Sobriété » (avec la carte de ce dépôt), `.claude/bin/journal`,
  `.claude/hooks/garde_pipe.py` et un `.claude/settings.json` (`bashOutputMaxChars`, crochet, lecture interdite
  de ses dossiers lourds). L'environnement cloud « Default » plafonne déjà les sorties Bash.
