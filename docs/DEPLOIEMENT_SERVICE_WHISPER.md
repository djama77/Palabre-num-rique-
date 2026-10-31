# Déployer le service faster-whisper de Palabre Numérique

## Architecture
Le navigateur Android ouvre l'interface statique sur Vercel. Pour transcrire, il envoie l'audio au service Python `backend/whisper_service`, avec le jeton de sa session Supabase. Le service vérifie ce jeton auprès de Supabase Auth, exécute faster-whisper en somali et renvoie le texte. Le navigateur sauvegarde ensuite le résultat et l'audio dans Supabase avec sa session utilisateur.

Le service ne publie aucun récit et ne possède pas de clé `service_role`.

## Variables serveur
- `SUPABASE_URL` : URL du projet Supabase.
- `SUPABASE_ANON_KEY` : clé publishable/anon du projet, jamais la clé service_role.
- `WHISPER_MODEL` : `small` par défaut ; `base` réduit généralement mémoire et chargement.
- `WHISPER_DEVICE` : `cpu` par défaut.
- `WHISPER_COMPUTE_TYPE` : `int8` par défaut.
- `ALLOWED_ORIGINS` : origines exactes Vercel, séparées par virgules.
- `MAX_AUDIO_BYTES` : limite en octets, 100 Mio par défaut.

## Construction locale
Depuis `backend/whisper_service` :
```bash
docker build -t palabre-whisper .
docker run --rm -p 8000:8000 -e SUPABASE_URL='https://VOTRE_PROJET.supabase.co' -e SUPABASE_ANON_KEY='VOTRE_CLE_PUBLISHABLE' -e ALLOWED_ORIGINS='https://VOTRE-DOMAINE-VERCEL' palabre-whisper
```
Vérifier `GET /health`. Le premier appel télécharge le modèle. Prévoir mémoire, CPU et cache disque suffisants. Vercel ne doit héberger que l'interface, pas le modèle Whisper.

## Sécurité
- Chaque transcription exige un jeton utilisateur Supabase valide.
- Formats acceptés : WAV, MP3, M4A, FLAC, OGG, OPUS et WEBM.
- Taille contrôlée ; fichier temporaire supprimé après traitement.
- CORS limité aux origines configurées.
- Pas de stockage serveur de l'audio/texte, pas de journalisation du contenu.
- RLS Supabase reste responsable de l'accès aux archives.
- Le consentement est requis avant envoi ; la validation humaine reste obligatoire avant publication.

## État
Le service HTTP est préparé dans le dépôt. Son déploiement sur un hébergeur de conteneurs Python, la configuration de son URL dans Vercel et le raccordement du bouton de transcription doivent encore être réalisés et testés. La transcription distante n'est donc pas encore déclarée opérationnelle.