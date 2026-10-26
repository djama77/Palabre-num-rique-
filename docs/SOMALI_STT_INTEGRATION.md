# Intégration candidate — Speech-To-Text pour le somali

## Objectif

Évaluer le dépôt public [ichillous/Speech-To-Text-For-The-Somali-Language](https://github.com/ichillous/Speech-To-Text-For-The-Somali-Language) comme piste complémentaire pour améliorer la transcription des témoignages oraux somalis dans PALABRE NUMÉRIQUE.

## Ce que montre actuellement le dépôt source

Le README décrit surtout un projet de recherche et une feuille de route :
- constituer des enregistrements somalis transcrits ;
- construire un dictionnaire phonétique ;
- construire un modèle de langue ;
- développer un modèle acoustique.

Le README marque la collecte d'enregistrements comme accomplie, mais les étapes du dictionnaire phonétique, du modèle de langue et du modèle acoustique restent indiquées comme non achevées. Le dépôt contient aussi un document de recherche sur l'utilisation de réseaux de neurones convolutifs pour la reconnaissance vocale somalie.

**Conclusion provisoire :** ne pas considérer ce dépôt comme un moteur de transcription prêt à brancher en production sans examiner les fichiers, les dépendances, les modèles réellement disponibles et les résultats reproductibles.

## Plan d'évaluation et d'intégration

1. **Audit technique**
   - Inventorier les scripts, notebooks, données, dictionnaires et éventuels poids de modèle.
   - Identifier les dépendances, la version de Python, les exigences CPU/GPU et les formats audio attendus.
   - Vérifier si le dépôt fournit une fonction d'inférence utilisable, ou seulement du matériel de recherche.

2. **Vérification des droits**
   - Vérifier la présence et le contenu d'une licence explicite dans le dépôt source.
   - Tant qu'une licence autorisant la réutilisation n'est pas confirmée, ne pas copier ni redistribuer son code, ses données ou ses modèles.
   - Enregistrer les attributions et licences de chaque composant retenu.

3. **Architecture dans PALABRE NUMÉRIQUE**
   - Ajouter, si l'audit le permet, un fournisseur optionnel nommé `SomaliResearchSTTProvider` derrière l'interface commune des fournisseurs audio.
   - **Conserver obligatoirement le fournisseur existant fondé sur faster-whisper comme moteur principal de transcription.** Ne pas le supprimer, le remplacer ni le désactiver.
   - VoiceStudio et tout composant issu du projet de recherche somali restent facultatifs et complémentaires ; ils ne peuvent être évalués qu'en comparaison avec Whisper, sans modifier le fonctionnement par défaut.
   - Toute activation éventuelle d'un moteur expérimental doit être explicite, réversible et accompagnée d'un mécanisme de retour immédiat à faster-whisper.
   - Ne pas faire dépendre l'application principale de ce dépôt tant que son exécution n'est pas reproductible.
   - Conserver les enregistrements originaux et associer chaque transcription à la provenance du moteur, sa version et son statut de validation humaine.

4. **Évaluation linguistique**
   - Constituer un petit corpus de validation dont les locuteurs ont donné leur consentement.
   - Faire transcrire les mêmes extraits par le moteur actuel et par tout modèle candidat.
   - Mesurer le WER (taux d'erreur de mots), inspecter les noms propres, les variantes dialectales et les mots patrimoniaux.
   - Faire corriger les transcriptions par une personne maîtrisant le somali avant publication.

5. **Critères d'acceptation**
   - Installation reproductible et tests automatisés réussis.
   - Résultats mesurés sur un corpus de validation documenté.
   - Aucune perte ou modification de l'audio original.
   - Validation humaine avant publication d'une transcription patrimoniale.
   - Licences et provenance des données/modèles documentées.

## État

Décision d'architecture : faster-whisper reste le moteur principal et le comportement par défaut de PALABRE NUMÉRIQUE. VoiceStudio et le projet Somali STT sont des pistes complémentaires et facultatives. Cette note prépare l'évaluation. Elle n'affirme pas que le code source a été importé, que le modèle fonctionne, ni qu'un benchmark a été exécuté. Les tests et l'intégration applicative restent à réaliser après l'audit technique et juridique.
