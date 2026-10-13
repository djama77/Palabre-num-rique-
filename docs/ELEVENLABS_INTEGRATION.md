# Intégration ElevenLabs — Palabre numérique

## État
Cette branche ajoute un prototype indépendant dans `elevenlabs-demo/index.html`. Il utilise la synthèse vocale du navigateur pour permettre une démonstration immédiate **sans compte, sans clé API et sans coût ElevenLabs**. Il ne réalise pas encore d'appel ElevenLabs.

## Intégration ElevenLabs de production
1. Identifier le framework, l'hébergement et le backend existants avant de modifier l'application principale.
2. Créer une clé API ElevenLabs dans le compte du propriétaire et la conserver **uniquement côté serveur** (variable d'environnement `ELEVENLABS_API_KEY`). Ne jamais publier cette clé dans GitHub ni l'envoyer directement au navigateur.
3. Ajouter une route backend authentifiée `POST /api/tts` acceptant un texte limité, une langue et une voix autorisée ; vérifier longueur, quotas et droits utilisateur.
4. Le serveur appelle l'API officielle ElevenLabs de synthèse vocale avec la clé et transmet le flux audio au client, sans exposer la clé.
5. Prévoir limites de dépenses, protection anti-abus, consentement pour les voix clonées, journalisation minimale, cache facultatif et alternative de lecture navigateur.
6. Tester les voix disponibles en français, somali et arabe **avant** de promettre leur qualité ou disponibilité.

## Tests du prototype
Ouvrir `elevenlabs-demo/index.html` sur Chrome ou Edge, saisir un message, choisir la langue, cliquer Écouter puis Arrêter. Les langues disponibles dépendent du système.

## Suite
Raccorder l'interface vocale aux messages de Palabre numérique après identification de la structure du projet et validation de l'architecture backend.
