-- PALABRE NUMÉRIQUE · Schéma cible V1
-- IMPORTANT : schéma cible distinct de public.palabre_records actuellement utilisé par le frontend.
-- Ne pas appliquer avant inventaire du projet distant et adaptation/test du frontend.
begin;

do $$ begin
  create type public.app_role as enum ('collecteur','transcripteur','traducteur','sage','admin','audit');
exception when duplicate_object then null; end $$;
do $$ begin
  create type public.record_status as enum ('brouillon','transcription','revision','soumis','approuve','refuse','publie','retire');
exception when duplicate_object then null; end $$;
do $$ begin
  create type public.visibility_level as enum ('prive','restreint','public');
exception when duplicate_object then null; end $$;
do $$ begin
  create type public.review_kind as enum ('culturelle','diffusion');
exception when duplicate_object then null; end $$;
do $$ begin
  create type public.review_decision as enum ('approuve','refuse','a_corriger');
exception when duplicate_object then null; end $$;

create table if not exists public.user_roles (
  user_id uuid not null references auth.users(id) on delete cascade,
  role public.app_role not null,
  primary key (user_id, role)
);

create table if not exists public.records (
  id uuid primary key default gen_random_uuid(),
  title text not null check (length(trim(title)) between 1 and 300),
  language text not null default 'so',
  locality text,
  recorded_on date,
  holder_label text not null check (length(trim(holder_label)) > 0),
  collector_id uuid not null default auth.uid() references auth.users(id),
  status public.record_status not null default 'brouillon',
  visibility public.visibility_level not null default 'prive',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.assignments (
  record_id uuid not null references public.records(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  primary key (record_id, user_id)
);

create table if not exists public.consents (
  id uuid primary key default gen_random_uuid(),
  record_id uuid not null references public.records(id) on delete cascade,
  scope jsonb not null check (jsonb_typeof(scope) = 'object'),
  granted_at timestamptz not null default now(),
  revoked_at timestamptz,
  recorded_by uuid not null default auth.uid() references auth.users(id)
);

create table if not exists public.audio_assets (
  id uuid primary key default gen_random_uuid(),
  record_id uuid not null references public.records(id) on delete cascade,
  storage_path text not null unique,
  duration_s integer check (duration_s is null or duration_s >= 0),
  created_at timestamptz not null default now()
);

create table if not exists public.text_versions (
  id uuid primary key default gen_random_uuid(),
  record_id uuid not null references public.records(id) on delete cascade,
  kind text not null check (kind in ('transcription','traduction')),
  lang text not null,
  body text not null,
  origin text not null check (origin in ('whisper','humain')),
  human_reviewed boolean not null default false,
  author_id uuid default auth.uid() references auth.users(id),
  created_at timestamptz not null default now()
);

create table if not exists public.reviews (
  id uuid primary key default gen_random_uuid(),
  record_id uuid not null references public.records(id) on delete cascade,
  kind public.review_kind not null,
  decision public.review_decision not null,
  motive text not null check (length(trim(motive)) > 0),
  reviewer_id uuid not null default auth.uid() references auth.users(id),
  created_at timestamptz not null default now()
);

create table if not exists public.audit_events (
  id bigint generated always as identity primary key,
  actor_id uuid default auth.uid() references auth.users(id),
  action text not null,
  entity text not null,
  entity_id uuid,
  details jsonb,
  created_at timestamptz not null default now()
);

create index if not exists records_collector_created_idx on public.records(collector_id, created_at desc);
create index if not exists assignments_user_record_idx on public.assignments(user_id, record_id);
create index if not exists consents_record_active_idx on public.consents(record_id, granted_at desc) where revoked_at is null;
create index if not exists text_versions_record_kind_idx on public.text_versions(record_id, kind, created_at desc);
create index if not exists reviews_record_kind_idx on public.reviews(record_id, kind, created_at desc);

-- Fonctions internes d'autorisation : les rôles ne sont jamais lus depuis user_metadata modifiable.
create or replace function public.has_role(r public.app_role)
returns boolean language sql stable security definer
set search_path = '' as $$
  select exists (
    select 1 from public.user_roles
    where user_id = (select auth.uid()) and role = r
  );
$$;

create or replace function public.has_valid_consent(rid uuid, s text)
returns boolean language sql stable security definer
set search_path = '' as $$
  select exists (
    select 1 from public.consents c
    where c.record_id = rid
      and c.revoked_at is null
      and coalesce(c.scope ->> s, 'false') = 'true'
  );
$$;

create or replace function public.is_publishable(rid uuid)
returns boolean language sql stable security definer
set search_path = '' as $$
  select coalesce(
    public.has_valid_consent(rid, 'diffusion')
    and (select rv.decision = 'approuve' from public.reviews rv
         where rv.record_id = rid and rv.kind = 'culturelle'
         order by rv.created_at desc limit 1)
    and (select rv.decision = 'approuve' from public.reviews rv
         where rv.record_id = rid and rv.kind = 'diffusion'
         order by rv.created_at desc limit 1),
    false
  );
$$;

-- Fonction minimale utilisée par le catalogue public : elle ne renvoie qu'un booléen.
create or replace function public.is_public_record(rid uuid)
returns boolean language sql stable security definer
set search_path = '' as $
  select exists (
    select 1 from public.records r
    where r.id = rid and r.status = 'publie' and r.visibility = 'public'
      and exists (select 1 from public.consents c where c.record_id = r.id
        and c.revoked_at is null and coalesce(c.scope ->> 'diffusion','false') = 'true')
      and (select rv.decision from public.reviews rv where rv.record_id = r.id
        and rv.kind = 'culturelle' order by rv.created_at desc limit 1) = 'approuve'
      and (select rv.decision from public.reviews rv where rv.record_id = r.id
        and rv.kind = 'diffusion' order by rv.created_at desc limit 1) = 'approuve'
  );
$;

revoke all on function public.has_role(public.app_role) from public, anon;
revoke all on function public.has_valid_consent(uuid, text) from public, anon;
revoke all on function public.is_publishable(uuid) from public, anon;
revoke all on function public.is_public_record(uuid) from public;
grant execute on function public.is_public_record(uuid) to anon, authenticated;
grant execute on function public.has_role(public.app_role) to authenticated;
grant execute on function public.has_valid_consent(uuid, text) to authenticated;
grant execute on function public.is_publishable(uuid) to authenticated;

create or replace function public.guard_publish()
returns trigger language plpgsql set search_path = '' as $$
begin
  if new.status = 'publie' and not public.is_publishable(new.id) then
    raise exception 'Publication refusée : consentement et double validation requis';
  end if;
  return new;
end;
$$;
drop trigger if exists trg_guard_publish on public.records;
create trigger trg_guard_publish before insert or update of status, visibility
on public.records for each row execute function public.guard_publish();

create or replace function public.guard_review()
returns trigger language plpgsql set search_path = '' as $$
declare owner_id uuid;
begin
  if new.reviewer_id is distinct from (select auth.uid()) then
    raise exception 'Le réviseur doit correspondre à la session authentifiée';
  end if;
  select collector_id into owner_id from public.records where id = new.record_id;
  if owner_id is null then raise exception 'Récit introuvable'; end if;
  if new.reviewer_id = owner_id then raise exception 'Auto-validation interdite'; end if;
  if not public.has_role('sage'::public.app_role) then
    raise exception 'Seul un Sage habilité peut enregistrer une validation';
  end if;
  return new;
end;
$$;
drop trigger if exists trg_guard_review on public.reviews;
create trigger trg_guard_review before insert or update on public.reviews
for each row execute function public.guard_review();

create or replace function public.on_revocation()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if new.revoked_at is not null and old.revoked_at is null then
    update public.records set status = 'retire', visibility = 'prive', updated_at = now()
      where id = new.record_id;
    insert into public.audit_events(actor_id, action, entity, entity_id)
      values ((select auth.uid()), 'retrait_consentement', 'consents', new.id);
  end if;
  return new;
end;
$$;
revoke all on function public.on_revocation() from public, anon, authenticated;
drop trigger if exists trg_revocation on public.consents;
create trigger trg_revocation after update of revoked_at on public.consents
for each row execute function public.on_revocation();

-- RLS activée sur toutes les tables exposées.
alter table public.user_roles enable row level security;
alter table public.records enable row level security;
alter table public.assignments enable row level security;
alter table public.consents enable row level security;
alter table public.audio_assets enable row level security;
alter table public.text_versions enable row level security;
alter table public.reviews enable row level security;
alter table public.audit_events enable row level security;

drop policy if exists roles_read_self_or_admin on public.user_roles;
create policy roles_read_self_or_admin on public.user_roles for select to authenticated
using (user_id = (select auth.uid()) or public.has_role('admin'::public.app_role));
-- Aucun droit d'écriture client sur user_roles : l'attribution de rôles doit être administrative.

drop policy if exists records_select_authorized on public.records;
create policy records_select_authorized on public.records for select to authenticated
using (
  collector_id = (select auth.uid())
  or public.has_role('admin'::public.app_role)
  or (public.has_role('sage'::public.app_role) and status in ('revision','soumis','approuve'))
  or exists (select 1 from public.assignments a where a.record_id = id and a.user_id = (select auth.uid()))
);
drop policy if exists records_insert_collector_draft on public.records;
create policy records_insert_collector_draft on public.records for insert to authenticated
with check (
  public.has_role('collecteur'::public.app_role)
  and collector_id = (select auth.uid())
  and status = 'brouillon' and visibility = 'prive'
);
drop policy if exists records_update_owner_draft on public.records;
create policy records_update_owner_draft on public.records for update to authenticated
using (collector_id = (select auth.uid()) and status = 'brouillon')
with check (collector_id = (select auth.uid()) and status = 'brouillon' and visibility = 'prive');
drop policy if exists records_delete_owner_draft on public.records;
create policy records_delete_owner_draft on public.records for delete to authenticated
using (collector_id = (select auth.uid()) and status = 'brouillon');

drop policy if exists assignments_read_related on public.assignments;
create policy assignments_read_related on public.assignments for select to authenticated
using (user_id = (select auth.uid()) or public.has_role('admin'::public.app_role)
  or exists (select 1 from public.records r where r.id = record_id and r.collector_id = (select auth.uid())));
-- Pas de policy client INSERT/UPDATE/DELETE : les affectations sont faites par un backend de confiance.

drop policy if exists consents_owner_read on public.consents;
create policy consents_owner_read on public.consents for select to authenticated
using (exists (select 1 from public.records r where r.id = record_id
  and (r.collector_id = (select auth.uid()) or public.has_role('admin'::public.app_role))));
drop policy if exists consents_owner_insert on public.consents;
create policy consents_owner_insert on public.consents for insert to authenticated
with check (recorded_by = (select auth.uid()) and exists (
  select 1 from public.records r where r.id = record_id and r.collector_id = (select auth.uid())
));
drop policy if exists consents_owner_revoke on public.consents;
create policy consents_owner_revoke on public.consents for update to authenticated
using (exists (select 1 from public.records r where r.id = record_id and r.collector_id = (select auth.uid())))
with check (recorded_by = (select auth.uid()) and exists (
  select 1 from public.records r where r.id = record_id and r.collector_id = (select auth.uid())
));

drop policy if exists audio_select_related on public.audio_assets;
create policy audio_select_related on public.audio_assets for select to authenticated
using (exists (select 1 from public.records r where r.id = record_id and r.collector_id = (select auth.uid()))
  or exists (select 1 from public.assignments a where a.record_id = record_id and a.user_id = (select auth.uid()))
  or public.has_role('admin'::public.app_role));
drop policy if exists audio_insert_with_consent on public.audio_assets;
create policy audio_insert_with_consent on public.audio_assets for insert to authenticated
with check (public.has_valid_consent(record_id, 'archivage') and exists (
  select 1 from public.records r where r.id = record_id and r.collector_id = (select auth.uid())
));

drop policy if exists texts_select_related on public.text_versions;
create policy texts_select_related on public.text_versions for select to authenticated
using (exists (select 1 from public.records r where r.id = record_id and
  (r.collector_id = (select auth.uid()) or public.has_role('sage'::public.app_role)
   or public.has_role('admin'::public.app_role)))
  or exists (select 1 from public.assignments a where a.record_id = record_id and a.user_id = (select auth.uid())));
drop policy if exists texts_insert_assigned on public.text_versions;
create policy texts_insert_assigned on public.text_versions for insert to authenticated
with check (author_id = (select auth.uid()) and exists (
  select 1 from public.assignments a where a.record_id = record_id and a.user_id = (select auth.uid())
));
-- Les utilisateurs ne peuvent pas déclarer eux-mêmes leur texte « humainement validé ».
revoke insert, update, delete on public.text_versions from anon, authenticated;
grant select on public.text_versions to authenticated;
grant insert (record_id, kind, lang, body, origin, author_id) on public.text_versions to authenticated;

drop policy if exists reviews_insert_sage on public.reviews;
create policy reviews_insert_sage on public.reviews for insert to authenticated
with check (public.has_role('sage'::public.app_role) and reviewer_id = (select auth.uid()));
drop policy if exists reviews_select_sage_audit on public.reviews;
create policy reviews_select_sage_audit on public.reviews for select to authenticated
using (public.has_role('sage'::public.app_role) or public.has_role('audit'::public.app_role)
  or public.has_role('admin'::public.app_role));

drop policy if exists audit_select_audit_admin on public.audit_events;
create policy audit_select_audit_admin on public.audit_events for select to authenticated
using (public.has_role('audit'::public.app_role) or public.has_role('admin'::public.app_role));
-- Pas d'écriture directe du journal d'audit depuis le client.

-- Catalogue public : vue invoker + politiques RLS publiques étroitement limitées.
drop policy if exists records_public_catalogue on public.records;
create policy records_public_catalogue on public.records for select to anon, authenticated
using (public.is_public_record(id));

drop policy if exists texts_public_catalogue on public.text_versions;
create policy texts_public_catalogue on public.text_versions for select to anon, authenticated
using (human_reviewed = true and public.is_public_record(record_id));
grant select on public.records, public.text_versions to authenticated;
grant select (id, title, language, locality, status, visibility) on public.records to anon;
grant select (record_id, kind, lang, body, human_reviewed, created_at) on public.text_versions to anon;

create or replace view public.public_records with (security_invoker = true) as
select r.id, r.title, r.language, r.locality,
  (select t.body from public.text_versions t where t.record_id = r.id and t.kind = 'transcription'
    and t.human_reviewed order by t.created_at desc limit 1) as transcription,
  (select t.body from public.text_versions t where t.record_id = r.id and t.kind = 'traduction'
    and t.lang = 'fr' and t.human_reviewed order by t.created_at desc limit 1) as traduction_fr
from public.records r
where public.is_public_record(r.id);
grant select on public.public_records to anon, authenticated;

-- Bucket privé : objets rangés sous <user_id>/<record_id>/<filename>.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('audio-prive','audio-prive',false,104857600,
  array['audio/webm','audio/mp4','audio/mpeg','audio/wav','audio/x-wav','audio/ogg','audio/flac'])
on conflict (id) do update set public = false, file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists audio_prive_upload_owner_consent on storage.objects;
create policy audio_prive_upload_owner_consent on storage.objects for insert to authenticated
with check (bucket_id = 'audio-prive'
  and (storage.foldername(name))[1] = (select auth.uid())::text
  and exists (select 1 from public.records r where r.id = ((storage.foldername(name))[2])::uuid
    and r.collector_id = (select auth.uid())
    and public.has_valid_consent(r.id, 'archivage')));
drop policy if exists audio_prive_read_owner_or_assignment on storage.objects;
create policy audio_prive_read_owner_or_assignment on storage.objects for select to authenticated
using (bucket_id = 'audio-prive' and (
  (storage.foldername(name))[1] = (select auth.uid())::text
  or exists (select 1 from public.assignments a where a.record_id = ((storage.foldername(name))[2])::uuid
    and a.user_id = (select auth.uid()))
  or public.has_role('admin'::public.app_role)
));
drop policy if exists audio_prive_delete_owner on storage.objects;
create policy audio_prive_delete_owner on storage.objects for delete to authenticated
using (bucket_id = 'audio-prive' and (storage.foldername(name))[1] = (select auth.uid())::text);


-- Droits SQL explicites : RLS filtre les lignes, les GRANT limitent les opérations/colonnes.
revoke all on public.user_roles, public.records, public.assignments, public.consents,
  public.audio_assets, public.text_versions, public.reviews, public.audit_events
from anon, authenticated;

grant select on public.user_roles to authenticated;
grant select on public.records to authenticated;
grant insert (title, language, locality, recorded_on, holder_label, collector_id)
  on public.records to authenticated;
grant update (title, language, locality, recorded_on, holder_label, updated_at)
  on public.records to authenticated;
grant delete on public.records to authenticated;

grant select on public.assignments to authenticated;
grant select on public.consents to authenticated;
grant insert (record_id, scope, recorded_by) on public.consents to authenticated;
grant update (revoked_at) on public.consents to authenticated;

grant select on public.audio_assets to authenticated;
grant insert (record_id, storage_path, duration_s) on public.audio_assets to authenticated;

grant select on public.text_versions to authenticated;
grant insert (record_id, kind, lang, body, origin, author_id) on public.text_versions to authenticated;

grant select on public.reviews to authenticated;
grant insert (record_id, kind, decision, motive, reviewer_id) on public.reviews to authenticated;

grant select on public.audit_events to authenticated;

-- Droits en colonnes pour le catalogue public uniquement.
grant select (id, title, language, locality, status, visibility) on public.records to anon;
grant select (record_id, kind, lang, body, human_reviewed, created_at) on public.text_versions to anon;

commit;
