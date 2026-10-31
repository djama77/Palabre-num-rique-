// Palabre numérique — archivage automatique privé Supabase.
"use strict";
const PALABRE_AUDIO_BUCKET = "palabre-audio";
const PALABRE_SUPABASE_URL = "https://sdxkawuufsapcscbhfzl.supabase.co";
const PALABRE_PUBLISHABLE_KEY = "sb_publishable__fZrN9zq3qE7dvR7vKejdA_GS401U_t";
const palabreDb = window.supabase.createClient(PALABRE_SUPABASE_URL, PALABRE_PUBLISHABLE_KEY);
const cloud = (id) => document.getElementById(id);
let palabreUser = null;
let archiveBusy = false;

function cloudStatus(message) { cloud("cloud-status").textContent = message; }
function archiveStatus(message) { cloud("archive-save-status").textContent = message; }

function safeFileExtension(file) {
  const mime = (file.type || "").split(";")[0].toLowerCase();
  const known = {"audio/webm":"webm","audio/mp4":"m4a","audio/mpeg":"mp3","audio/wav":"wav","audio/x-wav":"wav","audio/ogg":"ogg","audio/flac":"flac","audio/aac":"aac"};
  if (known[mime]) return known[mime];
  const ext = (file.name || "").split(".").pop().toLowerCase();
  return ["webm","m4a","mp3","wav","ogg","flac","aac","opus"].includes(ext) ? ext : null;
}

async function palabreEnsureAnonymousSession() {
  cloudStatus("Création automatique de votre espace privé…");
  const {data: sessionData, error: sessionError} = await palabreDb.auth.getSession();
  if (sessionError) throw sessionError;
  let session = sessionData.session;
  if (!session) {
    const {data, error} = await palabreDb.auth.signInAnonymously();
    if (error) throw error;
    session = data.session;
  }
  if (!session || !session.user) throw new Error("La session privée n'a pas pu être créée.");
  palabreUser = session.user;
  cloud("cloud-user").textContent = "Espace privé prêt · connexion automatique";
  cloudStatus("Votre espace privé est prêt. Les transcriptions seront archivées automatiquement.");
  await palabreList();
}

async function palabreSaveTranscription() {
  if (archiveBusy) return;
  if (!palabreUser) { archiveStatus("Espace privé indisponible. Rechargez la page puis réessayez."); return; }
  const transcript = cloud("transcription-result").value.trim();
  const file = cloud("audio-file").files && cloud("audio-file").files[0];
  const title = cloud("transcription-title").value.trim() || ("Transcription du " + new Date().toLocaleString("fr-FR"));
  if (!transcript) { archiveStatus("Aucun texte à enregistrer."); return; }
  if (!file) { archiveStatus("Le fichier audio source est introuvable. Réimportez-le pour archiver la transcription."); return; }
  if (!cloud("audio-consent").checked) { archiveStatus("Le consentement est nécessaire pour archiver ce témoignage."); return; }
  const ext = safeFileExtension(file);
  if (!ext) { archiveStatus("Format audio non pris en charge pour l'archivage."); return; }
  if (file.size > 100 * 1024 * 1024) { archiveStatus("Fichier audio trop volumineux (100 Mo maximum)."); return; }
  archiveBusy = true;
  const saveButton = cloud("save-transcription");
  saveButton.disabled = true;
  archiveStatus("Sauvegarde de la transcription et de son audio dans Supabase…");
  const id = crypto.randomUUID();
  const path = palabreUser.id + "/" + id + "." + ext;
  const mime = (file.type || "application/octet-stream").split(";")[0];
  try {
    const {error: uploadError} = await palabreDb.storage.from(PALABRE_AUDIO_BUCKET).upload(path, file, {contentType:mime, upsert:false});
    if (uploadError) throw uploadError;
    const {error: insertError} = await palabreDb.from("palabre_records").insert({
      owner_id:palabreUser.id,
      title_so:title.slice(0,300),
      transcript_so:transcript,
      audio_path:path,
      consent_recorded:true,
      publication_authorized:false,
      status:"draft"
    });
    if (insertError) {
      await palabreDb.storage.from(PALABRE_AUDIO_BUCKET).remove([path]);
      throw insertError;
    }
    archiveStatus("Transcription sauvegardée avec succès dans vos archives privées.");
    saveButton.disabled = true;
    await palabreList();
  } catch (error) {
    archiveStatus("Sauvegarde impossible : " + (error.message || "erreur Supabase") + ". Votre texte reste affiché ; vous pouvez réessayer.");
    saveButton.disabled = false;
  } finally {
    archiveBusy = false;
  }
}

