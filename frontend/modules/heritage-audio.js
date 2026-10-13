/** Palabre Numérique — optional read-aloud widget for validated heritage records.
 * No API key is exposed. Uses the original recording first; otherwise browser TTS.
 * For ElevenLabs production, connect a protected server endpoint only after authorization.
 */
export function mountHeritageAudio(container, record) {
  if (!(container instanceof HTMLElement)) throw new TypeError("Conteneur requis");
  if (!record || record.validation_status !== "validated" || record.access_level !== "public") {
    container.textContent = "Récit non disponible pour diffusion.";
    return () => {};
  }
  const audioUrl = record.original_audio_url;
  const title = document.createElement("h3");
  title.textContent = record.title_so || record.title_fr || "Récit validé";
  const original = document.createElement("audio");
  original.controls = true;
  original.preload = "none";
  if (typeof audioUrl === "string" && /^https:\/\//.test(audioUrl)) original.src = audioUrl;
  else original.hidden = true;
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = "Écouter la traduction française";
  const stop = document.createElement("button");
  stop.type = "button";
  stop.textContent = "Arrêter";
  const status = document.createElement("p");
  status.setAttribute("role", "status");
  button.addEventListener("click", () => {
    if (!("speechSynthesis" in window)) { status.textContent = "Lecture vocale indisponible."; return; }
    const text = String(record.translation_fr || "").trim();
    if (!text) { status.textContent = "Traduction française indisponible."; return; }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text.slice(0, 3000));
    utterance.lang = "fr-FR";
    utterance.rate = 0.85;
    utterance.onend = () => { status.textContent = "Lecture terminée."; };
    utterance.onerror = () => { status.textContent = "Erreur de lecture."; };
    window.speechSynthesis.speak(utterance);
    status.textContent = "Lecture de la traduction (voix synthétique).";
  });
  stop.addEventListener("click", () => {
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    original.pause();
    status.textContent = "Lecture arrêtée.";
  });
  container.replaceChildren(title, original, button, stop, status);
  return () => {
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    original.pause();
    container.replaceChildren();
  };
}
