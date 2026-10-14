// Palabre numérique : client Supabase public (jamais de clé service_role).
const PALABRE_AUDIO_BUCKET="palabre-audio";
const PALABRE_SUPABASE_URL="https://ymcptudijtrnpchwvkqe.supabase.co";
const PALABRE_PUBLISHABLE_KEY="sb_publishable_Hkfpxv77XtO8eFTqH8qlFA_gi5p66ri";
const palabreDb=window.supabase.createClient(PALABRE_SUPABASE_URL,PALABRE_PUBLISHABLE_KEY);

const cloud=(id)=>document.getElementById(id);
let palabreUser=null;
async function palabreRefreshAuth(){
 const {data}=await palabreDb.auth.getUser();
 palabreUser=data.user;
 cloud("cloud-user").textContent=palabreUser?"Connecté : "+palabreUser.email:"Non connecté";
 cloud("cloud-save").disabled=!palabreUser;
 cloud("cloud-refresh").disabled=!palabreUser;
 cloud("cloud-logout").hidden=!palabreUser;
 if(!palabreUser)cloud("cloud-list").replaceChildren();
}
async function palabreLogin(create){
 const email=cloud("cloud-email").value.trim();
 const password=cloud("cloud-password").value;
 if(!email||!password){cloud("cloud-status").textContent="Indiquez votre e-mail et votre mot de passe.";return}
 const {data,error}=create?await palabreDb.auth.signUp({email,password}):await palabreDb.auth.signInWithPassword({email,password});
 cloud("cloud-password").value="";
 cloud("cloud-status").textContent=error?palabreAuthMessage(error):create&&!data.session?"Vérifiez votre boîte e-mail pour confirmer votre compte.":"Connexion réussie. Vous pouvez maintenant sauvegarder votre enregistrement.";
 if(!error){await palabreRefreshAuth();if(palabreUser)await palabreList();}
}
cloud("cloud-login").onclick=()=>palabreLogin(false);
cloud("cloud-register").onclick=()=>palabreLogin(true);
cloud("cloud-logout").onclick=async()=>{await palabreDb.auth.signOut();await palabreRefreshAuth()};
palabreDb.auth.onAuthStateChange(()=>setTimeout(palabreRefreshAuth,0));
palabreRefreshAuth();

cloud("cloud-save").onclick=async()=>{
 if(!palabreUser||!cloud("cloud-consent").checked){cloud("cloud-status").textContent="Connexion et consentement nécessaires.";return}
 const title=cloud("cloud-title").value.trim();
 const audio=(typeof recordBlob!=="undefined"&&recordBlob)||cloud("cloud-file").files[0];
 if(!title||title.length>300||!audio){cloud("cloud-status").textContent="Ajoutez un titre et un enregistrement.";return}
 if(audio.size>100*1024*1024){cloud("cloud-status").textContent="100 Mo maximum.";return}
 const mime=(audio.type||"").split(";")[0];
 const formats={"audio/webm":"webm","audio/mp4":"m4a","audio/mpeg":"mp3","audio/wav":"wav","audio/x-wav":"wav","audio/ogg":"ogg","audio/flac":"flac"};
 if(!formats[mime]){cloud("cloud-status").textContent="Format audio non pris en charge.";return}
 const uuid=globalThis.crypto?.randomUUID?crypto.randomUUID():Date.now()+"-"+Math.random().toString(16).slice(2);\n const path=palabreUser.id+"/"+uuid+"."+formats[mime];
 cloud("cloud-save").disabled=true;cloud("cloud-status").textContent="Sauvegarde privée en cours…";
 try{
  const {error:upload}=await palabreDb.storage.from(PALABRE_AUDIO_BUCKET).upload(path,audio,{contentType:mime,upsert:false});
  if(upload)throw upload;
  const {error:insert}=await palabreDb.from("palabre_records").insert({owner_id:palabreUser.id,title_so:title,audio_path:path,consent_recorded:true,publication_authorized:false,status:"draft"});
  if(insert){await palabreDb.storage.from(PALABRE_AUDIO_BUCKET).remove([path]);throw insert}
  cloud("cloud-status").textContent="Discussion sauvegardée dans votre espace privé.";
  await palabreList();
 }catch(error){cloud("cloud-status").textContent="Sauvegarde impossible : "+error.message}
 finally{cloud("cloud-save").disabled=!palabreUser}
};

async function palabreList(){
 if(!palabreUser)return;
 const {data,error}=await palabreDb.from("palabre_records").select("id,title_so,audio_path,created_at").eq("owner_id",palabreUser.id).order("created_at",{ascending:false}).limit(100);
 const list=cloud("cloud-list");list.replaceChildren();
 if(error){cloud("cloud-status").textContent="Liste indisponible : "+error.message;return}
 for(const item of data){
  const article=document.createElement("article"),heading=document.createElement("h3"),button=document.createElement("button");
  heading.textContent=item.title_so;button.type="button";button.textContent="Écouter";
  button.disabled=!item.audio_path;
  button.onclick=async()=>{
   const {data:link,error:err}=await palabreDb.storage.from(PALABRE_AUDIO_BUCKET).createSignedUrl(item.audio_path,60);
   if(err){cloud("cloud-status").textContent=err.message;return}
   article.querySelector("audio")?.remove();
   const player=document.createElement("audio");player.controls=true;player.preload="metadata";player.src=link.signedUrl;player.style.width="100%";player.addEventListener("error",()=>{cloud("cloud-status").textContent="Lecture impossible. Actualisez puis réessayez."});article.append(player);\n   try{await player.play()}catch(e){cloud("cloud-status").textContent="Appuyez sur ▶ pour lancer la lecture."}
  };
  article.append(heading,button);list.append(article);
 }
 cloud("cloud-status").textContent=data.length+" enregistrement(s) privé(s).";
}
cloud("cloud-refresh").onclick=palabreList;

async function palabrePublicLibrary(){
 const status=document.getElementById("status");
 status.textContent="Chargement de la bibliothèque…";
 const {data,error}=await palabreDb.from("palabre_records").select("id,title_so,translation_fr,status").eq("status","published").eq("consent_recorded",true).eq("publication_authorized",true).order("created_at",{ascending:false}).limit(100);
 if(error){status.textContent="Bibliothèque indisponible : "+error.message;return}
 records=(data||[]).map(item=>({id:item.id,title_so:item.title_so,translation_fr:item.translation_fr}));
 status.textContent=records.length+" récit(s) publié(s).";render();
}
document.getElementById("refresh").addEventListener("click",palabrePublicLibrary);
palabrePublicLibrary();
