# NOVARYS Ω — cahier des charges fondateur (version compacte)

> Texte du propriétaire, reçu le 21/11/2026. Il fait référence : `registre/capacites.toml` en reprend les
> exigences une à une. Seule modification : dans la section 12, les noms d'actifs qui ne figurent dans aucun
> dépôt public ont été retirés, parce que ce dépôt est public.

## 1. Mission

NOVARYS est un moteur unifié d'intelligence, de recherche, d'invention, d'ingénierie, d'automatisation et de
production économique.

Mission permanente :

DÉCOUVRIR → COMPRENDRE → INVENTER → DÉCIDER → CONSTRUIRE → TESTER → CORRIGER → PRODUIRE → DISTRIBUER → VENDRE →
ENCAISSER → MESURER → APPRENDRE → RÉINVESTIR → PROGRESSER.

Objectif : transformer les possibilités en résultats réels, utiles, vérifiables et rentables.

## 2. Un seul moteur

Un CORE central, une mémoire, une orchestration, une source de vérité, un système de permissions et un protocole
de preuve.

Capacités intégrées :

- CORE : compréhension, planification, décision et coordination.
- INTELLIGENCE : raisonnement, analyse et résolution de problèmes.
- DISCOVERY : exploration, innovations et opportunités.
- INTERNET : recherche et collecte multi-sources.
- ENGINEERING : conception, programmation, tests et maintenance.
- BUSINESS : produits, clients, ventes, encaissements et rentabilité.
- AGENTS : spécialistes collaborant sous contrôle commun.
- MEMORY : mémoire persistante, apprentissage et continuation.
- Ω : vérification, falsification et audit.
- SOVEREIGN : autorité humaine et sécurité.

Ces capacités partagent les mêmes données, missions, identifiants, événements et permissions. Aucun assemblage
artificiel d'applications indépendantes.

## 3. Intelligence et recherche

Comprendre des objectifs complexes, décomposer les problèmes, comparer les hypothèses, détecter les
contradictions, rechercher les solutions existantes et concevoir des alternatives.

Explorer les sources accessibles : Web, moteurs de recherche, GitHub, Reddit, YouTube, TikTok, Instagram,
Facebook, LinkedIn, X, publications scientifiques et documentations.

Capacités : recherche parallèle et multilingue, lecture de pages et documents, extraction, déduplication,
vérification croisée, fraîcheur, fiabilité, citations, cache et reprise.

Chaque information conserve sa source, sa date, sa méthode et son niveau de confiance.

Aucun contournement de sécurité, accès privé non autorisé ou contenu externe traité comme instruction système.

## 4. Invention et opportunités

Détecter des problèmes, besoins, marchés, innovations, produits, automatisations et possibilités économiques.

Pour les décisions importantes : comparer trois candidats, noter sept critères (impact, faisabilité, preuve,
réutilisation, accélération, contrefactuel, résistance à la falsification), éliminer les solutions faibles et
justifier le choix.

Aucune nouveauté, demande commerciale ou supériorité déclarée sans recherche comparative.

## 5. Ingénierie et production

Inspecter les projets autorisés, comprendre leur architecture, écrire et modifier le code, exécuter les tests,
déboguer, sécuriser, optimiser, versionner et livrer.

Cycle obligatoire :

PROBLÈME → RECHERCHE → SPÉCIFICATION → ARCHITECTURE → CODE → TESTS → ATTAQUE → CORRECTION → AUDIT → LIVRAISON.

Tester les cas nominaux, invalides, limites, adversariaux, intégration, sécurité et régression.

## 6. Agents et fournisseurs

Orchestrer des agents spécialisés en recherche, science, programmation, sécurité, économie, marketing, analyse
et audit.

Chaque agent possède une mission, des outils, des entrées/sorties, des permissions et des limites.

Les agents peuvent travailler en parallèle, se contredire et proposer des alternatives. Le CORE tranche selon
les preuves.

Claude, Grok, OpenAI et autres modèles sont des fournisseurs interchangeables, jamais des autorités absolues.

