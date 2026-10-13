# Bouton « Transcrire l'enregistrement »

L'interface affiche un bouton compréhensible, sans mention du moteur de transcription.

## Démarrer sur PC Windows
```powershell
cd backend/heritage
python -m pip install -r requirements-whisper.txt
python web_app.py
```
Ouvrir http://127.0.0.1:8765/ sur **le même ordinateur**. Sélectionner un fichier audio en somali, cocher la confirmation du consentement, puis cliquer sur **Transcrire l'enregistrement**.

La première utilisation télécharge le modèle. L'audio est temporairement copié dans un fichier local, supprimé après le traitement. Le résultat est affiché dans le navigateur et **n'est pas automatiquement enregistré dans la base ni publié**. La page ne fournit pas de fonctionnalité de correction collaborative ou de stockage des résultats.

**Sécurité** : cet outil est réservé à une utilisation locale sur le PC de l'opérateur. Ne pas exposer ce serveur sur Internet, un réseau local, un tunnel ou un proxy. Les contrôles d'origine et de consentement sont des protections de base, pas une authentification administrateur. La qualité de transcription doit être vérifiée manuellement.
