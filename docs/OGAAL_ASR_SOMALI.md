# Reconnaissance somalie locale et enrichissement lexical

## Ce qui change

- faster-whisper reste disponible et reçoit un initial_prompt constitué exclusivement de mots somalis du lexique local.
- Ogaal-ASR est pris en charge comme moteur local alternatif, fondé sur Whisper large-v3 affiné pour le somali. Il n'est activé automatiquement que si son modèle est déjà présent sur le disque ; aucun téléchargement n'est déclenché par l'application.
- Le lexique ajoute les métadonnées mots_somali à la réponse. Le texte transcrit reste strictement inchangé : pas de traduction, pas de correction automatique et aucune nouvelle commande ou aucun bouton dans l'interface.
- Les fichiers audio originaux restent intacts. La transcription demeure un brouillon qui doit être relu par une personne compétente.

## Ogaal-ASR hors ligne sous Windows

Le code du projet Ogaal-ASR est sous Apache-2.0. Le modèle et ses dépendances doivent être installés séparément, et leur licence/version doit être vérifiée avant distribution. Préparer le modèle une seule fois sur une machine autorisée, puis copier les fichiers du modèle sur l'ordinateur hors ligne.

Définir le chemin vers le modèle local dans PowerShell :

    $env:PALABRE_OGAAL_MODEL_DIR = "C:\Models\Ogaal-ASR"

Pour forcer Ogaal, définir PALABRE_ASR_ENGINE=ogaal. Pour conserver faster-whisper avec le lexique, définir PALABRE_ASR_ENGINE=whisper. La valeur par défaut auto choisit Ogaal seulement si le répertoire configuré existe ; sinon, elle utilise faster-whisper. Ogaal nécessite PyTorch, Transformers et les dépendances audio ; il peut être trop lourd pour certains PC. Le modèle doit être présent localement et le mode local_files_only est utilisé.

## Enrichissement progressif du somali

Le lexique de départ dans backend/heritage/somali_lexicon.json est volontairement petit. Il peut être enrichi plus tard avec des termes vérifiés provenant de dictionnaires, corpus et standards somalis, après contrôle des licences et de la qualité linguistique. Les ressources candidates à examiner comprennent :

- somastllc/somali-language-standard pour l'orthographe et la terminologie ;
- yahyaqowle/Afsoomali pour le vocabulaire ;
- maktabadda/erey.ga pour les mots et expressions culturelles ;
- somastllc/somali-nlp-corpus pour des exemples textuels dédupliqués.

Aucune base tierce complète n'est copiée dans le dépôt par cette modification. Le lexique sert uniquement d'indice lexical de reconnaissance et d'annotation. Il ne doit pas normaliser la parole originale ni transformer une variante dialectale en erreur.

## Validation et tests

Depuis la racine :

    python -m unittest discover -s backend/heritage -p "test_*.py" -v

Les tests automatisés valident le comportement du lexique et les protections, mais ne mesurent pas la précision acoustique. Avant adoption définitive, comparer Ogaal et faster-whisper sur des extraits non sensibles avec autorisation, mesurer WER/CER et faire relire les résultats par des locuteurs somalis. Ne jamais utiliser des récits confidentiels pour une évaluation externe.
