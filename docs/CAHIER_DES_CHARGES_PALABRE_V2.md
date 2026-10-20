# Cahier des charges — Palabre Numérique V2

**Version de travail :** 1.0 — 16 octobre 2026.  
**Statut :** proposition à valider.  
**Modèle :** cahier des charges universel en six documents (PRD, TRD, APP FLOW, UI/UX DESIGN, BACKEND SCHEMA, IMPLEMENTATION PLAN).

## 01. PRD — Cahier des charges fonctionnel

**Finalité.** Préserver le patrimoine oral d'Ali-Sabieh : recueillir des récits en somali, archiver leurs voix originales, organiser une transcription et une traduction révisées, et ne diffuser que les récits autorisés.

**Utilisateurs.** Détenteurs de récits, collecteurs, transcripteurs, traducteurs, Collège des Sages, administrateurs et public.

**MVP.** Authentification ; consentement explicite ; enregistrement/import audio ; sauvegarde privée ; fiche de provenance ; transcription somalie amendable ; validation humaine ; bibliothèque publique filtrée ; retrait.

**Hors MVP.** Publication automatique, clonage vocal sans autorisation, traduction distante sans évaluation préalable.

| Exigence | Fonction | Recette |
|---|---|---|
| PRD-F001 | Consentement | Aucune collecte sans consentement applicable |
| PRD-F002 | Enregistrement audio | Capturer, relire et conserver le fichier |
| PRD-F003 | Stockage privé | Un autre utilisateur ne peut accéder au fichier |
| PRD-F004 | Provenance | Date, langue, localité, droits documentés |
| PRD-F005 | Transcription | Brouillon modifiable, correction humaine |
| PRD-F006 | Traduction | Version française attribuable et révisée |
| PRD-F007 | Revue | Soumission, retour et historique |
| PRD-F008 | Validation | Publication interdite sans approbation et droit de diffusion |
| PRD-F009 | Catalogue public | Uniquement les récits publiés |
| PRD-F010 | Révocation | Retrait des accès publics et audit |
| PRD-F011 | Traçabilité | Historique d'événements critiques |
| PRD-F012 | Voix synthétique (V2) | Annonce du caractère artificiel et permission |

**Objectifs indicatifs à confirmer :** 100 % des publications validées ; 100 % des récits collectés avec consentement vérifiable ; au moins 95 % des métadonnées requises renseignées.

## 02. TRD — Spécifications techniques

**Constat dépôt.** Frontend HTML/JS dans `frontend/heritage/`, backend Python/SQLite dans `backend/heritage/`, module local Faster-Whisper, adaptation Supabase Auth/Storage, squelette Android, prototype de narration. Les modes local/Cloud ne se synchronisent pas automatiquement.

**Cible.** HTTPS → frontend Android/web → authentification et permissions → API versionnée → PostgreSQL/Storage privés → transcription locale ou fournisseur contrôlé → validation humaine → catalogue public séparé.

- La clé `service_role` et les secrets IA ne doivent jamais être publiés dans le navigateur.
- Policies RLS à vérifier pour les tables ET les objets Storage.
- Séparer développement, tests et production ; sauvegarder, restaurer et superviser.
- Cibles indicatives : 99 % de disponibilité mensuelle ; restauration RTO ≤8 h ; pertes de données RPO ≤24 h ; latence p95 catalogue <3 s en conditions définies.
- Tester réellement le micro, l'enregistrement, la reconnexion et la lecture sur Android.
- Appliquer une revue humaine aux résultats Whisper, traduction et voix synthétique.

## 03. APP FLOW — Parcours utilisateur

**FLOW-P001 :** connexion → explication du consentement → collecte → aperçu → archive privée → métadonnées → transcription → corrections → validation culturelle → autorisation de diffusion → publication ou refus.

**FLOW-P002 :** visiteur → bibliothèque → filtre/recherche → récit publié → lecture de l'original et des textes autorisés.

**FLOW-P003 :** demande de retrait → contrôle habilité → dépublication → invalidation des accès → vérification et journalisation.

**Alternatives :** refus du micro, réseau absent, consentement non donné, fichier illisible, compte non habilité, revue refusée, révocation.

## 04. UI/UX DESIGN — Interfaces et ergonomie

Interface accessible mobile d'abord, en somali et français, avec langage simple et boutons larges.

