# Palabre numérique — Architecture vocale alignée sur le dossier Ali-Sabieh

## Référence fonctionnelle
Le projet est une plateforme de sauvegarde du patrimoine oral et coutumier d'Ali-Sabieh, **pas** un forum généraliste. Le dossier de candidature 2026 prévoit : interface HTML/CSS/JavaScript, transcription Whisper en somali, traduction NLLB-200/Helsinki-NLP en français, classification NLP, recherche sémantique, stockage PostgreSQL/pgvector ou SQLite, fonctionnement local et validation par le Collège des Sages.

## Chaîne de traitement
1. Consentement du Sage et capture audio **originale en somali**.
2. Stockage local sécurisé de l'original, avec métadonnées et niveau d'accès.
3. Whisper : transcription somali, segments et horodatages.
4. Correction et validation humaine par le Collège des Sages.
5. Traduction somali → français, relecture humaine, classement et indexation.
6. Archivage bilingue (somali et français) avec provenance, restrictions et validation.
7. Restitution : **audio original prioritaire** ; option de lecture de la traduction française avec ElevenLabs si autorisée, ou synthèse locale du navigateur.
8. Transmission pédagogique : fiches, glossaires et quiz fondés sur des contenus validés.

## Place d'ElevenLabs
ElevenLabs est un service distant facultatif de synthèse vocale, et ne doit jamais remplacer l'original ni être présenté comme la voix du Sage. Ne pas transférer d'audio culturel sensible ou de textes restreints à un fournisseur distant sans autorisation explicite. Le module `backend/voice/elevenlabs_tts.py` fournit un adaptateur Python **non connecté à une route web** ; l'application principale doit d'abord être localisée et son authentification vérifiée.

## Sécurité / gouvernance
- Ne pas mettre de clé API dans le navigateur ni dans GitHub ; configurer `ELEVENLABS_API_KEY` uniquement sur le serveur.
- Vérifier le statut « validé », le niveau d'accès et les droits du demandeur **depuis la base**, jamais à partir d'un booléen fourni par le navigateur.
- Limiter appels, coûts, volume et durée ; ne pas enregistrer automatiquement l'audio généré dans les archives historiques.
- Conserver la provenance de chaque audio (original / synthèse), la langue et l'identifiant du récit.
- Prévoir une alternative hors-ligne ; l'API ElevenLabs nécessite Internet.
- La disponibilité et la qualité des voix somali doivent être testées avant déploiement.

## Schéma des données à préserver
ID, titre somali, titre français, transcription somali, traduction française, lieu/date/source de collecte, fichier audio original, thèmes, mots-clés, validation par les Sages, niveau d'accès et contenus pédagogiques.

## Prochaine intégration
Identifier l'arborescence réelle du dépôt et son backend actif. Ajouter ensuite une route sécurisée (ex. `POST /api/voice/tts`) avec contrôle serveur des autorisations et de la validation, puis intégrer un bouton « Écouter la traduction » aux fiches de récits validés.
