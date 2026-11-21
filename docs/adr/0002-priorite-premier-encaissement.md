# ADR 0002 — Une seule priorité : le premier encaissement, deux missions actives au plus

Date : 21/11/2026. Statut : proposé, en attente de validation du propriétaire.

## Contexte vérifié

La section 17 du cahier des charges demande de choisir les missions sur six critères, d'éviter la dispersion et
de suspendre ce qui ne produit pas. L'état réel, lu dans les dépôts :

- 16 dépôts, aucun encaissement enregistré dans le moteur, trois offres prêtes, aucune en vente ;
- chaque chemin vers une vente attend des gestes que seul le propriétaire peut faire ;
- **un préalable est commun à tous** : un statut permettant de facturer. Alll le demande à l'étape 2 de sa mise
  en route, Velyx dans sa première revue en attente. Démarche gratuite, 20 à 30 minutes selon le dépôt Velyx.

## Trois candidats, six critères (0 à 5 ; pour le coût et le délai, 5 = gratuit ou immédiat)

| Critère | Velyx — fichiers pour courtiers | Alll — livret à 29 € | Ref — conformité face aux IA |
|---|---|---|---|
| Impact | 3 — ces courtiers paient déjà 9 à 110 € le contact (étude du dépôt) ; niche étroite | 3 — achat plaisir ou cadeau | 4 — risque juridique mesuré sur données réelles |
| Rentabilité potentielle | 2 — environ 5 sociétés à signaler par mois et par département, 4 cabinets visés d'abord (chiffres du dépôt) | 3 — coût marginal nul ; le dépôt estime lui-même à 5-10 % la chance d'atteindre son objectif | 3 — moteur gratuit ; le payant attend une validation client |
| Faisabilité | 3 — offre préparée ; brouillons privés à régénérer ; envoi par le propriétaire | 4 — chaîne écrite et testée ; environ 2 heures de mise en route | 3 — moteur construit ; démarchage d'éditeurs par le propriétaire |
| Coût | 5 — 0 € | 3 — médiateur de la consommation, environ 48 €, avant la première vente | 5 — 0 € |
| Délai | 3 — quelques jours après le dépôt du statut | 2 — fenêtre fermée le 20/12/2026 ; le numéro d'entreprise met environ deux semaines | 1 — pilote de 12 semaines |
| Preuves | 3 — étude sourcée ; 0 envoi, taux de réponse INCONNU | 3 — tests et exemple ; demande INCONNUE, aucune visite mesurée | 3 — études solides ; preuve commerciale indirecte |
| **Total / 30** | **19** | **18** | **19** |

Les totaux tiennent en un point : ils ne départagent rien. Ce qui départage, pour l'objectif « premier
encaissement sans dépense », ce sont le coût et le délai.

## Décision proposée

1. **Mission active n°1 — statut, puis premier envoi Velyx.** 0 €, le test le plus court : quatre messages.
2. **Mission active n°2, sous condition — Alll en vente avant le 20/12.** Seulement si le propriétaire accepte
   la dépense du médiateur et dépose le statut dans les jours qui viennent. Sinon : suspendue, et son propre
   critère d'arrêt s'applique.
3. **Suspendus, aucun temps d'agent** : le volet commercial de Ref, Toon-o-Matic, Hive, Clip-preuve, les moteurs
   de recherche (Tr, 1, A, All), MONDO, Artiste-. **Mesure seulement** : Paie-juste et Jeun, où un compteur de
   visites gratuit suffit à savoir s'il y a un usage.
4. **Moteur et outil de preuve** : uniquement ce qu'une mission active exige. Pas d'infrastructure nouvelle
   tant qu'aucun encaissement n'existe.

Suspendre n'efface rien : les dépôts restent, leur état est dans `ACTIFS.md`.

## Ce qui prouverait que cette décision est mauvaise

- Quatorze jours après le dépôt du statut, aucun message Velyx n'est parti : le frein n'était pas le statut.
- Les quatre premiers envois restent sans réponse quatorze jours : changer de cible ou de canal, ne pas insister.
- Une vente hors GitHub existe déjà (actifs non localisés) : elle passerait devant les trois candidats.

## Indicateurs de progrès, relevés à chaque cycle

Statut déposé (oui ou non) · messages envoyés · réponses reçues · montant encaissé, avec sa preuve.
