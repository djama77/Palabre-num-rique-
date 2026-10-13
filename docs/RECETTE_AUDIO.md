# Vérification du module de restitution — Palabre numérique

## Statut
Module de restitution front-end créé dans `frontend/modules/heritage-audio.js`. Il n'est pas encore intégré à une page existante.

## Exemple d'intégration (application JavaScript moderne)

```js
import { mountHeritageAudio } from "./modules/heritage-audio.js";
const dispose = mountHeritageAudio(document.querySelector("#recit-audio"), {
  title_so: "Titre du récit",
  translation_fr: "Texte français relu et validé",
  original_audio_url: "https://example.org/audio-autorise.mp3",
  validation_status: "validated",
  access_level: "public"
});
// dispose() lorsque la page se ferme.
```

La valeur `validation_status` fournie par le navigateur n'est **pas** une autorisation : l'API serveur doit vérifier le statut et les droits d'accès à partir de la base avant de fournir l'URL audio ou la traduction.

## Scénarios de recette
- Récit non validé : aucun texte ni audio ne doit être affiché.
- Récit privé : aucun texte ni audio ne doit être affiché.
- Récit public et validé : titre, original si présent, lecture française si traduction disponible.
- Navigateur sans synthèse vocale : message explicite, pas de crash.
- Bouton Arrêter : annule la lecture.
- Réseau indisponible : l'original distant ne sera pas accessible ; la synthèse navigateur peut dépendre des voix installées.
- Vérifier avec les Sages la prononciation, les droits de diffusion, et la distinction claire entre voix authentique et synthétique.

## Points bloquants
Le framework réel, le backend et le schéma de la base du dépôt ne sont pas encore identifiés. Ne pas fusionner avant ces vérifications et l'exécution des tests.
