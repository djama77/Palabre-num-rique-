# Supabase — Palabre Numérique

## État constaté

Le frontend `frontend/heritage/supabase-cloud.js` utilise Supabase Auth, la table `public.palabre_records` et le bucket `palabre-audio`. Le code client seul ne prouve pas que le projet distant est initialisé ou que les règles RLS sont correctes.

## Mise en place

1. Ouvrir le bon projet dans le tableau de bord Supabase et vérifier que son identifiant correspond à l'URL utilisée par le frontend.
2. Vérifier les tables et politiques existantes avant d'appliquer une migration. La migration `supabase/migrations/20261028000000_palabre_cloud_baseline.sql` crée le schéma de base et des politiques RLS, et configure le bucket audio en privé.
3. Exécuter la migration uniquement dans le projet prévu après revue. Elle ne doit pas être exécutée dans un autre projet par erreur.
4. Dans Auth, configurer la confirmation d'adresse e-mail et les URL autorisées pour les environnements de test et de production.
5. Garder uniquement l'URL et la clé publishable dans le navigateur. Ne jamais utiliser `service_role` ou une clé secrète côté client.
6. Tester avec deux comptes distincts : chaque compte doit voir ses brouillons et audios à lui uniquement. Un visiteur non connecté ne doit voir que les récits dont `status = 'published'`, `consent_recorded = true` et `publication_authorized = true`.
7. Ne publier aucun récit avant une validation humaine et une autorisation explicite du détenteur du savoir et du processus de gouvernance du projet.

## Choix de sécurité

- Les utilisateurs authentifiés peuvent créer uniquement des brouillons privés avec consentement confirmé.
- Les utilisateurs ne peuvent pas modifier eux-mêmes `status` ou `publication_authorized` via les droits SQL accordés par cette migration.
- Le bucket `palabre-audio` est privé ; les fichiers doivent être rangés dans un dossier portant l'UUID de leur propriétaire.
- La clé publishable est publique par conception ; la sécurité dépend des politiques RLS et Storage, jamais du secret de la clé.
- La migration ne crée pas de rôle « Collège des Sages » ni de mécanisme d'approbation administrative. Cette étape doit être implémentée dans un backend fiable avant d'autoriser la publication en production.
- Les enregistrements culturels sensibles doivent rester privés par défaut. La transcription ou la traduction automatique n'est pas une validation.

## Vérifications après application

- Confirmer que la table et le bucket existent.
- Lancer les conseillers Supabase de sécurité et corriger toute alerte.
- Tester l'inscription, la confirmation e-mail, la connexion, la déconnexion, l'upload, la lecture signée et la suppression d'un brouillon.
- Tester les accès avec un second compte et en navigation privée.
- Confirmer qu'aucun enregistrement n'est lisible sans autorisation.


## Schéma cible V1 : gouvernance des récits

Le fichier `supabase/migrations/20261028010000_palabre_schema_cible_v1.sql` propose le modèle métier détaillé demandé : rôles (collecteur, transcripteur, traducteur, Sage, admin, audit), récits, affectations, consentements par usage, fichiers audio privés, versions de texte, validations et journal d'audit.

**Cette migration est une proposition de schéma cible, pas une migration à exécuter maintenant.** Elle ajoute les tables `records`, `assignments`, `consents`, `audio_assets`, `text_versions`, `reviews` et `audit_events`. Elle ne remplace pas la table `palabre_records` utilisée par le frontend actuel ; le frontend devra être adapté et testé avant toute mise en production.

### Garde-fous prévus

- Les récits sont privés par défaut ; le catalogue public ne montre que les récits publiés, avec consentement de diffusion actif et deux validations approuvées.
- La vue publique utilise `security_invoker = true`, des politiques RLS dédiées et des droits de lecture limités par colonnes.
- Les rôles ne sont pas attribuables depuis le navigateur ; leur attribution doit passer par un canal administratif fiable.
- L'auto-validation est refusée et le réviseur doit être l'utilisateur connecté avec le rôle Sage.
- La révocation du consentement retire le récit du catalogue et écrit un événement d'audit.
- Le bucket `audio-prive` est privé ; l'accès aux objets est limité selon l'identité, l'affectation et le consentement d'archivage.
- Les URLs audio publiques temporaires ne sont pas encore générées : une fonction serveur devra vérifier le statut, le consentement et les validations avant de créer une URL signée.

### Avant toute application

1. Faire l'inventaire du schéma, des vues, des triggers et des politiques RLS déjà présents dans le projet Supabase cible.
2. Tester la migration sur un projet de test ou une branche de base de données.
3. Vérifier les droits réels du rôle `anon` et du rôle `authenticated`, notamment le catalogue public et les fichiers audio.
4. Tester les cas de refus : pas de consentement, consentement révoqué, une validation manquante, auto-validation, accès par un autre compte.
5. Adapter le frontend à ce nouveau modèle et faire passer les tests avant de planifier le déploiement.

Le schéma actuel n'a pas encore été inventorié à distance ; aucune migration de ce schéma cible n'a été appliquée à un projet Supabase distant.
