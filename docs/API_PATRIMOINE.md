# API locale de consultation du patrimoine — prototype

L'API est volontairement **en lecture seule** : elle n'autorise ni création de récits, ni validation par les Sages, ni publication. Les opérations administratives devront être implémentées plus tard avec une authentification et des autorisations serveur.

## Démarrage local (Python 3.11+)
Depuis le dossier `backend/heritage` :

```bash
python api.py
```

Endpoints :
- `GET http://127.0.0.1:8765/api/health`
- `GET http://127.0.0.1:8765/api/heritage/public`
- `GET http://127.0.0.1:8765/api/heritage/public/<id>`

Le fichier SQLite est créé automatiquement à côté du script, sauf si `PALABRE_DB_PATH` définit un chemin différent. Ne pas stocker les enregistrements audio ou les données sensibles dans un dépôt Git.

## Sécurité
- Par défaut, le serveur écoute uniquement sur `127.0.0.1` (ordinateur local).
- Ne pas définir `PALABRE_HOST=0.0.0.0` sur Internet sans reverse proxy TLS, contrôle d'accès, limites de requêtes et supervision.
- L'API ne retourne jamais le chemin du fichier audio original, ni l'historique de validation.
- Seuls les récits **validés et publics** sont visibles.
- Les règles de consentement, de révocation, de versionnage et de confidentialité doivent être renforcées avant usage réel.
- Aucune clé ElevenLabs n'est exposée et aucun service IA distant n'est appelé par cette API.

## Vérification
```bash
python -m unittest discover -s . -p "test_*.py" -v
```
