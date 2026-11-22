# Capacités de NOVARYS Ω : ce qui est prouvé

> Fichier généré par `omega render` à partir de `registre/capacites.toml` (ce qui est revendiqué) et de
> `registre/preuves.jsonl` (ce qui a été exécuté). Ne pas le modifier à la main.

**Verdict : NOVARYS n'est pas opérationnel.** 19 fonction(s) sur 28 sont sous le niveau TESTÉ ; 9 domaine(s) sur 10 n'ont aucune fonction démontrée sur données réelles (CORE, INTELLIGENCE, INTERNET, ENGINEERING, BUSINESS, AGENTS, MEMORY, OMEGA, SOVEREIGN).

Règle du verdict : aucune fonction sous TESTÉ, et dans chaque domaine au moins une fonction
OPÉRATIONNELLE. Rentable est une autre question : elle se lit dans les encaissements, pas ici.

Dépôt évalué « moteur » : `haynbroit-alt/SOVEREIGN` au commit `7cddfbd53ae6`.
Dépôt évalué « gestion » : `haynbroit-alt/Logiciel-` au commit `a6fd9a74371d`.

## Vue d'ensemble

| Domaine | ABSENT | DISPONIBLE | CONNECTÉ | TESTÉ | OPÉRATIONNEL | VALIDÉ |
|---|---:|---:|---:|---:|---:|---:|
| CORE | 1 | · | · | 2 | · | · |
| INTELLIGENCE | · | · | · | 1 | · | · |
| DISCOVERY | 1 | · | · | · | 1 | · |
| INTERNET | 1 | · | · | · | · | · |
| ENGINEERING | 1 | 1 | · | · | · | · |
| BUSINESS | 7 | · | · | 1 | · | · |
| AGENTS | 1 | · | 1 | · | · | · |
| MEMORY | · | 2 | 1 | 1 | · | · |
| OMEGA | 1 | · | · | 1 | · | · |
| SOVEREIGN | · | 1 | · | 2 | · | · |

## Scénarios de validation (cahier des charges, section 14)

| N° | Scénario | Fonctions rattachées | Niveau le plus bas |
|---:|---|---|---|
| 1 | Recherche multi-source vérifiée | `recherche-multi-source` | ABSENT |
| 2 | Inspection, correction et livraison d'un projet | `livraison-projet` | ABSENT |
| 3 | Invention comparée et falsifiable | `comparaison-sept-criteres` | ABSENT |
| 4 | Création d'une offre réellement commercialisable | `premier-encaissement-reel` | ABSENT |
| 5 | Reprise fiable d'une mission interrompue | `gestion-sauvegarde-restaurable`, `reprise-tache-interrompue` | DISPONIBLE |
| 6 | Blocage d'une action non autorisée et protection des secrets | `gestion-cloisonnement-des-projets`, `registre-ajout-seul`, `depense-sans-encaissement-refusee`, `aucune-approbation-par-agent` | DISPONIBLE |
| 7 | Reproduction indépendante d'une capacité | `reproduction-par-un-tiers` | ABSENT |

## CORE

| Fonction | Statut | Niveau | Dernière preuve | Limites |
|---|---|---|---|---|
| Le noyau du moteur passe ses contrôles : lint, format, types et suite de tests (`noyau-suite-verifiee`) | PROUVÉ | TESTÉ | 2026-11-21 · agent · moteur@7cddfbd5 · 2 exécution(s) · attaque résistée · n°14 | Une suite verte prouve ce que la suite teste, pas l'absence de défaut : jusqu'au commit 62ecac3, l'attaque par REPLACE de `registre-ajout-seul` passait au travers de ses 291 tests. |
| La ligne de commande du moteur rend l'état du système sur un espace neuf (`cli-etat-systeme`) | PROUVÉ | TESTÉ | 2026-11-21 · agent · moteur@7cddfbd5 · 2 exécution(s) · attaque résistée · n°15 | Espace vide : aucune donnée d'entreprise. L'API REST et le serveur MCP ne sont couverts que par les tests du moteur ; l'interface web exigée par le cahier des charges n'existe pas. |
| Interface web de pilotage (`interface-web`) | — | ABSENT | non construite | Non construite. Interfaces existantes du moteur : CLI, API REST, MCP. |

## INTELLIGENCE

