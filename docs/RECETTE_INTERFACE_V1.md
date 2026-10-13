# Recette technique — interface de consultation V1

## Tests automatisés
Le workflow existant `Heritage and voice unit tests` découvre les fichiers `backend/heritage/test_*.py`. Le nouveau fichier `test_web_app.py` vérifie :
- la présence des contrôles de recherche, d'actualisation et de lecture vocale ;
- la disponibilité HTTP de la page locale ;
- la réponse JSON de l'API publique avec une base vide.

## Tests manuels sur PC
1. Depuis `backend/heritage`, lancer `python -m unittest discover -s . -p "test_*.py" -v`.
2. Lancer `python web_app.py` puis ouvrir `http://127.0.0.1:8765/`.
3. Vérifier le message « 0 récit(s) public(s) disponible(s) » lorsque la base est vide.
4. Vérifier que la recherche et « Actualiser » ne provoquent aucune erreur.
5. Ajouter uniquement un récit fictif de test, passé par les étapes de validation et publication ; vérifier son affichage. Ne pas utiliser de témoignage réel sans consentement.
6. Vérifier la lecture française sur un navigateur qui propose une voix française.
7. Vérifier qu'un récit non validé n'apparaît jamais dans l'API ni dans l'interface.

## Avant fusion et publication
Ne pas confondre la réussite des tests unitaires avec un audit de sécurité. L'application reste une bibliothèque **locale, en lecture seule**. Pour l'ouverture à Internet : TLS, authentification pour toute administration, gestion du consentement, contrôle des données publiées, journalisation et sauvegardes. Les appels Whisper, NLLB et ElevenLabs ne sont pas encore intégrés.
