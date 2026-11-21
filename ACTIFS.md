# Actifs existants : état réel et prochaine action rentable

> Fichier généré par `omega render` à partir de `registre/actifs.toml`. Ne pas le modifier à la main.
> Ce registre est public : il ne décrit que des dépôts publics, sans donnée personnelle.

| Actif | État réel | Blocages | Prochaine action rentable |
|---|---|---|---|
| **Alll** — L'histoire de votre maison, livret personnalisé à 29 € | Chaîne commande, fabrication, envoi écrite et testée (2 289 lignes, 38 cas de test, 2 workflows). Site non mis en ligne, lien de paiement non configuré (A_REMPLACER), pages légales à compléter. 0 vente. | Actions réservées au propriétaire : rendre le dépôt privé, statut pour facturer (préalable commun avec Velyx), médiateur, boîte d'envoi, Cloudflare, Stripe, pages légales. Environ 2 heures selon docs/MISE-EN-ROUTE.md. | Décision datée : pour vendre avant le 20/12/2026 (critère d'arrêt du dépôt : moins de 30 commandes pour environ 1 000 visites), le statut doit être déposé dans les jours qui viennent, le numéro d'entreprise mettant environ deux semaines selon le dépôt. Puis session 1 de docs/MISE-EN-ROUTE.md, environ 1 heure. |
| **Velyx-prospection-** — VELYX, fichiers de prospection fondés sur des signaux publics | Offre préparée : entreprises du bâtiment immatriculées récemment, pour des courtiers en assurance construction. État du dépôt au 16/11/2026 : 0 envoi, 0 € encaissé. Quatre gestes en attente, tous à faire par le propriétaire : statut pour facturer, ouverture d'un canal, publication du service, envoi de la première proposition (4 cabinets d'un département). | Statut pour facturer non confirmé : préalable commun avec Alll. Les brouillons privés du 16/11/2026 (fiche et message pour les 4 cabinets) ne sont ni dans le dépôt ni retrouvés ailleurs : à régénérer. Le registre public ne donne ni e-mail ni téléphone des cabinets : à trouver par le propriétaire. Aucun message ne part sans lui. | Propriétaire : déposer le statut (gratuit, 20 à 30 minutes selon docs/statut-micro-entreprise.md du dépôt). Agent, sur accord : régénérer la fiche des 4 cabinets et le brouillon de message. C'est le chemin le plus court vers un premier encaissement sans dépense préalable. |
| **Ref** — NOVARYS OMNISEARCH, conformité des droits face aux IA | Moteur construit (3 509 lignes, 63 cas de test), études sur données réelles, dossier de pilote complet. Tous les messages sont des brouillons non envoyés. Pas de CI. 0 client. | Aucun contact pris : la validation par un client exige l'envoi des messages par le propriétaire. Cycle de vente long. Son paquet Python s'appelle aussi « novarys ». | Relire docs/pilote/MESSAGES.md et envoyer une première demande de pilote. Ajouter une CI, gratuite sur un dépôt public. |
| **Paie-juste** — Paie Juste, vérifier sa paie hors ligne | Application installable, hors ligne, sans compte, sous licence MIT. 8 349 lignes, 27 cas de test, 2 workflows. 4 PR de mises à jour de dépendances ouvertes. | Aucun modèle de revenu : l'application est gratuite et libre. Audience non mesurée. | Mesurer l'usage avant toute décision (compteur sans cookie). Sans audience mesurée, aucune action rentable identifiée. |
| **Clip-preuve** — Clip-preuve, un clip vertical et sa carte de preuve | Outil local sous licence MIT : un lien vidéo donne un clip de 20 à 90 secondes et une carte de preuve. 4 761 lignes, 121 cas de test, 1 workflow. 1 PR de dépendances ouverte. | Outil en ligne de commande à installer. Ni offre, ni service hébergé, ni utilisateur connu. | Aucune action rentable sans test de demande. Piste à 0 € : proposer le service à la pièce, à la main, à quelques créateurs. |
| **Jeun** — MULTIVERSE, plusieurs VOD d'un même événement sur une horloge commune | Outil en ligne. 935 lignes, 7 cas de test, 2 workflows. | Le test de 7 jours prévu par le dépôt ne peut pas être mesuré : le compteur de visites gratuit n'est pas activé, il faut un compte créé par le propriétaire. Pas de modèle de revenu. | Activer le compteur, puis lancer le test de 7 jours (seuil du dépôt : 30 visiteurs inconnus et 3 liens créés par d'autres). |
| **Toon-o-Matic** — Toon-o-Matic, usine de web-série animée | Chaîne écriture, voix, animation, montage, revue humaine. 8 396 lignes, 70 cas de test, 1 workflow. | La production réelle demande une dépense, refusée tant que rien n'est encaissé. Les revenus de plateformes vidéo supposent des seuils d'audience. | Aucune à 0 € au-delà du mode simulé. À reprendre quand une enveloppe de dépense existera. |
| **Hive** — HIVE, colonie d'agents sous contrôle humain | Agents coordonnés par traces sur un tableau commun. 7 106 lignes, 54 cas de test, pas de CI. Feuille de route du dépôt : jours 2 à 7 « à faire ». | Aucun modèle de langage branché (jour 2 de sa feuille de route). Pas d'offre. | Aucune action rentable directe. Décision à prendre : en faire la brique AGENTS du moteur, ou le geler. |
| **SOVEREIGN** — Le moteur : noyau, registre financier, mémoire, validations humaines | Moteur de NOVARYS : base SQLite, règle des 10 %, mémoire des décisions, CLI, API REST, serveur MCP. 20 081 lignes, 238 cas de test relevés par l'observateur, 2 workflows. Aucune donnée d'entreprise chargée. | Défaut trouvé ce cycle : registre financier et audit réécrivables par INSERT OR REPLACE (correctif proposé en PR). Le cycle quotidien n'exécute plus rien depuis le 18/11/2026 parce que le dépôt est public. | Fusionner le correctif, décider de la visibilité du dépôt pour relancer le cycle quotidien, puis y enregistrer le premier encaissement réel quand il existera. |
| **NOVARYS** — Ce dépôt : charte, protocole de preuves Ω, registres | Outil de preuves, référentiel des capacités, registre des preuves et registre des actifs. Créé dans ce cycle. | Dépôt public : aucune donnée privée ne peut y être mémorisée. La CI n'écrit pas encore au registre (niveau VALIDÉ inatteignable). | Faire de la CI le second acteur du registre ; décider de la visibilité du dépôt. |
| **Tr** — Page de travail commune de GALILÉE, CORTEX et LAVOISIER | Trois moteurs de recherche réunis autour d'un journal commun, avec leurs échecs publiés. 8 243 lignes, 53 cas de test, pas de CI. Recouvre à 90 % les dépôts 1, A et All selon l'observateur. | Recherche sans offre ni utilisateur. Quatre dépôts pour le même code. | Aucune action rentable identifiée. Garder Tr comme référence et archiver les trois copies réduirait la dispersion : décision du propriétaire. |
| **1** — CORTEX, boucle cognitive qui pilote une activité inconnue | 8 297 lignes, 34 cas de test, pas de CI. Repris dans Tr. | Recherche sur simulation. Pas d'offre. | Aucune. Voir Tr. |
| **All** — Galilée, agent scientifique qui retrouve une loi cachée | 3 755 lignes, 29 cas de test, pas de CI. Repris dans Tr. | Recherche sur simulation. Pas d'offre. | Aucune. Voir Tr. |
| **A** — LAVOISIER, reconstruire les comptes d'une entreprise opaque | 2 408 lignes, 34 cas de test, pas de CI. Premier jalon en cours selon le dépôt. Repris dans Tr. | Recherche à son premier jalon. Pas d'offre. | Aucune. Voir Tr. |
| **MONDO** — MONDO, document de stratégie | Deux fichiers, aucun code. Nom de travail dont la disponibilité juridique n'est pas vérifiée, selon le dépôt. | Idée sans prototype. | Aucune action rentable identifiée. |
| **Artiste-** — Document fondateur d'un projet musical | Quatre fichiers, version 0.1. Rien n'est publié ni déposé, selon le dépôt. | Projet créatif à l'état de document. | Aucune action rentable identifiée dans ce cycle. |

## Alll — L'histoire de votre maison, livret personnalisé à 29 €

Observé le 2026-11-21, commit `b998e46909ca`.

- **Localisation** : github.com/haynbroit-alt/Alll, dépôt public.
- **Accès** : Lecture seule depuis cette session.
- **État réel** : Chaîne commande, fabrication, envoi écrite et testée (2 289 lignes, 38 cas de test, 2 workflows). Site non mis en ligne, lien de paiement non configuré (A_REMPLACER), pages légales à compléter. 0 vente.
- **Fonctions démontrées** : Génération d'un livret réel (exemple d'Amiens dans le dépôt). Le dépôt déclare 13 commandes de test réelles en novembre 2026.
- **Dépendances** : Données ouvertes (IGN, Base Adresse Nationale, cadastre, BDNB, Wikipédia), GitHub Actions, Stripe, Cloudflare, une boîte d'envoi.
- **Coûts** : 0 € de frais fixes. Avant la première vente : adhésion à un médiateur de la consommation, environ 48 € pour 3 ans selon le dépôt (décision du propriétaire). Commission Stripe par vente.
- **Réutilisation** : Le relais paiement, fabrication, envoi est réutilisable pour tout produit numérique personnalisé. Le moteur sait déjà transformer un paiement Stripe signé en encaissement.
- **Preuves** : Tests et exemple présents dans le dépôt, non rejoués dans ce cycle. Risque noté par le dépôt : fabriquer des commandes clients dans GitHub Actions est une zone grise de ses conditions d'utilisation.
- **Blocages** : Actions réservées au propriétaire : rendre le dépôt privé, statut pour facturer (préalable commun avec Velyx), médiateur, boîte d'envoi, Cloudflare, Stripe, pages légales. Environ 2 heures selon docs/MISE-EN-ROUTE.md.
- **Prochaine action rentable** : Décision datée : pour vendre avant le 20/12/2026 (critère d'arrêt du dépôt : moins de 30 commandes pour environ 1 000 visites), le statut doit être déposé dans les jours qui viennent, le numéro d'entreprise mettant environ deux semaines selon le dépôt. Puis session 1 de docs/MISE-EN-ROUTE.md, environ 1 heure.

## Velyx-prospection- — VELYX, fichiers de prospection fondés sur des signaux publics

Observé le 2026-11-21, commit `08edccb3eb2d`.

- **Localisation** : github.com/haynbroit-alt/Velyx-prospection-, dépôt public.
- **Accès** : Lecture seule depuis cette session.
- **État réel** : Offre préparée : entreprises du bâtiment immatriculées récemment, pour des courtiers en assurance construction. État du dépôt au 16/11/2026 : 0 envoi, 0 € encaissé. Quatre gestes en attente, tous à faire par le propriétaire : statut pour facturer, ouverture d'un canal, publication du service, envoi de la première proposition (4 cabinets d'un département).
- **Fonctions démontrées** : Cycle quotidien sur données réelles (demandes publiées, registre des entreprises), registre chaîné SHA-256. 15 281 lignes, 273 cas de test, 1 workflow.
- **Dépendances** : Node 20 ou plus, aucune dépendance. Sources publiques.
- **Coûts** : 0 € (mandat du dépôt : aucune dépense avant le premier encaissement).
- **Réutilisation** : Mêmes principes que le moteur : registre chaîné, porte réseau à liste blanche, file de revue humaine. Les recettes déclaratives se réutilisent pour d'autres zones et d'autres métiers.
- **Preuves** : 230 tests déclarés par le README, non rejoués : l'exécution du code de ce dépôt a été refusée dans cette session. Volume annoncé par le dépôt : environ 5 sociétés à signaler par mois et par département. Taux de réponse : INCONNU, aucun envoi.
- **Blocages** : Statut pour facturer non confirmé : préalable commun avec Alll. Les brouillons privés du 16/11/2026 (fiche et message pour les 4 cabinets) ne sont ni dans le dépôt ni retrouvés ailleurs : à régénérer. Le registre public ne donne ni e-mail ni téléphone des cabinets : à trouver par le propriétaire. Aucun message ne part sans lui.
- **Prochaine action rentable** : Propriétaire : déposer le statut (gratuit, 20 à 30 minutes selon docs/statut-micro-entreprise.md du dépôt). Agent, sur accord : régénérer la fiche des 4 cabinets et le brouillon de message. C'est le chemin le plus court vers un premier encaissement sans dépense préalable.