| Fonction | Statut | Niveau | Dernière preuve | Limites |
|---|---|---|---|---|
| La boucle du directeur s'exécute de bout en bout sur le jeu de démonstration, et son mode à blanc n'exécute rien (`directeur-boucle-demo`) | PROUVÉ | TESTÉ | 2026-11-21 · agent · moteur@7cddfbd5 · 2 exécution(s) · attaque résistée · n°16 | La preuve établit que chaque phase laisse sa trace dans le rapport (compétences mobilisées, constats, recommandations, conseil, simulation) et que le mode à blanc ne crée rien. Elle ne mesure pas la qualité des décisions : données de démonstration, aucune donnée d'entreprise chargée. |

## DISCOVERY

| Fonction | Statut | Niveau | Dernière preuve | Limites |
|---|---|---|---|---|
| Observer en lecture seule les dépôts réels du compte et en tirer des faits mesurés (`observation-depots-reels`) | PROUVÉ | OPÉRATIONNEL | 2026-11-21 · agent · moteur@7cddfbd5 · 2 exécution(s) · attaque résistée · n°17 | Mesure la forme (taille, tests, CI, dépendances), pas la valeur commerciale. « secrets=0 » vaut pour les motifs que l'observateur connaît. Les dépôts sont pris à leur dernier commit, listé dans la sortie : la preuve n'est pas épinglée et n'est plus rejouable si un dépôt devient privé. Les actifs hors GitHub ne sont pas observés. |
| Comparer trois candidats sur sept critères et consigner la décision (`comparaison-sept-criteres`) | — | ABSENT | non construite | Non construite dans le moteur. La comparaison de ce cycle (docs/adr/0001) a été faite à la main ; le moteur a un conseil et un classement multicritère, pas ce protocole. |

## INTERNET

| Fonction | Statut | Niveau | Dernière preuve | Limites |
|---|---|---|---|---|
| Recherche parallèle multi-sources avec citations, déduplication, cache et reprise (`recherche-multi-source`) | — | ABSENT | non construite | Non construite. Le moteur sait seulement lire des flux RSS (option « watch », non prouvée ici). Les recherches de ce cycle ont été faites par l'agent de session, pas par le moteur. |

## ENGINEERING

| Fonction | Statut | Niveau | Dernière preuve | Limites |
|---|---|---|---|---|
| Inspecter, corriger, tester et livrer un projet de code (`livraison-projet`) | — | ABSENT | non construite | Non construite dans le moteur. C'est l'agent de session qui le fait, sous revue humaine par PR : ce cycle, le correctif de `registre-ajout-seul`. |
| L'application de travail (OMNIA) passe sa suite de tests (`gestion-suite-verifiee`) | INCONNU | DISPONIBLE | jamais exécutée | Une suite verte prouve ce que la suite teste. Les fournisseurs d'IA et les envois vers les messageries n'y sont éprouvés que contre des réponses simulées. Aucune donnée réelle : le service en ligne n'est pas l'objet de cette preuve. |

## BUSINESS

