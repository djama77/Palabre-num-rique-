# Audit technique — VoiceStudio et PALABRE NUMÉRIQUE

Date de l'audit documentaire : 2026-10-26  
Branche : `feature/voicestudio-integration`

## Résumé exécutif

PALABRE NUMÉRIQUE possède déjà une chaîne audio locale et des garde-fous. VoiceStudio est une application desktop de production vocale, avec plusieurs moteurs sélectionnables, transcription/dictée, clonage vocal, doublage vidéo et API locale/MCP annoncée dans son README. La meilleure stratégie est de conserver le workflow documentaire et la conservation des récits dans PALABRE NUMÉRIQUE, puis d'évaluer VoiceStudio comme moteur optionnel séparé. Ne pas copier des modules ou modèles avant vérification de la licence et de l'API de la version retenue.

## Audit de PALABRE NUMÉRIQUE

| Fichier | Rôle observé | Décision |
|---|---|---|
| `backend/heritage/whisper_transcription.py` | Transcription locale via faster-whisper, langue somalie demandée, formats et taille limités, segments horodatés | Garder comme moteur de référence pour le premier prototype |
| `backend/heritage/local_transcription.py` | Route POST locale `/api/local/transcrire`, consentement, origine/hôte et taille contrôlés, fichier temporaire supprimé | Garder ; compléter les tests d'erreur et mesurer la performance |
| `backend/heritage/local_narration.py` | Narration d'une traduction française déjà publiée via adaptateur ElevenLabs | Garder ; dépend d'un service distant et d'une configuration secrète |
| `backend/voice/elevenlabs_tts.py` | Adaptateur backend ElevenLabs, limite texte, clé d'environnement et délai réseau | Garder comme fournisseur distant facultatif |
| `frontend/modules/heritage-audio.js` | Lit l'original et utilise SpeechSynthesis du navigateur pour la traduction d'un récit public validé | Garder comme solution légère sans installation de modèle |
| `backend/heritage/web_app.py` | Serveur local loopback, branche les routes transcription/narration | Garder ; ne pas exposer directement à Internet |
| `backend/heritage/test_local_transcription.py` | Tests de refus accès distant, consentement manquant, origine croisée, route inconnue et taille excessive | Étendre avec tests de non-écrasement et erreur moteur |

## Capacités de VoiceStudio à évaluer

Le README amont décrit une application desktop Electron, un moteur vocal par défaut OmniVoice, un catalogue d'autres moteurs, des fonctions de clonage/conception vocale, doublage, dictée/transcription, livres audio, une API locale et MCP. Il annonce des exécutions locales, avec services distants optionnels. Les capacités exactes dépendent de la version, du moteur installé et du matériel.

Source amont : https://github.com/debpalash/VoiceStudio  
Licence indiquée par le README : AGPL-3.0. Vérifier aussi les licences propres à chaque moteur et modèle.

## Complémentarité — décision

- **Transcription somalie :** garder faster-whisper pour le premier test. VoiceStudio ne le remplace que si un moteur identifié fournit une meilleure précision mesurée sur les mêmes extraits somalis.
- **Narration française :** garder le navigateur TTS pour une option simple et ElevenLabs pour l'adaptateur distant déjà présent. Évaluer VoiceStudio local comme fournisseur alternatif seulement après vérification de l'API et de la qualité.
- **Catalogue, consentement, validation, droits et publication :** rester dans PALABRE NUMÉRIQUE ; ce sont les règles métier du projet, pas des fonctions à déléguer à un studio audio.
- **Clonage vocal et doublage vidéo :** hors du premier prototype ; risque de consentement, complexité et coûts de validation plus élevés.
- **Pas de duplication :** l'intégration doit appeler un fournisseur via une interface, et non copier toute l'application VoiceStudio ou créer une deuxième bibliothèque documentaire.

## Limite de cet audit

Il s'agit d'un audit documentaire des fichiers accessibles sur GitHub, pas d'une exécution sur une machine. Aucun échantillon audio, aucune mesure de qualité ou de temps de traitement et aucun essai réel de VoiceStudio n'ont encore été fournis/exécutés. Les mesures restent donc à compléter lors du prototype local.