## Ref — NOVARYS OMNISEARCH, conformité des droits face aux IA

Observé le 2026-11-21, commit `7753dd034a4b`.

- **Localisation** : github.com/haynbroit-alt/Ref, dépôt public.
- **Accès** : Lecture seule depuis cette session.
- **État réel** : Moteur construit (3 509 lignes, 63 cas de test), études sur données réelles, dossier de pilote complet. Tous les messages sont des brouillons non envoyés. Pas de CI. 0 client.
- **Fonctions démontrées** : Compilation d'une politique en signaux lisibles par les IA, audit, vérification de journaux. Le pilote est répété de bout en bout sur données synthétiques.
- **Dépendances** : Python 3.10 ou plus, aucune dépendance.
- **Coûts** : 0 €.
- **Réutilisation** : Registre de preuves infalsifiable et tests d'affirmations : même idée que le protocole Ω de ce dépôt.
- **Preuves** : Le rapport de recherche du dépôt conclut à un « GO limité » : la preuve commerciale n'est qu'indirecte. Tests non rejoués dans ce cycle.
- **Blocages** : Aucun contact pris : la validation par un client exige l'envoi des messages par le propriétaire. Cycle de vente long. Son paquet Python s'appelle aussi « novarys ».
- **Prochaine action rentable** : Relire docs/pilote/MESSAGES.md et envoyer une première demande de pilote. Ajouter une CI, gratuite sur un dépôt public.

