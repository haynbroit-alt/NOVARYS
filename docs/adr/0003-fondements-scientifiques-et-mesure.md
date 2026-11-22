# ADR 0003 — Fondements scientifiques : ce qui existe, ce qui se mesure, ce qui attend un besoin

Date : 22/11/2026. Statut : proposé, en attente de validation du propriétaire.

## Contexte

Le propriétaire demande un noyau « VELYX Ω » fondé sur six familles de méthodes, où chaque décision est
mesurable, chaque action traçable, chaque résultat vérifiable et chaque apprentissage réversible, sans jamais
annoncer d'autonomie non mesurée. Cette demande recouvre le cahier des charges existant (sections 9, 10, 11 et
14). Elle ne crée pas un nouveau système : l'ADR 0001 garde un seul moteur. Elle ajoute une exigence utile, que
cet ADR fixe : dire, pour chaque famille, ce qui est prouvé, ce qui est absent, et à quelle mesure on le saura.

État de départ, lu dans `CAPACITES.md` : NOVARYS n'est pas opérationnel, 16 fonctions sur 25 sont sous le niveau
TESTÉ. Encaissement : 0 €.

## Les six familles face à l'existant

| Famille demandée | Ce qui existe | État |
|---|---|---|
| Cryptographie, isolation, preuves d'intégrité | Registres en ajout seul chaînés en SHA-256 (ce dépôt, le moteur, Velyx) ; commandes de preuve exécutées sans secrets | PROUVÉ sur données de test (`registre-ajout-seul`, `outil-de-preuve`, attaques résistées). Pas de signature : l'identité d'un acteur reste une déclaration. |
| Empêcher les actions non autorisées | Dépense refusée sans encaissement ; aucune approbation possible par un agent ; actions sensibles d'OMNIA soumises au propriétaire | PROUVÉ par tests et attaques (`depense-sans-encaissement-refusee`, `aucune-approbation-par-agent`). Ce sont des tests, pas une vérification formelle. |
| Méthodes formelles, vérification automatisée | Aucun modèle formel, aucun prouveur | ABSENT. Les invariants sont éprouvés par des tests et des sondes d'attaque. |
| Multi-agents, graphes, systèmes complexes | Répartition de missions dans le moteur ; colonie par traces de Hive | CONNECTÉ pour la répartition (`repartition-missions-agents`). Orchestration réelle ABSENTE ; Hive n'a aucun modèle branché. |
| Probabilités, inférence, raisonnement sous incertitude | Moteurs de recherche de l'espace commun (Tr) : choix d'expériences, révision de croyances, évaluations pré-enregistrées | Démontré en simulation seulement, échecs publiés compris. Aucun usage sur une donnée réelle de l'écosystème. |
| Optimisation, recherche opérationnelle, théorie des jeux | Classement des missions sur six critères notés à la main (ADR 0002) | ABSENT comme méthode. |
| Contrôle adaptatif, détection d'anomalies, apprentissage | Poids des règles ajustés selon les décisions acceptées, dans OMNIA | Écrit et testé dans OMNIA ; réversibilité non éprouvée. Détection d'anomalies ABSENTE. |

## Indicateurs

Chacun se calcule depuis les registres, par une commande rejouable, jamais à la main.

| Indicateur | Définition | Valeur au 22/11/2026 |
|---|---|---|
| Autonomie | Sur une période : actions utiles menées à terme sans geste du propriétaire, divisées par toutes les actions utiles menées à terme. Une action « utile » change un indicateur économique ou livre un résultat vérifié. | NON MESURÉ. Aucune commande ne le calcule, et le dénominateur économique est nul. |
| Traçabilité | Part des actions exécutées qui ont une ligne chaînée dans un registre. | Vérifiée pour ce dépôt (`omega check`). Non mesurée pour l'ensemble. |
| Vérifiabilité | Part des fonctions au niveau TESTÉ ou au-dessus. | 9 sur 25. |
| Réversibilité | Part des apprentissages (poids, règles, croyances) qu'une commande ramène à l'état précédent, à l'identique. | NON MESURÉ. |
| Économie | Euros encaissés et vérifiés. | 0 €. |

Règle : aucun pourcentage d'autonomie n'est écrit, affiché ou dit tant que l'indicateur n'est pas calculé par
une commande inscrite au référentiel et rejouée par un second acteur.

## Expériences falsifiables

| N° | Hypothèse | Ce qui la réfute | État |
|---|---|---|---|
| E1 | Un registre falsifié est toujours refusé. | Une falsification acceptée par `omega check`. | Tentée trois fois par preuve, résistée. |
| E2 | Aucun agent ne peut approuver une dépense ni déclarer un encaissement. | Un outil exposé qui le permet. | Tentée, résistée. |
| E3 | Un apprentissage annulé rend exactement l'état précédent. | Un écart après annulation. | À construire quand un apprentissage tournera sur des données réelles. |
| E4 | Coordonner deux projets fait mieux que les conduire séparément. | Sur des résultats mis de côté, pas d'écart ou un écart négatif. | À construire quand deux projets produiront des résultats mesurables. |
| E5 | L'autonomie mesurée par l'agent et par un second acteur concordent. | Deux valeurs différentes pour la même période. | À construire avec l'indicateur. |

## Décision

1. Pas de nouveau noyau. Le moteur reste SOVEREIGN, la mémoire NOVARYS, l'application de travail OMNIA.
2. Une méthode n'entre que lorsqu'un besoin mesuré l'appelle, avec son expérience et son attaque. Arbitrer des
   ressources par théorie des jeux, optimiser un portefeuille ou détecter des anomalies n'a pas d'objet tant
   qu'il n'y a ni ressource à répartir, ni revenu, ni flux de données réelles : ces familles restent ABSENTES et
   sont dites telles.
3. Le premier ajout justifié est l'indicateur d'autonomie, parce qu'il empêche une affirmation fausse. Il se
   construit dès qu'une action utile existe à compter, c'est-à-dire après le premier envoi ou le premier
   encaissement.
4. L'ordre des priorités de l'ADR 0002 ne change pas : le premier encaissement d'abord.

## Conséquence

Ce document ne livre aucune capacité. Il empêche d'en revendiquer une qui n'existe pas, et fixe à quoi l'on
reconnaîtra qu'elle existe.
