# Reconnaissance somalie locale et enrichissement lexical

## Ce qui change

- faster-whisper reste disponible et reçoit un initial_prompt constitué exclusivement de mots somalis du lexique local.
- Ogaal-ASR est pris en charge comme moteur local alternatif, fondé sur Whisper large-v3 affiné pour le somali. Il n'est activé automatiquement que si son modèle est déjà présent sur le disque ; aucun téléchargement n'est déclenché par l'application.
- Le lexique ajoute les métadonnées mots_somali à la réponse locale. L'interface ne les affiche pas et aucun bouton n'est ajouté. Le texte transcrit reste strictement inchangé : pas de traduction ni de correction automatique.
- Les fichiers audio originaux restent intacts. La transcription demeure un brouillon qui doit être relu par une personne compétente.

## Ogaal-ASR hors ligne sous Windows

Le code du projet Ogaal-ASR est sous Apache-2.0. Le modèle et ses dépendances doivent être installés séparément, et leur licence/version doit être vérifiée avant distribution. Préparer le modèle une seule fois sur une machine autorisée, puis copier les fichiers du modèle sur l'ordinateur hors ligne.

Installer les dépendances optionnelles dans un environnement virtuel :

    python -m pip install -r backend/heritage/requirements-ogaal.txt

Si une connexion Internet est autorisée pendant la préparation, télécharger une fois le modèle vers un dossier local avec le client Hugging Face installé :

    hf download Ogaal-Labs/Ogaal-ASR --local-dir C:\Models\Ogaal-ASR

Transférer ensuite ce dossier sur le PC hors ligne. Au démarrage, l'application n'effectue pas de téléchargement.

Définir le chemin vers le modèle local dans PowerShell :

    $env:PALABRE_OGAAL_MODEL_DIR = "C:\Models\Ogaal-ASR"

Pour forcer Ogaal, définir PALABRE_ASR_ENGINE=ogaal. Pour conserver faster-whisper avec le lexique, définir PALABRE_ASR_ENGINE=whisper. La valeur par défaut auto choisit Ogaal seulement si le répertoire configuré existe ; sinon, elle utilise faster-whisper. Ogaal peut être trop lourd pour certains PC. Le modèle doit être présent localement et le mode local_files_only est utilisé. Aucun enregistrement ne part vers une API distante.

## Enrichissement progressif du somali

Le lexique de départ dans backend/heritage/somali_lexicon.json est volontairement petit. Il peut être enrichi avec des termes vérifiés provenant de dictionnaires, corpus et standards somalis, après contrôle des licences et de la qualité linguistique. Les ressources candidates à examiner comprennent :

- somastllc/somali-language-standard pour l'orthographe et la terminologie ;
- yahyaqowle/Afsoomali pour le vocabulaire ;
- maktabadda/erey.ga pour les mots et expressions culturelles ;
- somastllc/somali-nlp-corpus pour des exemples textuels dédupliqués.
- somastllc/SomNLP-Translate et asmelashteka/HornMT sont conservés comme pistes de recherche pour d’éventuels corpus parallèles, mais ne sont pas intégrés ici : cette modification enrichit uniquement les mots somalis et n’ajoute aucune traduction.

Aucune base tierce complète n'est copiée dans le dépôt par cette modification. Le lexique sert uniquement d'indice lexical de reconnaissance et d'annotation. Il ne normalise pas la parole originale ni ne transforme une variante dialectale en erreur.

## Validation et tests

Depuis la racine :

    python -m unittest discover -s backend/heritage -p "test_*.py" -v

Les tests automatisés valident le comportement du lexique et les protections, mais ne mesurent pas la précision acoustique. Avant adoption définitive, comparer Ogaal et faster-whisper sur des extraits non sensibles avec autorisation, mesurer WER/CER et faire relire les résultats par des locuteurs somalis. Ne jamais utiliser des récits confidentiels pour une évaluation externe.


## Comparer les deux moteurs sur Windows (calcul entièrement local)

Préparer un court extrait somali non sensible, avec consentement, et un fichier texte de référence relu par un locuteur somali. Les deux modèles doivent déjà exister sur le disque. Le dossier faster-whisper doit être au format CTranslate2 ; le dossier Ogaal doit contenir les fichiers du modèle Hugging Face. Le script n'envoie ni audio ni transcription vers Internet.

Depuis la racine du dépôt, dans l'environnement Python où les dépendances des deux moteurs sont installées :

    python scripts/evaluate_somali_asr.py --audio "C:\audio\extrait.wav" --reference "C:\audio\reference.txt" --ogaal-model "C:\Models\Ogaal-ASR" --whisper-model "C:\Models\faster-whisper-small" --report "C:\audio\rapport-comparaison.json"

Le rapport contient le WER (taux d'erreur de mots), le CER (taux d'erreur de caractères), la durée et les mots somalis repérés. Plus les taux WER/CER sont faibles, mieux la transcription correspond au texte de référence. Tester plusieurs locuteurs et plusieurs extraits avant de conclure ; ne jamais utiliser une transcription automatique comme vérité de référence. Le rapport ne conserve ni le son ni le texte de référence ; il stocke uniquement les mesures, les noms de fichiers et les mots somalis repérés.
