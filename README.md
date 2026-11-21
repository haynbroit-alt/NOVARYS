# NOVARYS Ω

NOVARYS est un moteur de recherche, d'invention, d'ingénierie et de production économique, sous contrôle
humain. Ce dépôt n'est pas le moteur : c'est son **poste de pilotage**. Il dit ce que NOVARYS prétend savoir
faire, le fait exécuter, l'attaque, et garde la trace de ce qui a tenu et de ce qui a échoué.

- Le moteur lui-même est le dépôt [SOVEREIGN](https://github.com/haynbroit-alt/SOVEREIGN) (noyau, registre
  financier, mémoire, validations humaines, CLI, API, MCP). Pourquoi un seul moteur et pas deux :
  [docs/adr/0001-un-seul-moteur.md](docs/adr/0001-un-seul-moteur.md).
- Ce que NOVARYS doit devenir : [docs/CAHIER_DES_CHARGES.md](docs/CAHIER_DES_CHARGES.md).

## État réel

| Question | Réponse | Où le lire |
|---|---|---|
| Qu'est-ce qui est prouvé ? | La matrice des capacités, fonction par fonction | [CAPACITES.md](CAPACITES.md) |
| Quels actifs existent, et qu'est-ce qui les bloque ? | Le registre des actifs | [ACTIFS.md](ACTIFS.md) |
| Où en est le travail ? | Le journal des cycles, le plus récent en dernier | [journal/](journal/) |
| Qu'est-ce qui attend le propriétaire ? | Les décisions à prendre, avec la réponse en un mot | [DECISIONS.md](DECISIONS.md) |
| Sur quoi porte l'effort ? | Le premier encaissement, deux missions actives au plus | [ADR 0002](docs/adr/0002-priorite-premier-encaissement.md) |
| Et le commercial ? | REACHER : la mission, son état réel, ce qui lui manque | [docs/REACHER.md](docs/REACHER.md) |

NOVARYS n'est pas opérationnel au sens de son cahier des charges, et rien ne prouve qu'il soit rentable : aucun
encaissement n'est enregistré dans le moteur à ce jour. Les ventes éventuelles d'actifs hors GitHub ne sont pas
connues de ce dépôt. Ces faits se mettent à jour avec les preuves, pas avec les intentions.

## Le protocole de preuves Ω

Une capacité revendiquée s'écrit dans [`registre/capacites.toml`](registre/capacites.toml) avec la commande qui
la démontre et l'attaque qui tente de la réfuter. L'outil `omega` exécute, calcule le statut et consigne :

| Statut | Condition, calculée par l'outil |
|---|---|
| PROUVÉ | au moins deux exécutions concordantes, ligne de bilan vue, périmètre écrit, code validé dans Git, attaque tentée et résistée |
| ÉTAYÉ | résultat correct, preuve incomplète |
| INCONNU | rien d'exécuté, ou sortie retenue parce qu'un secret y apparaissait |
| CONFLIT | exécutions contradictoires |
| ÉCHEC | test échoué, ou attaque réussie |

Chaque preuve porte les sept champs du cahier des charges (capacité, commande, sortie brute, statut, impact,
reproductibilité, limites) dans [`registre/preuves.jsonl`](registre/preuves.jsonl). Ce registre est en ajout
seul : chaque ligne est chaînée à la précédente, et la CI refuse une PR qui en retire ou en réécrit une.
Les échecs y restent.

Une fonction exigée mais non construite reste dans le référentiel, sans commande : elle apparaît ABSENTE.

## Utilisation

```bash
uv sync                      # Python 3.12 ou plus ; l'outil n'a aucune dépendance
uv run omega check           # registre intact, fichiers générés à jour
uv run omega verify --tag ci # rejoue les preuves et les compare au registre, sans rien écrire
uv run omega run             # exécute, consigne au registre, régénère CAPACITES.md et ACTIFS.md
```

Les preuves visent le moteur à un commit épinglé dans le référentiel. Par défaut l'outil le cherche dans
`../SOVEREIGN`, sinon : `--subject moteur=/chemin/vers/SOVEREIGN`. Le moteur doit être exactement à ce commit,
sans modification, et installé (`uv sync --locked` dans son dossier).

## Limites à connaître

- **L'outil prouve qu'une commande donne le résultat attendu.** Il ne juge pas si la commande choisie démontre
  bien la capacité : ce jugement est une relecture humaine du référentiel, à chaque PR.
- **Une commande de preuve est du code.** Ne jamais lancer `omega run` sur le référentiel d'un dépôt qu'on ne
  maîtrise pas. Les commandes tournent sans les secrets de la session, mais avec vos droits sur la machine :
  elles peuvent lire vos fichiers et l'environnement d'autres processus. Le retrait des secrets et le contrôle
  des sorties protègent des fuites accidentelles, pas d'une commande malveillante.
- **Le registre protège le passé, pas l'écriture.** Une preuve retirée ou réécrite est refusée par la CI. Une
  preuve inventée puis ajoutée proprement n'est démasquée que si elle est rejouée : la CI rejoue celles qui
  portent l'étiquette « ci », les autres reposent sur la relecture de la PR.
- **Le niveau VALIDÉ n'est jamais attribué.** Il demanderait une preuve reproduite par un second acteur dont
  l'identité se vérifie. Le nom d'acteur consigné n'est qu'une déclaration, et la CI rejoue les preuves sans
  écrire au registre.
- **Le dépôt évalué est contrôlé par Git, pas au-delà.** Commit épinglé, racine du dépôt, aucun fichier modifié,
  ajouté ou masqué : tout cela est vérifié. Les fichiers que Git ignore (environnement installé, caches) ne le
  sont pas ; la CI, elle, repart d'un clone neuf.
- **Ce dépôt est public.** Rien de privé n'y est mémorisé : ni donnée personnelle, ni compte, ni chiffre d'un
  actif qui n'est pas déjà public.
