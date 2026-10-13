# Lecture audio naturelle — Palabre numérique

Le bouton visible est **« Écouter le récit »**. Il lit la traduction française d'un récit **déjà publié**. Aucune validation des Sages n'est requise.

## Configuration Windows (PowerShell)

```powershell
$env:ELEVENLABS_API_KEY="VOTRE_CLE_PRIVEE"
$env:ELEVENLABS_VOICE_ID="IDENTIFIANT_DE_VOIX"
cd backend/heritage
python web_app.py
```

Ouvrir http://127.0.0.1:8765/ et cliquer sur « Écouter le récit » d'une fiche publiée contenant une traduction française. Le service nécessite Internet et peut consommer des crédits ElevenLabs. Choisir une voix disponible dans votre compte ElevenLabs.

**Sécurité et confidentialité** : la clé API reste sur le serveur, jamais dans le HTML ni GitHub. Le texte français publié est transmis à ElevenLabs lors de la génération. Les enregistrements originaux ne sont pas transmis. La fonctionnalité n'est autorisée que sur le serveur local et ne doit pas être exposée publiquement sans authentification, quotas, et contrôle des coûts. Si ElevenLabs est indisponible, le navigateur tente sa synthèse vocale intégrée.

Le moteur existant `backend/voice/elevenlabs_tts.py` utilise l'API officielle de synthèse vocale. Ne jamais committer une clé API.
