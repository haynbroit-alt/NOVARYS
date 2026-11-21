# ADR 0001 — Un seul moteur : SOVEREIGN reste le noyau, NOVARYS le pilote et le prouve

Date : 21/11/2026. Statut : proposé, en attente de validation du propriétaire.

## Contexte vérifié

Le cahier des charges demande de construire un CORE, des permissions, une mémoire et un journal (étapes 2 à 4),
tout en exigeant d'inspecter avant de reconstruire et de n'avoir qu'un seul moteur (sections 2 et 12).

L'inspection de ce cycle montre que ces étapes existent déjà dans le dépôt SOVEREIGN :

- noyau SQLite, registre financier en ajout seul, bus d'événements persistant, mémoire des décisions ;
- règle des 10 %, validations humaines, aucune approbation exposée aux agents ;
- interfaces CLI, API REST et MCP, file de tâches durable, observateur de dépôts en lecture seule ;
- sur `main` (commit `62ecac3ada8b`) : lint, format et types sans erreur, 291 tests réussis, rejoués ici.

Ce qui n'existe nulle part : le protocole de preuves Ω, un registre d'actifs, la recherche multi-source,
l'orchestration d'agents, l'interface web.

## Trois candidats, sept critères (0 à 5)

| Critère | A. Nouveau moteur autonome dans NOVARYS | B. Couche NOVARYS branchée dans la base de SOVEREIGN | C. SOVEREIGN reste le moteur ; NOVARYS pilote et prouve |
|---|---|---|---|
| Impact | 2 — donne du code à NOVARYS mais double journal, permissions et mémoire | 3 | 4 — chaque capacité revendiquée devient vérifiable |
| Faisabilité | 3 — faisable, mais le noyau existant pèse 20 000 lignes | 2 — une table de preuves exige une migration dans le schéma de SOVEREIGN : deux dépôts à modifier à chaque évolution | 5 — construit et exécuté dans ce cycle |
| Preuve | 1 — rien de prouvé ; abandonne 291 tests réussis | 3 | 4 — 12 preuves consignées, tests de l'outil, relecture indépendante |
| Réutilisation | 1 | 4 | 5 — tout le moteur est repris ; l'outil de preuve sert n'importe quel dépôt |
| Accélération | 1 — refait les étapes 2 à 4 avant d'avancer | 2 | 4 — passe directement aux étapes 5 et suivantes |
| Contrefactuel | 1 — sans lui, ces fonctions existent déjà | 3 | 4 — sans lui, les capacités restent affirmées dans des textes ; le défaut REPLACE restait invisible à 291 tests |
| Résistance à la falsification | 1 — contredit les sections 2 et 12 du cahier des charges | 2 — exécute des commandes de preuve dans le processus qui détient le registre financier et les clés | 4 — attaqué par ses tests et par une relecture indépendante ; limites écrites |
| **Total / 35** | **10** | **19** | **30** |

Éliminés : A, parce qu'il crée une seconde source de vérité ; B, parce qu'il fait tourner du code de preuve à
côté de l'argent et des clés, ce que le moteur s'interdit déjà pour son observateur de dépôts.

## Décision

1. **Le moteur est le code du dépôt SOVEREIGN.** On l'étend, on ne le refait pas.
2. **NOVARYS est le poste de pilotage** : la charte, l'outil de preuve Ω, le référentiel des capacités, le
   registre des preuves, le registre des actifs et le journal des cycles.
3. **L'outil de preuve est un processus séparé**, sans dépendance, qui exécute ses commandes sans les secrets de
   la session et ne touche jamais la base du moteur. Il vise le moteur à un commit épinglé.

## Écarts assumés par rapport au cahier des charges

- Section 2, « aucun assemblage d'applications indépendantes » : l'outil de preuve est volontairement hors du
  processus du moteur, pour la raison de sécurité ci-dessus. Le moteur ne lit pas encore le registre des preuves :
  cette liaison n'est pas faite et n'est pas revendiquée.
- Section 11, « stockage SQLite » : le moteur l'utilise. Le registre des preuves est un fichier texte dans Git,
  parce qu'il doit survivre à des sessions éphémères, se relire dans une PR et se vérifier par un tiers.
- Section 13, missions et cycles bornés : tenus dans `journal/`, à la main. Aucun code ne les impose.

## Ce qui prouverait que cette décision est mauvaise

À réexaminer si l'un de ces faits se produit :

- une preuve a besoin d'écrire dans la base du moteur pour être faite ;
- plus de deux changements coordonnés entre les deux dépôts sont nécessaires dans un même cycle ;
- le propriétaire veut un seul dépôt et un seul nom.

## Décisions qui restent au propriétaire

- **Visibilité des dépôts.** NOVARYS public : aucune donnée privée ne peut y être mémorisée. SOVEREIGN public :
  son cycle quotidien refuse de s'exécuter.
- **Nom du moteur.** Le code s'appelle `sovereign`. Le renommer ou le déplacer change l'identité d'un dépôt :
  ce n'est pas fait ici.
- **Hive.** Il recouvre le moteur sur l'orchestration d'agents : en faire la brique AGENTS, ou le geler.
