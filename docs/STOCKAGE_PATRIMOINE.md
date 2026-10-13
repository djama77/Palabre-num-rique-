# Stockage du patrimoine oral — étape SQLite

Ce module ajoute une persistance **locale** avec SQLite, cohérente avec le prototype hors ligne envisagé pour Ali-Sabieh. Le fichier `backend/heritage/storage.py` sauvegarde les métadonnées, transcriptions, traductions et historiques de validation. Les enregistrements audio originaux restent des fichiers protégés, référencés par leur chemin ; ils ne sont jamais intégrés à GitHub.

## Utilisation
Depuis le répertoire `backend/heritage` :

```bash
python -m unittest discover -s . -p "test_*.py" -v
```

L'API serveur doit authentifier les utilisateurs et déterminer leurs rôles. Ne jamais accepter depuis le navigateur `is_authorized_sage`, `publication_authorized` ou le statut de validation comme preuve de droit. Le composant `HeritageStorage` est une couche de persistance, **pas** une API publique sécurisée.

## Règles de publication
1. Consentement du détenteur de savoir.
2. Transcription en somali et contrôle humain.
3. Validation du Collège des Sages.
4. Autorisation explicite de publication.
5. Accès public limité aux champs validés ; audio original servi uniquement par une route autorisée.

## Limites à résoudre avant production
- L'implémentation actuelle emploie un modèle « dernier enregistrement gagnant » : ajouter contrôle de versions, transactions métier et journal d'audit append-only pour empêcher la modification non autorisée de statuts.
- Ajouter chiffrement au repos, sauvegardes, gestion des droits et suppression/révocation du consentement.
- Les champs texte peuvent contenir des informations personnelles : modération et revue avant diffusion.
- Définir les migrations vers PostgreSQL si l'usage devient multi-utilisateur.
- Aucune connexion réelle à Whisper, NLLB ou ElevenLabs n'est encore configurée.