## 7. Mémoire et auto-évolution

Conserver durablement missions, projets, décisions, architectures, sources, erreurs, tests, preuves, résultats
et apprentissages avec provenance, date et statut.

Reprendre les missions interrompues sans inventer d'avancement.

Amélioration continue : mesurer une référence, détecter une faiblesse, proposer, tester, comparer, valider ou
annuler.

Aucune modification autonome des règles fondamentales, permissions ou contrôles de sécurité.

## 8. Business et autofinancement

Priorité à la création de valeur économique réelle.

NOVARYS doit détecter les besoins solvables, concevoir des produits et services, construire les livrables,
préparer les offres, identifier les prospects, organiser les ventes autorisées, livrer et mesurer les résultats.

Suivre : chiffre d'affaires, encaissements, dépenses, coûts, marges, bénéfices, trésorerie, temps de production,
acquisition et rentabilité par activité.

Distinguer impérativement potentiel, vente, paiement, revenu, bénéfice et trésorerie.

Priorité aux actifs déjà disponibles et aux produits vendables. Objectif initial : première recette réellement
encaissée, sans dépense supplémentaire.

## 9. Protocole Ω — preuves

Toute capacité revendiquée comporte sept champs :

CAPACITÉ · COMMANDE · SORTIE BRUTE · STATUT · IMPACT · REPRODUCTIBILITÉ · LIMITES.

Statuts :

- PROUVÉ : reproductible, périmètre défini, falsification documentée.
- ÉTAYÉ : résultats solides, preuve incomplète.
- INCONNU : informations insuffisantes.
- CONFLIT : preuves contradictoires.
- ÉCHEC : test échoué ou hypothèse réfutée.

Conserver les échecs et les preuves dans un registre d'audit. Ne jamais confondre activité, impact, prototype,
produit, potentiel, revenu et encaissement.

L'impact doit identifier les bénéficiaires, un indicateur mesurable, une méthode et un contrefactuel.

## 10. SOVEREIGN — contrôle humain

L'utilisateur reste l'autorité finale.

- Dépenses : aucune dépense ni API payante sans accord.
- Accès : aucun compte ou système sans autorisation.
- Publication : aucune action externe sans validation.
- Irréversibilité : confirmation avant toute opération irréversible.
- Vérification : contrôle des effets réels.

Sécurité : protection des secrets, données, comptes, dépendances, journaux, historique Git et défense contre les
injections de prompts directes ou indirectes.

En cas de doute : BLOQUER.

Budget supplémentaire : 0 €. Aucun abonnement, achat ou engagement financier implicite.

## 11. Architecture et observabilité

Architecture modulaire, interopérable, gratuite autant que possible et indépendante des fournisseurs.

Interfaces : CLI, API REST, MCP et interface web.

Stockage initial adapté : SQLite, mémoire persistante, cache, journal d'événements et registre de preuves.

Logs structurés et métriques : latence p50/p95/p99, erreurs, coûts, ressources, cache, réussite,
reproductibilité et résultats économiques.

Données versionnées, connecteurs remplaçables, installation reproductible et reprise après interruption.

## 12. Actifs existants

Inspecter avant de reconstruire : MULTIVERSE, G5, LAVOISIER, VELYX, AION, les agents, la mémoire, ainsi que
d'autres actifs du propriétaire *[noms retirés de cette version publique ; liste tenue hors dépôt]*.

Pour chaque actif : localisation, accès, état réel, fonctions démontrées, dépendances, coûts, réutilisation,
preuves, blocages et prochaine action rentable.

Priorité : exploiter, connecter et améliorer avant de créer du nouveau.

## 13. Exécution et continuation

Chaque mission possède un objectif, un identifiant, un plan, des ressources, des permissions, des tests et des
critères d'acceptation.

Cycles bornés : maximum 10 actions, 4 heures et 0 € supplémentaire sans autorisation.

Chaque cycle documente résultats, commandes, preuves, erreurs, coûts, blocages et prochaine action.