| Fonction | Statut | Niveau | Dernière preuve | Limites |
|---|---|---|---|---|
| Enregistrer un encaissement et en déduire au centime l'enveloppe de dépense autorisée (`encaissement-et-enveloppe`) | PROUVÉ | TESTÉ | 2026-11-21 · agent · moteur@7cddfbd5 · 2 exécution(s) · attaque résistée · n°18 | Montants fictifs. Aucun encaissement réel n'est enregistré dans le moteur à ce jour. |
| Offre mise en vente et premier encaissement réel vérifié (`premier-encaissement-reel`) | — | ABSENT | non construite | Non démontré : aucun encaissement n'est enregistré dans le moteur, et les ventes éventuelles d'actifs hors GitHub sont inconnues de ce dépôt. Trois offres sont prêtes mais aucune n'est en vente (voir ACTIFS.md) ; ce qui manque relève du propriétaire : statut, comptes, validation. |
| REACHER : lire les performances et les ventes des comptes commerciaux du propriétaire (`reacher-lecture-comptes`) | — | ABSENT | non construite | Non démontré par une commande. Au 21/11/2026 (cycle C-0005), un des sept comptes sondés est lisible, par un connecteur de la session que omega ne peut pas rejouer : son audience est relevée, aucune vente. Les six autres ne sont pas reliés ; la boutique bloquée est abandonnée, remplacée par celle d'un réseau social. Le détail est dans le tableau de bord privé. |
| REACHER : chaque jour, mettre le tableau de bord à jour et proposer au plus trois actions (`reacher-brief-quotidien`) | — | ABSENT | non construite | Non construit. Aucune tâche programmée tant qu'aucune boutique ni aucun réseau actif n'est lisible et que le propriétaire ne l'a pas demandée : un brief sans donnée nouvelle serait du travail fictif. |
| REACHER : produire un contenu commercial et le publier après validation du propriétaire (`reacher-publication-validee`) | — | ABSENT | non construite | Non démontré. Aucun réseau n'est relié à un outil de publication ; aucun contenu n'a été soumis ni publié. |
| REACHER : trouver des prospects, répondre aux demandes et suivre les commandes (`reacher-prospects-commandes`) | — | ABSENT | non construite | Non démontré. Aucune boutique ni messagerie n'est lisible ; les seuls prospects connus sont ceux du dépôt Velyx, à régénérer. |
| Portail velyx.org en ligne : une page par projet, servie depuis le registre des actifs (`portail-velyx-en-ligne`) | — | ABSENT | non construite | Non démontré par une commande. Constaté le 21/11/2026 : les 23 pages de site/ sont servies, identiques au dépôt, à une adresse de l'hébergeur (Cloudflare Workers), publiées à chaque fusion sur la branche principale. Le domaine velyx.org n'y est pas rattaché : il pointe encore ailleurs et répond « site introuvable » (DECISIONS.md, D9). Le portail montre les registres ; il n'exécute aucune action. |
| Centre de connexions : relier, autoriser, surveiller et déconnecter les services externes depuis VELYX (`centre-de-connexions`) | — | ABSENT | non construite | Non démontré par une commande. Ce qui existe au 21/11/2026 : un registre (registre/connexions.toml) et sa page, dont chaque état vient d'un essai en lecture fait par l'agent avec les connecteurs du compte du propriétaire, que omega ne peut pas rejouer. Ce qui n'existe pas : un serveur VELYX qui détient ses propres autorisations OAuth, reçoit des webhooks, synchronise seul et révoque une liaison. Connecter et déconnecter se font dans les réglages du compte, pas dans VELYX. |

## AGENTS

| Fonction | Statut | Niveau | Dernière preuve | Limites |
|---|---|---|---|---|
| Répartir des missions entre agents déclarés selon leurs capacités et leur charge (`repartition-missions-agents`) | ÉTAYÉ | CONNECTÉ | 2026-11-21 · agent · moteur@7cddfbd5 · 2 exécution(s) · attaque non tentée · n°19 | Tests unitaires seulement, sans attaque : ÉTAYÉ au mieux. Aucun agent réel n'est branché sur le moteur. |
| Faire travailler des agents spécialisés en parallèle et trancher selon les preuves (`orchestration-agents`) | — | ABSENT | non construite | Non construite. Les agents de ce cycle (relecture indépendante) ont été lancés par l'agent de session. |

## MEMORY

| Fonction | Statut | Niveau | Dernière preuve | Limites |
|---|---|---|---|---|
| Sauvegarde chiffrée de toute l'instance, restaurée à l'identique, sans jamais écraser un travail (`gestion-sauvegarde-restaurable`) | INCONNU | DISPONIBLE | jamais exécutée | Données de test. La phrase secrète n'est enregistrée nulle part : perdue, la sauvegarde est irrécupérable. Les fichiers vidéo du studio n'y figurent pas. Sur un hébergement sans disque persistant, la sauvegarde ne protège que si le propriétaire la télécharge. |
| Le registre financier, les dépenses approuvées et le journal d'audit ne peuvent pas être réécrits (`registre-ajout-seul`) | PROUVÉ | TESTÉ | 2026-11-21 · agent · moteur@7cddfbd5 · 2 exécution(s) · attaque résistée · n°20 | Hors périmètre : un accès au fichier de base permet de supprimer les déclencheurs. Les données de la sonde sont fictives. |
| Une tâche interrompue est reprise sans refaire les étapes déjà validées (`reprise-tache-interrompue`) | ÉTAYÉ | CONNECTÉ | 2026-11-21 · agent · moteur@7cddfbd5 · 2 exécution(s) · attaque non tentée · n°21 | Tests unitaires seulement : aucune interruption réelle (processus tué) n'a été provoquée. ÉTAYÉ au mieux. |
| L'état du moteur est sauvegardé à chaque cycle quotidien (`etat-persistant-a-jour`) | ÉCHEC | DISPONIBLE | 2026-11-21 · agent · moteur@7cddfbd5 · 2 exécution(s) · attaque non tentée · n°22 | Depuis le 18/11/2026 le cycle quotidien se termine « réussi » en dix secondes sans rien exécuter : son garde-fou de confidentialité le bloque parce que le dépôt est public. Décision du propriétaire : rendre le dépôt privé, ou autoriser l'état public. |

