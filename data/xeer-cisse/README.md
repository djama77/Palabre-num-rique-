# Corpus de référence — Xeer-Ciise

Ce dossier prépare l'usage du PDF Xeer-Ciise comme source documentaire pour
la transcription somalie et le prototype local Xeer-Yaqaan.

## État initial

- Le PDF original est conservé séparément et n'est pas ajouté au dépôt.
- Le texte OCR n'est pas encore validé : ne pas présenter les résultats OCR
  comme une transcription fiable du livre.
- Les noms propres, termes coutumiers, citations et numéros de page doivent
  être vérifiés par comparaison avec les pages scannées et, si nécessaire,
  par une personne compétente en somali et en Xeer-Ciise.
- N'ajoutez ici que des fichiers dont vous avez le droit de reproduire et
  distribuer le contenu.

## Préparer le texte OCR

Depuis la racine du dépôt, après installation d'OCRmyPDF et de Poppler :

\`\`\`powershell
python backend/heritage/prepare_xeer_pdf.py "CHEMIN_VERS_LE_PDF.pdf" "data/xeer-cisse/ocr/xeer-cisse.txt" --language eng
\`\`\`

Si un modèle Tesseract pour le somali est installé, essayez \`--language som\`.
Le nom de langue doit correspondre à un modèle réellement installé. Vérifiez
le résultat OCR page par page avant toute utilisation documentaire.

Le fichier texte doit contenir des marqueurs tels que \`[[PAGE 1]]\`, un par
page. Le numéro correspond à la page PDF, pas nécessairement au numéro imprimé
dans le livre.

## Xeer-Yaqaan

\`backend/heritage/xeer_yaqaan.py\` effectue une recherche locale simple dans
le texte OCR et retourne des extraits avec les numéros de page PDF. Il ne
génère pas encore de réponses par un grand modèle de langage et ne remplace
pas un spécialiste. Si aucun extrait ne correspond, il indique qu'aucune
preuve n'a été trouvée dans l'index.

## Vocabulaire de transcription

Le glossaire doit être créé à partir du PDF après OCR et vérification humaine.
Les mots suggérés dans des descriptions ou des conversations ne doivent pas
être marqués comme validés sans contrôle dans la source. Un prompt Whisper
peut aider à reconnaître des termes, mais ne doit jamais remplacer ou
corriger silencieusement ce qui est réellement audible.
