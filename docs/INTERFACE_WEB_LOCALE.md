# Palabre numérique — interface de consultation locale

Une interface **réelle, en lecture seule**, est ajoutée dans `frontend/heritage/index.html`. Elle interroge l'API SQLite sur le même serveur et n'affiche que les récits validés et publics. Recherche locale en somali/français, affichage des traductions et lecture française via la synthèse vocale du navigateur. Aucun service ElevenLabs distant n'est requis.

## Lancer sur Windows (Python 3.11+)
1. Télécharger le dépôt ou la branche puis extraire le ZIP.
2. Ouvrir un terminal dans `backend/heritage`.
3. Exécuter `python web_app.py`.
4. Ouvrir `http://127.0.0.1:8765/` sur le même ordinateur.

La base SQLite est créée automatiquement. Elle sera vide tant qu'aucun récit n'aura été importé et validé : **aucune donnée de Sage n'est inventée ou préchargée**.

## Limites et confidentialité
- L'application ne permet pas encore l'enregistrement, l'import, la validation ou la traduction automatique.
- Les données privées, chemins audio et historiques de validation ne sont pas envoyés à l'interface.
- Ne pas ouvrir directement le fichier HTML via `file://` : il faut le serveur Python.
- Le serveur écoute `127.0.0.1` par défaut : l'interface n'est donc pas accessible depuis un autre téléphone.
- Avant déploiement public : authentification, rôles, HTTPS, politique de consentement et révocation, audit, migrations de base, sauvegardes, tests de sécurité et gestion de charge.
- Les voix françaises dépendent des capacités du navigateur ; le TTS ElevenLabs réel reste à connecter côté serveur.
