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
 cloud("cloud-status").textContent=error?error.message:create&&!data.session?"Vérifiez votre boîte e-mail pour confirmer votre compte.":"Connexion réussie.";
 if(!error)await palabreRefreshAuth();
}
cloud("cloud-login").onclick=()=>palabreLogin(false);
cloud("cloud-register").onclick=()=>palabreLogin(true);
cloud("cloud-logout").onclick=async()=>{await palabreDb.auth.signOut();await palabreRefreshAuth()};
palabreDb.auth.onAuthStateChange(()=>setTimeout(palabreRefreshAuth,0));
palabreRefreshAuth();
