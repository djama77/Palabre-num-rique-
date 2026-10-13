// Palabre numérique : client Supabase public (jamais de clé service_role).
const PALABRE_AUDIO_BUCKET="palabre-audio";
const PALABRE_SUPABASE_URL="https://ymcptudijtrnpchwvkqe.supabase.co";
const PALABRE_PUBLISHABLE_KEY="sb_publishable_Hkfpxv77XtO8eFTqH8qlFA_gi5p66ri";
const palabreDb=window.supabase.createClient(PALABRE_SUPABASE_URL,PALABRE_PUBLISHABLE_KEY);
