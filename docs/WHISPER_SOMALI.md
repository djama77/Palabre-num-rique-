# Whisper somali — intégration locale V1

Cette branche ajoute un moteur de transcription **facultatif** pour les enregistrements des Sages, sans modifier l'API publique en lecture seule.

## Installation sur Windows
Depuis le dossier `backend/heritage` :

```powershell
python -m pip install -r requirements-whisper.txt
python -m unittest discover -s . -p "test_*.py" -v
```

Le modèle `small` est téléchargé à la première utilisation ; l'inférence ultérieure peut être locale. Sur un PC de 8 Go RAM, commencer avec `base` si `small` est trop lent. Le CPU avec `int8` ne requiert pas NVIDIA.

## Exemple pour un enregistrement autorisé
```python
from workflow import HeritageRecord
from whisper_transcription import transcrire_brouillon
from storage import HeritageStorage

record = HeritageRecord(
    id="essai-001",
    title_so="Récit de démonstration",
    original_audio_path="essai.wav",
    consent_recorded=True,
)
resultat = transcrire_brouillon(
    record,
    actor="operateur_habilite",
    audio_root="CHEMIN_VERS_DOSSIER_AUDIO_PRIVE",
    model_name="small",
)
HeritageStorage("heritage.sqlite3").save(record)
print(resultat["texte"])
```

Remplacer les chemins et identifiants fictifs. Les appels doivent être faits depuis un processus de confiance : `actor` est fourni par un système d'authentification réel, jamais directement par un navigateur. Les segments horodatés sont retournés en mémoire ; la base actuelle ne possède pas encore de table de segments dédiée.

## Garanties et limites
- Consentement vérifié avant traitement ; accès aux fichiers audio limité au dossier privé.
- Transcription uniquement des brouillons ; résultat reste privé, statut `transcribed`.
- La publication exige ensuite une revue et la validation du Collège des Sages.
- La qualité en somali varie : correction humaine obligatoire.
- Pas de traduction NLLB ni de connexion ElevenLabs dans ce module.
- Pas de route publique d'import ou d'exécution Whisper : l'authentification, le quota, le contrôle de durée et la supervision doivent être développés avant de l'exposer.
- Les tests unitaires simulent Whisper ; ils ne prouvent pas la qualité réelle de transcription.