## Paie-juste — Paie Juste, vérifier sa paie hors ligne

Observé le 2026-11-21, commit `574bd8b08ef1`.

- **Localisation** : github.com/haynbroit-alt/Paie-juste, dépôt public. Application en ligne sur GitHub Pages.
- **Accès** : Lecture seule depuis cette session.
- **État réel** : Application installable, hors ligne, sans compte, sous licence MIT. 8 349 lignes, 27 cas de test, 2 workflows. 4 PR de mises à jour de dépendances ouvertes.
- **Fonctions démontrées** : Pointage, estimation de la paie selon le droit du travail français, comparaison au bulletin, lettre de réclamation (captures dans le dépôt).
- **Dépendances** : Un navigateur. pdf.js et tesseract.js embarqués.
- **Coûts** : 0 €.
- **Réutilisation** : Chaîne d'empreintes SHA-256 côté client ; modèle d'application hors ligne.
- **Preuves** : Tests présents dans le dépôt, non rejoués dans ce cycle. Nombre d'utilisateurs : INCONNU, aucune mesure d'audience vue.
- **Blocages** : Aucun modèle de revenu : l'application est gratuite et libre. Audience non mesurée.
- **Prochaine action rentable** : Mesurer l'usage avant toute décision (compteur sans cookie). Sans audience mesurée, aucune action rentable identifiée.

