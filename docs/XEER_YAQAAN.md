# Xeer-Yaqaan — intégration progressive

## Objectif

Ajouter à Palabre Numérique une aide à la transcription somalie et un outil de
consultation documentaire pour le Xeer-Ciise, tout en gardant le PDF source,
les transcriptions et les réponses de recherche clairement distincts.

## Première tranche livrée

1. \`backend/heritage/prepare_xeer_pdf.py\` prépare un PDF scanné en texte OCR
   avec marqueurs de page. Il utilise OCRmyPDF et Poppler installés localement.
2. \`backend/heritage/xeer_yaqaan.py\` recherche les passages pertinents dans
   le texte OCR et retourne les numéros de page PDF et les extraits.
3. \`backend/heritage/test_xeer_yaqaan.py\` vérifie la récupération par page,
   l'exigence de marqueurs et l'absence de réponse inventée quand aucun extrait
   ne correspond.
4. \`data/xeer-cisse/README.md\` documente le corpus et les limites.

## Transcription Whisper

Le moteur Whisper reste un outil de brouillon. Une liste de termes du livre
pourra être fournie comme \`initial_prompt\` après vérification du glossaire.
Ce prompt est une aide à la reconnaissance, pas une source de vérité : aucune
correction automatique ne doit modifier la transcription sans écoute et
validation humaine.

## Source et citations

- Une réponse documentaire future devra présenter les extraits utilisés et
  leurs numéros de page.
- Le numéro fourni est celui de la page PDF. Il peut différer de la pagination
  imprimée.
- Si l'OCR est illisible, si aucune source pertinente n'est retrouvée ou si
  les sources se contredisent, l'outil doit le dire explicitement.
- Les connaissances générales, les témoignages oraux non vérifiés et le
  contenu de la description promotionnelle doivent être séparés du texte du
  livre.
- Aucun résultat de recherche ne doit valider ou publier automatiquement un
  récit patrimonial.

## Vérifications locales

Depuis \`backend/heritage\` :

\`\`\`powershell
python -m unittest discover -s . -p "test_*.py" -v
\`\`\`

Le moteur de recherche documentaire n'exige pas de dépendance Python externe.
L'OCR requiert les commandes système \`ocrmypdf\` et \`pdftotext\`.

## Étapes suivantes

1. OCR du PDF réel et contrôle humain de la qualité.
2. Construction d'un glossaire somali à partir du livre, avec statut de
   vérification et références de pages.
3. Intégration du glossaire au prompt Whisper, sans réécriture automatique.
4. Ajout d'un panneau Xeer-Yaqaan dans l'interface web, avec recherche et
   affichage des extraits et pages.
5. Si un modèle génératif est ajouté plus tard, le limiter aux passages
   récupérés, afficher les citations et répondre « source insuffisante » en
   l'absence de preuve.
