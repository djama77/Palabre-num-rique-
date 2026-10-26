# Protocole prototype — transcription et narration

## État
Ce protocole est prêt à exécuter localement. Les mesures réelles restent en attente : les fichiers audio non sensibles et la machine de test doivent être fournis/exécutés sur l'environnement de l'utilisateur. Ne pas présenter de scores hypothétiques comme des résultats.

## Échantillon
- 3 à 5 extraits autorisés et non sensibles, idéalement 30 à 120 secondes chacun.
- Couvrir une voix claire, un débit naturel et un extrait avec bruit ambiant.
- Utiliser la même copie des fichiers pour chaque moteur.
- Calculer et noter le SHA-256 de chaque original avant et après traitement.
- Pour la transcription de référence, faire corriger chaque extrait par une personne compétente en somali.

## Comparaison transcription
Tester le moteur existant faster-whisper (`tiny`, puis `small` si la machine le permet) et un moteur VoiceStudio clairement identifié comme compatible avec le somali. Ne pas supposer qu'un moteur présenté comme multilingue traite correctement le somali.

Mesures à consigner :
- modèle, version, OS, CPU, RAM, GPU/VRAM ;
- durée audio, temps de traitement, ratio temps/audio ;
- texte de référence corrigé ;
- erreurs de noms propres, négations, chiffres, expressions coutumières ;
- WER/CER si une normalisation convenue est disponible ;
- corrections humaines nécessaires et appréciation de la lisibilité.

Pour un calcul WER : WER = (substitutions + suppressions + insertions) / nombre de mots de référence. Normaliser seulement les différences convenues (espaces/ponctuation) ; conserver les noms et mots locaux pour l'évaluation.

## Comparaison narration
Comparer le TTS navigateur existant, l'adaptateur ElevenLabs déjà présent si une clé autorisée est configurée, et une voix locale VoiceStudio. Utiliser un texte français public/autorisé de 100 à 300 mots.

Noter : durée de génération, durée du résultat, intelligibilité, prononciation des noms somalis, prosodie, taille du fichier, dépendance Internet, consommation RAM/VRAM, coûts éventuels. Ne pas cloner la voix d'une personne réelle sans consentement explicite documenté.

## Fiche de résultat
| Extrait/moteur | OS/CPU/RAM/GPU | Durée audio | Temps traitement | WER/CER ou score de revue | Erreurs critiques | Mémoire max | Original SHA-256 inchangé |
|---|---|---:|---:|---|---|---|---|
| À remplir | À remplir | | | | | | |

## Conditions de réussite
- Aucun original modifié ou écrasé.
- Aucune transmission vers un service distant sans consentement et information explicite.
- La sortie automatique est toujours un brouillon.
- Le moteur retenu doit être mesurablement acceptable sur les extraits réels.
- Documenter l'installation, le modèle et la configuration pour reproduire le test.

## Validation des accès et erreurs
- Pas de consentement => refus.
- Requête distante sur le serveur local => refus.
- Origine/Host non autorisés => refus.
- Extension/type/taille invalides => refus.
- Moteur absent ou erreur de modèle => erreur contrôlée, aucune publication.
- Récit non validé ou non public => aucune narration publique.
- Vérifier que le fichier temporaire d'upload est supprimé et que le SHA-256 de l'original reste identique.
- Les tests unitaires ne remplacent pas les essais manuels sur Windows et Android.

## Pourquoi VoiceStudio n'est pas encore appelé directement
VoiceStudio annonce une API locale, mais ses routes, son authentification, son format de requête et les capacités du moteur installé doivent être vérifiés dans la documentation de la version exécutée. Cette intégration n'invente donc pas d'endpoint. Le fournisseur sera ajouté après test réel du contrat API.