## OMEGA

| Fonction | Statut | Niveau | Dernière preuve | Limites |
|---|---|---|---|---|
| L'outil de preuve passe ses contrôles : lint, types et tests, cas d'attaque compris (`outil-de-preuve`) | PROUVÉ | TESTÉ | 2026-11-21 · local · ce dépôt@8d5e3f73 · 2 exécution(s) · attaque résistée · n°30 | L'outil prouve qu'une commande donne le résultat attendu ; il ne juge pas si la commande choisie démontre bien la capacité. Ce jugement reste une relecture humaine du référentiel. |
| Une capacité prouvée est reproduite par un second acteur, qui l'écrit au registre (`reproduction-par-un-tiers`) | — | ABSENT | non construite | Non construite. La CI rejoue les preuves étiquetées « ci » à chaque PR (`omega verify`) mais n'écrit pas au registre, et le nom d'acteur consigné n'est qu'une déclaration : l'outil n'attribue donc jamais le niveau VALIDÉ. |

## SOVEREIGN

| Fonction | Statut | Niveau | Dernière preuve | Limites |
|---|---|---|---|---|
| Chaque projet garde ses données : comptes, rôles, coordination et mémoire partagée respectent les droits (`gestion-cloisonnement-des-projets`) | INCONNU | DISPONIBLE | jamais exécutée | Données de test. Les droits n'agissent qu'avec des comptes : avec le seul jeton d'accès, qui le détient peut tout. Pas de double authentification. |
| Une dépense est refusée tant qu'aucun argent n'a réellement été encaissé (`depense-sans-encaissement-refusee`) | PROUVÉ | TESTÉ | 2026-11-21 · agent · moteur@7cddfbd5 · 2 exécution(s) · attaque résistée · n°23 | Le moteur autorise ou refuse ; il n'a aucun accès bancaire et ne peut ni payer ni empêcher un paiement fait ailleurs. |
| Par les outils exposés aux agents, on ne peut ni approuver une dépense ni se déclarer un encaissement (`aucune-approbation-par-agent`) | PROUVÉ | TESTÉ | 2026-11-21 · agent · moteur@7cddfbd5 · 2 exécution(s) · attaque résistée · n°24 | Le contrôle lit les noms des outils ; c'est l'attaque qui éprouve leur effet, sur quatre voies seulement. Jusqu'au commit 62ecac3, le filtre de surface laissait passer l'alias « encaissements » et seul le registre refusait ; les deux refusent désormais. L'approbation en ligne de commande n'est pas réservée techniquement à un humain : la barrière réelle est que l'agent n'y a pas recours et que les PR sont relues. |

## Lecture

- **Statuts** (calculés à l'exécution) : PROUVÉ — au moins deux exécutions concordantes, ligne de bilan vue,
  périmètre écrit, code validé dans Git, attaque tentée et résistée ; ÉTAYÉ — résultat correct mais preuve
  incomplète ; INCONNU — rien d'exécuté, ou sortie retenue ; CONFLIT — exécutions contradictoires ; ÉCHEC —
  test échoué ou attaque réussie.
- **Ce que PROUVÉ ne dit pas** : que la commande choisie démontre bien la capacité. L'outil vérifie un
  résultat attendu ; le choix de la commande et de l'attaque se juge en relisant `registre/capacites.toml`.
- **Niveaux** (déduits des preuves) : ABSENT — non construit ; DISPONIBLE — commande déclarée sans preuve
  valide ; CONNECTÉ — ÉTAYÉ ; TESTÉ — PROUVÉ sur données de test ; OPÉRATIONNEL — PROUVÉ sur données
  réelles ; VALIDÉ — jamais attribué aujourd'hui : il faudrait un second acteur dont l'identité se vérifie.
- Le numéro en fin de preuve renvoie à la ligne du registre, qui contient la commande et sa sortie brute.