| Écran | But |
|---|---|
| UX-E001 | Accueil et bibliothèque |
| UX-E002 | Connexion / profil |
| UX-E003 | Consentement / capture |
| UX-E004 | Mes enregistrements privés |
| UX-E005 | Transcription / traduction |
| UX-E006 | Revue et décision |
| UX-E007 | Recherche / détail du récit |
| UX-E008 | Administration / audit |

Prévoir erreurs lisibles, assistance vocale si permise, états de chargement, navigation clavier et audits WCAG applicables. Tester maquettes PC et Android avec les collecteurs et validateurs.

## 05. BACKEND SCHEMA — Données et services

**Tables cibles proposées :** `users`, `records`, `consents`, `audio_assets`, `transcript_versions`, `translations`, `reviews`, `audit_events`. Vérifier le schéma réel avant migration ; ces noms ne constituent pas un état des tables Supabase déployées.

**Relations.** Un récit possède plusieurs versions de transcription, ressources audio, décisions et, selon les cas, traductions. Le statut public doit résulter d'une autorisation en vigueur ET d'une validation documentée.

**API cible proposée et non confirmée dans le code :** `GET /api/v1/public/records`, `POST /api/v1/records`, `POST /api/v1/consents`, `POST /api/v1/records/{id}/reviews` et `POST /api/v1/records/{id}/withdraw`.

**Contrôles.** UUID, contraintes de qualité, journal d'audit, conservation minimale, chiffrement transit, RLS, liens audio temporaires signés et procédure de révocation.

## 06. IMPLEMENTATION PLAN — Plan de réalisation

| Phase | Travail | Livrable | Validation |
|---|---|---|---|
| 1 | Audit dépôt et besoins | Diagnostic | Risques approuvés |
| 2 | Maquettes et navigation | UX | Parcours validés |
| 3 | Accès, données, RLS, API | Backend | Tests d'isolation réussis |
| 4 | Audio, transcription, revue | MVP | Parcours de bout en bout |
| 5 | Tests Android, sécurité, UX | Rapport | Aucun bloquant |
| 6 | Déploiement / sauvegarde | Version publiée | Go/no-go signé |
| 7 | Stabilisation / formation | Version stable | Réception validée |

**Calendrier de cadrage proposé :** 12 à 16 semaines selon ressources, priorités et disponibilité du Collège des Sages. Budget à chiffrer ; ne pas tenir les services externes pour gratuits.

**RACI (proposé) :** porteur A pour le périmètre et la mise en service ; développeur R pour le code ; Sages A/R pour la validation culturelle ; responsable qualité R pour la recette. Désignations nominatives à confirmer.

**Risques critiques :** divulgation de récits non autorisés, perte audio, transcription infidèle, incompatibilité Android, erreurs RLS, transferts de données tiers.

**Recette minimale :** TEST-001 refus consentement ; TEST-002 isolement fichier A/B ; TEST-003 brouillon jamais public ; TEST-004 retrait public ; TEST-005 Android micro/lecture ; TEST-006 correction somalie ; TEST-007 sauvegarde/restauration ; TEST-008 retour arrière.

## Annexes et traçabilité

| PRD | Flow | UX | Backend | Test |
|---|---|---|---|---|
| PRD-F001 | FLOW-P001 | UX-E003 | consents | TEST-001 |
| PRD-F003 | FLOW-P001 | UX-E004 | audio_assets/RLS | TEST-002 |
| PRD-F008 | FLOW-P001 | UX-E006 | reviews | TEST-003 |
| PRD-F010 | FLOW-P003 | UX-E008 | consents/withdrawal | TEST-004 |

**Checklist avant production :** approbations, consentements, rôles/RLS, tests fonctionnels et sécurité, sauvegarde/restauration, documentation/formation, supervision, retour arrière et autorisation écrite.

**Réception :** projet/version, date, livrables, tests, réserves, décision et signatures du porteur, des représentants des Sages et des responsables techniques.

## État connu et limites

Le [README du dépôt](../README.md) précise que le prototype est en développement et que la disponibilité en production des modules doit être vérifiée. Les PR #3–#6 ont introduit Whisper local, interface de transcription, microphone et intégration Supabase, sans constituer une recette de production. Ce cahier des charges formule les exigences attendues, **pas** la preuve que chaque fonctionnalité est opérationnelle.

**Références :** modèle universel à six volets remis par le porteur ; [README](../README.md) ; [API](API_PATRIMOINE.md) ; [Stockage](STOCKAGE_PATRIMOINE.md) ; [Recette audio](RECETTE_AUDIO.md).
