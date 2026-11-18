# Audit et durcissement — Palabre Numérique

Date : 18 novembre 2026  
Branche : `fix/palabre-audio-privacy-hardening`

## Périmètre de cette intervention

Cette branche part de `feat/palabre-supabase-dedicated` afin de conserver la PR #14 intacte. Elle ne modifie pas `main` et ne fusionne aucune branche.

## Corrections apportées dans cette branche

- L'inférence Faster-Whisper est déplacée hors de la boucle asynchrone FastAPI afin de ne pas bloquer les autres requêtes HTTP.
- Le service refuse les nouvelles transcriptions lorsque sa capacité de traitement configurée est déjà occupée (HTTP 429 et Retry-After).
- Les limites de taille et de concurrence sont vérifiées au démarrage.
- Le chargement du modèle est paresseux : la route `/health` ne télécharge ni ne charge le modèle.
- Les fichiers temporaires sont supprimés dans un bloc `finally`, y compris en cas d'erreur.
- Des tests API isolés vérifient authentification, format, type MIME, taille, réponse, erreurs et nettoyage, sans télécharger de modèle.
- Le consentement à transmettre un audio au service de transcription est distingué de l'autorisation d'archiver audio et texte dans Supabase.
- L'archivage devient une action explicite de l'utilisateur après relecture de la transcription ; il n'est plus déclenché automatiquement.
- Une migration ajoute `archive_authorized` et impose cette autorisation pour la création et la lecture publique des archives publiées.

## Limites qui restent à lever avant production

1. Déployer le conteneur Whisper sur un hébergeur adapté et renseigner son URL HTTPS dans la configuration front-end.
2. Configurer les variables serveur Supabase et les origines CORS exactes.
3. Exécuter les tests GitHub Actions sur cette branche.
4. Tester les règles RLS et le bucket privé sur un projet Supabase de préproduction, avec des comptes de test distincts.
5. Vérifier sur Android les formats réellement produits par l'enregistreur, l'envoi, la reprise après coupure réseau et la lecture d'archives.
6. Tester la qualité du modèle sur un corpus somali validé par des locuteurs compétents. Le résultat automatique ne doit jamais être considéré comme une transcription officielle sans correction humaine.

## Paramètres du service

- `MAX_AUDIO_BYTES` : taille maximale autorisée, 100 Mio par défaut.
- `MAX_CONCURRENT_TRANSCRIPTIONS` : nombre maximal de traitements simultanés dans un processus, 1 par défaut.
- Pour une mise à l'échelle multi-instance, ajouter une limitation distribuée au niveau du proxy ou de la plateforme d'hébergement. Le sémaphore applicatif ne remplace pas cette protection.

## Décision de livraison

Cette branche est une proposition de correction à tester. Elle ne constitue pas une validation de production. La fusion vers `main` reste conditionnée aux tests verts, à la revue de la migration SQL et aux essais réels de bout en bout.
