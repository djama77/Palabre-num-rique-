# Corpus de référence — Xeer-Ciise

Ce dossier prépare l'usage du document Xeer Dhaqameed comme source documentaire pour la transcription somalie et le prototype local Xeer-Yaqaan.

## Fichiers PDF présents dans la branche de travail

Trois PDF compressés sont actuellement enregistrés dans ce dossier :

- `extracted-xeer_dhaqameed-compressed.pdf` — 10 334 429 octets
- `extracted-xeer_dhaqameed (1)-compressed.pdf` — 10 683 795 octets
- `extracted-xeer_dhaqameed (2)-compressed.pdf` — 11 168 248 octets

Chaque fichier est inférieur à 25 Mo. Les noms et tailles ont été vérifiés dans l'API GitHub. En revanche, le nombre de pages, la continuité entre les parties, l'absence de pages manquantes et la fidélité au PDF d'origine restent à vérifier en ouvrant les fichiers et en comparant les pages. Ne pas supposer leur ordre à partir des seuls noms.

**Droits de diffusion : à confirmer.** Avant toute fusion ou diffusion publique, confirmez que vous avez le droit de reproduire et de publier ces fichiers. Ils sont actuellement présents sur la branche de travail de la pull request.

## État du corpus

- Le texte OCR n'est pas encore généré ni validé.
- Ne présentez pas les résultats OCR comme une transcription fiable avant comparaison avec les pages scannées.
- Les noms propres, termes coutumiers, citations et numéros de page doivent être vérifiés avec le document et, si nécessaire, par une personne compétente en somali et en Xeer-Ciise.
- Le glossaire doit être construit à partir de la source puis vérifié humainement.

## Préparer le texte OCR

Depuis la racine du dépôt, après installation d'OCRmyPDF et de Poppler :

```powershell
python backend/heritage/prepare_xeer_pdf.py "CHEMIN_VERS_LE_PDF.pdf" "data/xeer-cisse/ocr/xeer-cisse.txt" --language eng
```

Si un modèle Tesseract pour le somali est installé, essayez `--language som`. Le nom de langue doit correspondre à un modèle réellement installé. Vérifiez le résultat OCR page par page avant toute utilisation documentaire.

Le fichier texte doit contenir des marqueurs tels que `[[PAGE 1]]`, un par page. Le numéro correspond à la page PDF, pas nécessairement au numéro imprimé dans le livre.

## Xeer-Yaqaan

`backend/heritage/xeer_yaqaan.py` effectue une recherche locale simple dans le texte OCR et retourne des extraits avec les numéros de page PDF. Il ne génère pas encore de réponses par un grand modèle de langage et ne remplace pas un spécialiste. Si aucun extrait ne correspond, il indique qu'aucune preuve n'a été trouvée dans l'index.

## Vocabulaire de transcription

Le glossaire doit être créé à partir du PDF après OCR et vérification humaine. Les mots suggérés dans des descriptions ou des conversations ne doivent pas être marqués comme validés sans contrôle dans la source. Un prompt Whisper peut aider à reconnaître des termes, mais ne doit jamais remplacer ou corriger silencieusement ce qui est réellement audible.