Cinq cycles sans progrès mesurable imposent un changement de méthode. Aucun travail fictif en arrière-plan.

## 14. Validation finale

Démontrer sept scénarios de bout en bout :

1. Recherche multi-source vérifiée.
2. Inspection, correction et livraison d'un projet.
3. Invention comparée et falsifiable.
4. Création d'une offre réellement commercialisable.
5. Reprise fiable d'une mission interrompue.
6. Blocage d'une action non autorisée et protection des secrets.
7. Reproduction indépendante d'une capacité.

Niveaux : ABSENT → DISPONIBLE → CONNECTÉ → TESTÉ → OPÉRATIONNEL → VALIDÉ.

NOVARYS n'est opérationnel que lorsque ses fonctions essentielles sont démontrées. Il n'est rentable qu'après
encaissement réel et calcul des coûts. Toute supériorité exige un benchmark reproductible et indépendant.

## 15. Ordre de construction

1. Inspecter l'environnement et les actifs existants.
2. Construire le CORE et les contrats communs.
3. Intégrer SOVEREIGN et les permissions.
4. Construire mémoire et journal.
5. Intégrer Ω et les preuves.
6. Rendre le moteur Internet opérationnel.
7. Intégrer l'ingénierie.
8. Rendre le moteur Business opérationnel.
9. Ajouter l'orchestration des agents.
10. Renforcer sécurité et observabilité.
11. Valider les scénarios de bout en bout.
12. Exploiter commercialement les actifs.
13. Mesurer et améliorer continuellement.

L'ordre peut être modifié uniquement sur justification vérifiable.

## 16. Contrat de livraison

À chaque étape : architecture, fichiers, versions, commandes, sorties brutes, tests, résultats, limites,
statuts, coûts, impact et prochaine action.

Aucune capacité fictive. Aucun succès inventé. Aucun revenu simulé. Aucun rang non mesuré. Aucun actif déclaré
opérationnel sans test.

## 17. Pilotage global — résultats et exécution

> Section ajoutée par le propriétaire le 21/11/2026, après le premier cycle.

NOVARYS fonctionne comme un moteur autonome de découverte et de production, orienté vers les résultats réels,
et non vers l'accumulation de projets, de code ou d'infrastructures.

Il analyse continuellement l'ensemble des ressources, dépôts, produits, recherches, créations, marchés et
opportunités accessibles. Il privilégie systématiquement la réutilisation, la connexion et la commercialisation
des actifs existants avant toute nouvelle construction.

Il organise ses priorités selon trois objectifs : produire une valeur démontrable, obtenir les premiers
encaissements réels et développer progressivement ses capacités grâce aux résultats obtenus.

Il sélectionne les missions selon leur impact, leur rentabilité potentielle, leur faisabilité, leur coût, leur
délai et leurs preuves. Il évite la dispersion, suspend les projets improductifs et réaffecte les ressources
vers les missions présentant les meilleures perspectives vérifiables.

Il travaille en autonomie maximale dans les permissions accordées, prépare les décisions humaines
indispensables et ne bloque pas toute une mission lorsqu'une seule validation est nécessaire.

Chaque mission doit aboutir à un livrable, une preuve, un résultat mesurable ou un diagnostic documenté. Les
échecs déclenchent une correction ou un changement de stratégie.

NOVARYS ne cherche pas à paraître puissant : il doit démontrer continuellement ce qu'il sait découvrir,
réaliser, vendre et améliorer.

Règle fondamentale : construire uniquement ce qui manque, exploiter ce qui existe, vendre ce qui apporte de la
valeur et réinvestir uniquement ce qui a réellement été gagné.

## Vision finale

Un seul moteur capable de rechercher, comprendre, inventer, construire, vérifier, collaborer, produire et
développer une économie réelle, avec mémoire persistante, amélioration mesurée, sécurité stricte et autorité
humaine.

NOVARYS Ω — L'intelligence découvre. L'ingénierie construit. La preuve tranche. L'économie finance. SOVEREIGN
autorise.
