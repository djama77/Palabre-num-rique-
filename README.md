# Palabre Numérique — Patrimoine oral d’Ali-Sabieh

**Palabre Numérique** est un projet de sauvegarde, de valorisation et de transmission du patrimoine oral et coutumier d’Ali-Sabieh (Djibouti). Il vise à préserver les récits des Sages dans leur langue originale, à organiser une validation humaine et à permettre une consultation pédagogique des contenus autorisés.

> **État du projet : prototype en développement.** Certains modules fonctionnent localement ; la disponibilité en production de l’authentification, des enregistrements, des sauvegardes cloud, de la transcription automatique et de la synthèse vocale distante doit être vérifiée séparément. Un déploiement réussi ne prouve pas ces fonctionnalités.

## Objectifs

- Conserver les témoignages et enregistrements **originaux en somali**, avec consentement et provenance.
- Proposer des transcriptions en somali, corrigées par des personnes compétentes.
- Préparer des traductions françaises et une diffusion soumise à la validation du Collège des Sages.
- Faciliter la recherche, la consultation, la transmission intergénérationnelle et la production de supports pédagogiques.
- Protéger les données culturelles sensibles, les droits des contributeurs et les restrictions de publication.

## Organisation du dépôt

| Chemin | Rôle |
| --- | --- |
| `frontend/heritage/index.html` | Interface web du patrimoine oral |
| `frontend/heritage/supabase-cloud.js` | Code d’intégration côté client Supabase |
| `frontend/heritage/supabase-config.example.js` | Exemple de configuration publique Supabase |
| `frontend/modules/heritage-audio.js` | Fonctions audio pour l’interface |
| `backend/heritage/web_app.py` | Serveur local HTTP et interface web |
| `backend/heritage/api.py` | API de consultation des récits publics |
| `backend/heritage/storage.py` | Persistance locale SQLite |
| `backend/heritage/workflow.py` | Cycle de vie et règles des récits |
| `backend/heritage/whisper_transcription.py` | Module de transcription locale Whisper |
| `backend/heritage/local_transcription.py` | Traitement de transcription locale |
| `backend/heritage/local_narration.py` | Fonctions de narration locale |
| `backend/voice/elevenlabs_tts.py` | Adaptateur Python ElevenLabs (pas une route web de production) |
| `elevenlabs-demo/index.html` | Démonstrateur de voix de navigateur, sans appel ElevenLabs |
| `docs/` | Architecture, API, sécurité, stockage, essais et guides |
| `.github/workflows/` | Tests automatisés GitHub Actions |

## Démarrage en local sur Windows

Prérequis : **Python 3.11 ou supérieur**. Le serveur et l’API de consultation reposent sur la bibliothèque standard Python.

1. Télécharger le dépôt via **Code → Download ZIP**, puis l’extraire.
2. Ouvrir un terminal dans le dossier du projet.
3. Lancer :

```powershell
cd backend/heritage
python web_app.py
```

4. Ouvrir **http://127.0.0.1:8765/** dans le navigateur du même ordinateur.

La base de données SQLite peut être créée automatiquement. Elle est vide si aucun récit n’a été importé et validé. Le serveur est conçu pour un usage **local** et non une exposition directe sur Internet.

### Transcription Whisper (optionnelle)

Dans le dossier `backend/heritage` :

```powershell
python -m pip install -r requirements-whisper.txt
```

L’utilisation d’un modèle de transcription peut demander un téléchargement initial et des ressources CPU/RAM. Sur une machine à 8 Go de RAM, commencer avec un modèle léger, puis corriger systématiquement la transcription somalie par un humain habilité. Voir [WHISPER_SOMALI.md](docs/WHISPER_SOMALI.md).

## Tests

Depuis la racine du projet :

```bash
python -m unittest discover -s backend/heritage -p "test_*.py" -v
```

Des workflows GitHub Actions sont présents dans `.github/workflows/`. Leur réussite doit être vérifiée dans l’onglet **Actions** ; les tests unitaires ne remplacent pas les essais réels sur navigateur et téléphone Android.

## Supabase et déploiement web

Le frontend comprend du code de connexion Supabase. L’exemple de configuration se trouve dans `frontend/heritage/supabase-config.example.js`. Pour un déploiement Vercel ou un autre hébergeur, identifier d’abord le point d’entrée web, les variables publiques attendues et le schéma de base de données réellement déployé.

**Sécurité :** utiliser uniquement une clé publique/publishable côté navigateur ; ne jamais publier une clé `service_role`, un secret serveur ou une clé ElevenLabs. Mettre en place les politiques **Row Level Security (RLS)** et tester, pour chaque rôle, la connexion, l’enregistrement, la lecture, la sauvegarde et les restrictions d’accès avant une ouverture publique.

Le serveur Python SQLite local et l’intégration cloud Supabase sont deux modes distincts : leurs données ne sont **pas automatiquement synchronisées**.

## Parcours de préservation proposé

1. Obtenir le consentement du détenteur du récit.
2. Capturer l’audio original en somali et conserver sa provenance.
3. Produire une transcription en brouillon (Whisper facultatif).
4. Corriger la transcription et, si nécessaire, préparer la traduction française.
5. Faire valider le contenu et son niveau de diffusion par le Collège des Sages.
6. Publier uniquement les éléments autorisés ; conserver les archives restreintes hors consultation publique.
7. Proposer l’écoute originale et, si autorisée, une narration de la traduction clairement identifiée comme voix synthétique.

La transcription ou la traduction automatique **ne constitue jamais une validation** du récit.

## Fonctionnalités à vérifier / compléter avant production

- Authentification et autorisations applicables aux opérations d’écriture.
- Enregistrement sur Android et compatibilité des permissions micro.
- Sauvegarde effective et lecture après reconnexion à Supabase.
- Déploiement Vercel, routage et configuration des variables d’environnement.
- Gestion des consentements, révocations, sauvegardes, journal d’audit et accès restreints.
- Intégration contrôlée de Whisper et de la traduction, avec validation humaine.
- Route serveur sécurisée pour ElevenLabs, si ce service facultatif est retenu.

## Documentation

Consulter [l’architecture vocale](docs/ARCHITECTURE_PALABRE_VOIX.md), [l’API](docs/API_PATRIMOINE.md), [le stockage](docs/STOCKAGE_PATRIMOINE.md), [l’interface locale](docs/INTERFACE_WEB_LOCALE.md), [la transcription somalie](docs/WHISPER_SOMALI.md), [l’intégration ElevenLabs](docs/ELEVENLABS_INTEGRATION.md) et [la recette audio](docs/RECETTE_AUDIO.md).

## Projet

- **Dépôt GitHub :** https://github.com/djama77/Palabre-num-rique-
- **Territoire de référence :** Ali-Sabieh, République de Djibouti.
- **Vocation :** archivage patrimonial, transmission intergénérationnelle et consultation de récits autorisés.

**Respect culturel :** aucun témoignage, voix ou information sensible ne doit être publié ou transmis à un service externe sans autorisation appropriée.