## Clip-preuve — Clip-preuve, un clip vertical et sa carte de preuve

Observé le 2026-11-21, commit `541c1dc367a3`.

- **Localisation** : github.com/haynbroit-alt/Clip-preuve, dépôt public.
- **Accès** : Lecture seule depuis cette session.
- **État réel** : Outil local sous licence MIT : un lien vidéo donne un clip de 20 à 90 secondes et une carte de preuve. 4 761 lignes, 121 cas de test, 1 workflow. 1 PR de dépendances ouverte.
- **Fonctions démontrées** : Chaîne complète avec un modèle local sur processeur (démonstration et exemples dans le dépôt).
- **Dépendances** : Linux, ffmpeg, Python 3.11 ou plus, llama.cpp et un modèle local ; 16 dépendances.
- **Coûts** : 0 € avec le modèle local. Temps de calcul par vidéo : INCONNU.
- **Réutilisation** : Son « Falsificateur » applique déjà les statuts PROUVÉ, INCONNU, CONFLIT à un contenu.
- **Preuves** : Exemples de cartes de preuve dans le dépôt. Tests non rejoués dans ce cycle.
- **Blocages** : Outil en ligne de commande à installer. Ni offre, ni service hébergé, ni utilisateur connu.
- **Prochaine action rentable** : Aucune action rentable sans test de demande. Piste à 0 € : proposer le service à la pièce, à la main, à quelques créateurs.

