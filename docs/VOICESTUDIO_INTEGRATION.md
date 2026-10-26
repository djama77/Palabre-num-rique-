# Intégration audio inspirée de VoiceStudio

## Objectif
Améliorer Palabre Numérique pour gérer les enregistrements du patrimoine oral : import, écoute, transcription assistée, correction humaine, traduction validée et narration audio facultative.

Projet de référence fourni : https://github.com/debpalash/VoiceStudio

> Cette note prépare une intégration ciblée. Le code de VoiceStudio n'a pas encore été importé ni testé dans Palabre Numérique. Vérifier le dépôt source, sa licence, ses dépendances et ses exigences avant toute réutilisation.

## Principes de protection du patrimoine
1. Conserver l'enregistrement original sans le modifier ; les transcriptions, traductions et narrations sont des fichiers dérivés distincts.
2. Documenter le consentement, la provenance, les droits d'accès et les restrictions de diffusion.
3. Toute transcription ou traduction automatique reste un brouillon jusqu'à validation par une personne habilitée.
4. Donner la priorité au somali original et permettre la correction des variantes locales.
5. Ne jamais publier automatiquement un récit sensible.
6. Ne jamais placer de clés API ou secrets dans le frontend, le dépôt Git ou les journaux.
7. La consultation locale doit rester possible sans fournisseur vocal distant.

## Fonctionnalités proposées
### Phase 1 — Fichiers audio
- Import avec titre, langue, date, source et statut de consentement.
- Calcul d'une empreinte SHA-256 pour vérifier l'intégrité de l'original.
- Lecteur accessible sur mobile, durée, format et taille.
- Statuts : brouillon, à transcrire, à corriger, à valider, validé, restreint, publié.
- Vérification du type réel et de la taille du fichier ; protection des fichiers restreints.

### Phase 2 — Transcription assistée
- Auditer et réutiliser en priorité les modules locaux de transcription déjà présents dans backend/heritage/.
- Conserver la sortie automatique et les corrections humaines comme versions séparées.
- Enregistrer le moteur, sa version, la date et la langue utilisée.
- Afficher un avertissement explicite indiquant que la transcription doit être vérifiée.

### Phase 3 — Narration vocale
- Définir une interface de fournisseur remplaçable entre moteur local et service distant.
- Générer une narration seulement après validation du texte et vérification des droits.
- Étiqueter clairement les voix synthétiques ; ne cloner aucune voix réelle sans consentement explicite.
- Stocker les narrations séparément des originaux et garder les métadonnées du moteur.
- Appeler les services distants côté serveur uniquement, avec limites de taille, durée et coût.

### Phase 4 — Interface
- Ajouter un espace « Audio et témoignages » à l'interface du patrimoine.
- Distinguer l'original, la transcription automatique, le texte corrigé, la traduction et la narration.
- Prévoir des commandes adaptées au clavier et aux téléphones Android.
- Afficher des erreurs compréhensibles lorsque le moteur ou Internet est indisponible.

## Architecture cible
- Frontend : interface et lecteur ; aucun secret fournisseur.
- Backend : autorisation, validation des fichiers et orchestration des moteurs.
- Stockage : originaux séparés des dérivés, accès contrôlé par statut.
- Base de données : métadonnées, consentements, versions, validations et historique minimal.
- Fournisseurs : adaptateurs facultatifs ; ne pas rendre un service distant obligatoire pour consulter les récits locaux.

## Critères d'acceptation
- L'original reste inchangé après chaque opération.
- Un récit restreint est inaccessible sans autorisation.
- Les textes automatiques et validés sont clairement distingués.
- Aucun secret n'est présent dans le frontend ou dans Git.
- Tests des fichiers invalides, permissions, erreurs de moteur et contenus non publiés.
- Essais sur ordinateur et téléphone Android.
- Documentation exacte des fonctions locales et de celles qui nécessitent Internet.

## Plan de réalisation
1. Auditer les modules audio et les tests existants de Palabre Numérique.
2. Vérifier la licence, les langues et les dépendances de VoiceStudio.
3. Choisir les composants réutilisables sans remplacer inutilement l'existant.
4. Implémenter import et lecteur avec contrôle d'accès.
5. Relier la transcription locale existante et la validation humaine.
6. Ajouter un adaptateur de synthèse vocale facultatif.
7. Exécuter les tests et les essais sur appareil avant mise en production.

## État
- [x] Branche de travail créée.
- [x] Plan d'intégration et exigences de protection documentés.
- [ ] Audit de code et de licence de VoiceStudio.
- [ ] Intégration du code audio dans l'application.
- [ ] Tests d'intégration et validation sur appareil.

Cette documentation seule n'active aucune fonctionnalité de production.