async function palabreList() {
  if (!palabreUser) return;
  const list = cloud("cloud-list");
  list.replaceChildren();
  const {data, error} = await palabreDb.from("palabre_records")
    .select("id,title_so,transcript_so,audio_path,created_at")
    .eq("owner_id", palabreUser.id)
    .order("created_at", {ascending:false})
    .limit(100);
  if (error) { cloudStatus("Impossible de charger les archives : " + error.message); return; }
  if (!data || !data.length) {
    const empty = document.createElement("p");
    empty.className = "empty muted";
    empty.textContent = "Aucune transcription archivée pour le moment. Après une transcription, elle sera enregistrée ici.";
    list.append(empty);
    cloudStatus("Votre espace privé est prêt · 0 archive.");
    return;
  }
  for (const item of data) {
    const article = document.createElement("article");
    const heading = document.createElement("h3");
    const date = document.createElement("p");
    const transcript = document.createElement("p");
    const listen = document.createElement("button");
    heading.textContent = item.title_so || "Transcription sans titre";
    date.className = "muted";
    date.textContent = item.created_at ? new Date(item.created_at).toLocaleString("fr-FR") : "";
    transcript.textContent = item.transcript_so || "Texte non disponible.";
    transcript.style.whiteSpace = "pre-wrap";
    listen.type = "button";
    listen.textContent = "Écouter l'audio original";
    listen.disabled = !item.audio_path;
    listen.addEventListener("click", async () => {
      listen.disabled = true;
      try {
        const {data:link, error:linkError} = await palabreDb.storage.from(PALABRE_AUDIO_BUCKET).createSignedUrl(item.audio_path, 60);
        if (linkError) throw linkError;
        const player = document.createElement("audio");
        player.controls = true;
        player.preload = "metadata";
        player.src = link.signedUrl;
        player.style.width = "100%";
        article.querySelector("audio")?.remove();
        article.append(player);
        await player.play().catch(() => {});
      } catch (error) { cloudStatus("Lecture impossible : " + error.message); }
      finally { listen.disabled = false; }
    });
    article.append(heading, date, transcript, listen);
    list.append(article);
  }
  cloudStatus(data.length + " transcription(s) privée(s) dans vos archives.");
}

cloud("archive-refresh").addEventListener("click", palabreList);
cloud("save-transcription").addEventListener("click", palabreSaveTranscription);
cloud("transcription-result").addEventListener("input", () => {
  cloud("save-transcription").disabled = !cloud("transcription-result").value.trim();
});
cloud("transcribe").addEventListener("click", () => { cloud("save-transcription").disabled = true; });
window.addEventListener("palabre:transcription-ready", () => { cloud("save-transcription").disabled = false; palabreSaveTranscription(); });
palabreDb.auth.onAuthStateChange((_event, session) => {
  if (session && session.user) {
    palabreUser = session.user;
    cloud("cloud-user").textContent = "Espace privé prêt · connexion automatique";
  }
});
palabreEnsureAnonymousSession().catch((error) => {
  cloud("cloud-user").textContent = "Espace privé non initialisé";
  cloudStatus("Activez les connexions anonymes dans Supabase Auth, puis rechargez la page. Détail : " + error.message);
});