## Jeun — MULTIVERSE, plusieurs VOD d'un même événement sur une horloge commune

Observé le 2026-11-21, commit `e427e9314584`.

- **Localisation** : github.com/haynbroit-alt/Jeun, dépôt public. Outil en ligne sur GitHub Pages.
- **Accès** : Lecture seule depuis cette session.
- **État réel** : Outil en ligne. 935 lignes, 7 cas de test, 2 workflows.
- **Fonctions démontrées** : Un exemple public prêt à l'emploi (trois VOD synchronisées).
- **Dépendances** : Un navigateur ; les lecteurs YouTube et Twitch.
- **Coûts** : 0 €.
- **Réutilisation** : INCONNU.
- **Preuves** : L'étude d'opportunités du dépôt présente ses chiffres d'audience comme des hypothèses, pas des mesures.
- **Blocages** : Le test de 7 jours prévu par le dépôt ne peut pas être mesuré : le compteur de visites gratuit n'est pas activé, il faut un compte créé par le propriétaire. Pas de modèle de revenu.
- **Prochaine action rentable** : Activer le compteur, puis lancer le test de 7 jours (seuil du dépôt : 30 visiteurs inconnus et 3 liens créés par d'autres).

## Toon-o-Matic — Toon-o-Matic, usine de web-série animée

Observé le 2026-11-21, commit `1aa8c329bff0`.

- **Localisation** : github.com/haynbroit-alt/Toon-o-Matic, dépôt public.
- **Accès** : Lecture seule depuis cette session.
- **État réel** : Chaîne écriture, voix, animation, montage, revue humaine. 8 396 lignes, 70 cas de test, 1 workflow.
- **Fonctions démontrées** : La chaîne complète en mode simulé, sans carte graphique ni clé. Production d'un épisode réel : INCONNU.
- **Dépendances** : Blender, un moteur vocal, un modèle de langage, un stockage objet, une carte graphique louée pour le rendu final.
- **Coûts** : 0 € en mode simulé. Rendu final : carte graphique louée, coût non chiffré ici, bloqué par défaut sans accord.
- **Réutilisation** : Revue humaine Valider, Refaire, Rejeter ; fournisseurs interchangeables.
- **Preuves** : Tests du dépôt, non rejoués dans ce cycle.
- **Blocages** : La production réelle demande une dépense, refusée tant que rien n'est encaissé. Les revenus de plateformes vidéo supposent des seuils d'audience.
- **Prochaine action rentable** : Aucune à 0 € au-delà du mode simulé. À reprendre quand une enveloppe de dépense existera.

## Hive — HIVE, colonie d'agents sous contrôle humain

Observé le 2026-11-21, commit `8b552da54e4a`.

- **Localisation** : github.com/haynbroit-alt/Hive, dépôt public.
- **Accès** : Lecture seule depuis cette session.
- **État réel** : Agents coordonnés par traces sur un tableau commun. 7 106 lignes, 54 cas de test, pas de CI. Feuille de route du dépôt : jours 2 à 7 « à faire ».
- **Fonctions démontrées** : Selon le README : une démonstration locale produit et contrôle deux vidéos de 30 secondes, registre chaîné vérifié.
- **Dépendances** : Python 3.11 ou plus, sans dépendance ; ffmpeg et espeak-ng optionnels.
- **Coûts** : 0 €.
- **Réutilisation** : Recouvre le moteur sur l'orchestration d'agents et la validation humaine : candidat pour le domaine AGENTS plutôt que second moteur.
- **Preuves** : Auto-test « 12 garde-fous sur 12 » déclaré par le README, non rejoué.
- **Blocages** : Aucun modèle de langage branché (jour 2 de sa feuille de route). Pas d'offre.
- **Prochaine action rentable** : Aucune action rentable directe. Décision à prendre : en faire la brique AGENTS du moteur, ou le geler.

## SOVEREIGN — Le moteur : noyau, registre financier, mémoire, validations humaines

Observé le 2026-11-21, commit `62ecac3ada8b`.

- **Localisation** : github.com/haynbroit-alt/SOVEREIGN, dépôt public.
- **Accès** : Lecture et écriture sur une branche de travail ; fusion par le propriétaire.
- **État réel** : Moteur de NOVARYS : base SQLite, règle des 10 %, mémoire des décisions, CLI, API REST, serveur MCP. 20 081 lignes, 238 cas de test relevés par l'observateur, 2 workflows. Aucune donnée d'entreprise chargée.
- **Fonctions démontrées** : Voir CAPACITES.md : le moteur est le sujet des preuves de ce dépôt.
- **Dépendances** : Python 3.12 ou plus, 9 dépendances verrouillées.
- **Coûts** : 0 €.
- **Réutilisation** : Sert tout le portefeuille : observation des dépôts, contrôle des dépenses, encaissement à partir d'un paiement Stripe signé.
- **Preuves** : registre/preuves.jsonl de ce dépôt ; 291 tests réussis sur main dans ce cycle.
- **Blocages** : Défaut trouvé ce cycle : registre financier et audit réécrivables par INSERT OR REPLACE (correctif proposé en PR). Le cycle quotidien n'exécute plus rien depuis le 18/11/2026 parce que le dépôt est public.
- **Prochaine action rentable** : Fusionner le correctif, décider de la visibilité du dépôt pour relancer le cycle quotidien, puis y enregistrer le premier encaissement réel quand il existera.

## NOVARYS — Ce dépôt : charte, protocole de preuves Ω, registres

Observé le 2026-11-21.

- **Localisation** : github.com/haynbroit-alt/NOVARYS, dépôt public.
- **Accès** : Lecture et écriture sur une branche de travail ; fusion par le propriétaire.
- **État réel** : Outil de preuves, référentiel des capacités, registre des preuves et registre des actifs. Créé dans ce cycle.
- **Fonctions démontrées** : Voir CAPACITES.md, domaine OMEGA.
- **Dépendances** : Python 3.12 ou plus, bibliothèque standard seulement ; le moteur pour exécuter ses preuves.
- **Coûts** : 0 €.
- **Réutilisation** : L'outil de preuve s'applique à n'importe quel dépôt du portefeuille : un référentiel, des commandes, un registre.
- **Preuves** : registre/preuves.jsonl ; tests de l'outil.
- **Blocages** : Dépôt public : aucune donnée privée ne peut y être mémorisée. La CI n'écrit pas encore au registre (niveau VALIDÉ inatteignable).
- **Prochaine action rentable** : Faire de la CI le second acteur du registre ; décider de la visibilité du dépôt.

## Tr — Page de travail commune de GALILÉE, CORTEX et LAVOISIER

Observé le 2026-11-21, commit `67a043cfd198`.

- **Localisation** : github.com/haynbroit-alt/Tr, dépôt public.
- **Accès** : Lecture seule depuis cette session.
- **État réel** : Trois moteurs de recherche réunis autour d'un journal commun, avec leurs échecs publiés. 8 243 lignes, 53 cas de test, pas de CI. Recouvre à 90 % les dépôts 1, A et All selon l'observateur.
- **Fonctions démontrées** : Selon le dépôt : découverte de lois cachées, pilotage d'une activité inconnue, reconstruction de comptes, sur des bancs d'essai simulés.
- **Dépendances** : Node, sans dépendance.
- **Coûts** : 0 €.
- **Réutilisation** : Discipline commune : protocole avant le code, graines réservées, échecs publiés.
- **Preuves** : Bancs d'essai du dépôt, non rejoués dans ce cycle.
- **Blocages** : Recherche sans offre ni utilisateur. Quatre dépôts pour le même code.
- **Prochaine action rentable** : Aucune action rentable identifiée. Garder Tr comme référence et archiver les trois copies réduirait la dispersion : décision du propriétaire.

## 1 — CORTEX, boucle cognitive qui pilote une activité inconnue

Observé le 2026-11-21, commit `8825007b1c06`.

- **Localisation** : github.com/haynbroit-alt/1, dépôt public.
- **Accès** : Lecture seule depuis cette session.
- **État réel** : 8 297 lignes, 34 cas de test, pas de CI. Repris dans Tr.
- **Fonctions démontrées** : Selon le dépôt : un agent dirige un commerce simulé sans savoir lequel, résultats et verdicts publiés dans bench/.
- **Dépendances** : Node, sans dépendance.
- **Coûts** : 0 €.
- **Réutilisation** : La boucle Observer, Confronter, Décider, Mesurer est celle du directeur du moteur.
- **Preuves** : Bancs d'essai du dépôt, non rejoués dans ce cycle.
- **Blocages** : Recherche sur simulation. Pas d'offre.
- **Prochaine action rentable** : Aucune. Voir Tr.

## All — Galilée, agent scientifique qui retrouve une loi cachée

Observé le 2026-11-21, commit `58e25ca8163a`.

- **Localisation** : github.com/haynbroit-alt/All, dépôt public.
- **Accès** : Lecture seule depuis cette session.
- **État réel** : 3 755 lignes, 29 cas de test, pas de CI. Repris dans Tr.
- **Fonctions démontrées** : Selon le dépôt : choix des expériences, confrontation aux mesures, verdict gradué, échecs listés dans bench/RESULTS.md.
- **Dépendances** : Node, sans dépendance.
- **Coûts** : 0 €.
- **Réutilisation** : Verdict gradué (établie, empirique, hypothèse) proche des statuts Ω.
- **Preuves** : Bancs d'essai du dépôt, non rejoués dans ce cycle.
- **Blocages** : Recherche sur simulation. Pas d'offre.
- **Prochaine action rentable** : Aucune. Voir Tr.

## A — LAVOISIER, reconstruire les comptes d'une entreprise opaque

Observé le 2026-11-21, commit `38b957822c7d`.

- **Localisation** : github.com/haynbroit-alt/A, dépôt public.
- **Accès** : Lecture seule depuis cette session.
- **État réel** : 2 408 lignes, 34 cas de test, pas de CI. Premier jalon en cours selon le dépôt. Repris dans Tr.
- **Fonctions démontrées** : Selon le dépôt : banc d'essai du premier jalon écrit ; première version du bilan de matière en développement.
- **Dépendances** : Node, sans dépendance.
- **Coûts** : 0 €.
- **Réutilisation** : INCONNU.
- **Preuves** : Banc d'essai du dépôt, non rejoué dans ce cycle.
- **Blocages** : Recherche à son premier jalon. Pas d'offre.
- **Prochaine action rentable** : Aucune. Voir Tr.

## MONDO — MONDO, document de stratégie

Observé le 2026-11-21, commit `f1c055390bc6`.

- **Localisation** : github.com/haynbroit-alt/MONDO, dépôt public.
- **Accès** : Lecture seule depuis cette session.
- **État réel** : Deux fichiers, aucun code. Nom de travail dont la disponibilité juridique n'est pas vérifiée, selon le dépôt.
- **Fonctions démontrées** : Rien : c'est un document.
- **Dépendances** : Aucune.
- **Coûts** : 0 €.
- **Réutilisation** : INCONNU.
- **Preuves** : Aucune.
- **Blocages** : Idée sans prototype.
- **Prochaine action rentable** : Aucune action rentable identifiée.

## Artiste- — Document fondateur d'un projet musical

Observé le 2026-11-21, commit `79ea5154f1dd`.

- **Localisation** : github.com/haynbroit-alt/Artiste-, dépôt public.
- **Accès** : Lecture seule depuis cette session.
- **État réel** : Quatre fichiers, version 0.1. Rien n'est publié ni déposé, selon le dépôt.
- **Fonctions démontrées** : Rien : c'est un document de travail.
- **Dépendances** : Aucune.
- **Coûts** : 0 €.
- **Réutilisation** : INCONNU.
- **Preuves** : Aucune.
- **Blocages** : Projet créatif à l'état de document.
- **Prochaine action rentable** : Aucune action rentable identifiée dans ce cycle.
