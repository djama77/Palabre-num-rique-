# Intégration audio VoiceStudio — PALABRE NUMÉRIQUE

Référence : https://github.com/debpalash/VoiceStudio

## Travail préparé sur cette branche
- `docs/VOICESTUDIO_AUDIT.md` : audit documentaire des modules audio existants.
- `backend/heritage/audio_providers.py` : interfaces de fournisseurs, adaptateur faster-whisper, adaptateur ElevenLabs et empreinte SHA-256.
- `backend/heritage/voicestudio_client.py` : client optionnel pour `POST /v1/audio/transcriptions` et `POST /v1/audio/speech`.
- `backend/heritage/test_audio_providers.py` et `test_voicestudio_client.py` : tests unitaires ajoutés.
- `docs/VOICESTUDIO_PROTOTYPE_PROTOCOL.md` : protocole de benchmark.

## Principes
1. Garder l'original immuable ; les sorties sont des dérivés.
2. Consentement requis et transcription automatique soumise à validation humaine.
3. Les récits, les droits, les validations et la publication restent gérés par PALABRE NUMÉRIQUE.
4. Aucun secret dans le navigateur ni dans Git.
5. Par défaut, VoiceStudio est appelé sur `http://127.0.0.1:3900`. Tout hôte distant exige HTTPS et `PALABRE_ALLOW_REMOTE_VOICESTUDIO=yes`.
6. Ne pas cloner une voix réelle sans consentement explicite.

## Configuration locale
Le client lit `VOICESTUDIO_BASE_URL` et, si configurée, `VOICESTUDIO_API_KEY` depuis l'environnement serveur. Les identifiants de modèles STT/TTS doivent être sélectionnés après inspection des modèles réellement installés. La prise en charge du somali doit être mesurée, pas présumée.

## Étapes restantes
- Exécuter les tests dans l'environnement cible.
- Tester sur 3 à 5 extraits audio non sensibles et autorisés.
- Mesurer WER/CER, erreurs de noms propres, durée de traitement, RAM/VRAM, CPU/GPU et qualité de narration.
- Raccorder l'adaptateur au workflow métier seulement après validation des mesures.
- Tester permissions, refus sans consentement, erreurs du moteur et intégrité SHA-256.
- Examiner la licence AGPL-3.0 de VoiceStudio et la licence du modèle retenu avant distribution.

## État réel
L'audit documentaire et le code client facultatif sont ajoutés à cette branche. Les tests n'ont pas encore été exécutés par moi dans un environnement cible, aucun fichier audio de test n'a été fourni, et l'adaptateur n'est pas encore raccordé à une route web de PALABRE NUMÉRIQUE. Aucun résultat de benchmark n'est donc déclaré.
