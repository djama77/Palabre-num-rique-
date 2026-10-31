-- Palabre Numérique: safe baseline for cloud records and private audio.
-- Apply only to the intended Supabase project after reviewing its existing schema.
create table if not exists public.palabre_records (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  title_so text not null check (char_length(btrim(title_so)) between 1 and 300),
  title_fr text,
  transcript_so text,
  translation_fr text,
  audio_path text not null unique,
  consent_recorded boolean not null default false,
  publication_authorized boolean not null default false,
  status text not null default 'draft'
    check (status in ('draft', 'review', 'published', 'restricted')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists palabre_records_owner_created_idx
  on public.palabre_records (owner_id, created_at desc);
create index if not exists palabre_records_public_created_idx
  on public.palabre_records (created_at desc)
  where status = 'published' and consent_recorded and publication_authorized;

alter table public.palabre_records enable row level security;

drop policy if exists "Owners and approved public records can be read" on public.palabre_records;
create policy "Owners and approved public records can be read"
  on public.palabre_records for select
  to anon, authenticated
  using (
    owner_id = (select auth.uid())
    or (status = 'published' and consent_recorded = true and publication_authorized = true)
  );

drop policy if exists "Users can create private drafts" on public.palabre_records;
create policy "Users can create private drafts"
  on public.palabre_records for insert
  to authenticated
  with check (
    owner_id = (select auth.uid())
    and consent_recorded = true
    and publication_authorized = false
    and status = 'draft'
  );

drop policy if exists "Owners can edit draft text only" on public.palabre_records;
create policy "Owners can edit draft text only"
  on public.palabre_records for update
  to authenticated
  using (owner_id = (select auth.uid()) and status = 'draft')
  with check (
    owner_id = (select auth.uid())
    and status = 'draft'
    and publication_authorized = false
    and consent_recorded = true
  );

drop policy if exists "Owners can delete drafts" on public.palabre_records;
create policy "Owners can delete drafts"
  on public.palabre_records for delete
  to authenticated
  using (owner_id = (select auth.uid()) and status = 'draft');

grant usage on schema public to anon, authenticated;
grant select on public.palabre_records to anon, authenticated;
grant insert (owner_id, title_so, transcript_so, audio_path, consent_recorded)
  on public.palabre_records to authenticated;
grant update (title_so, title_fr, transcript_so, translation_fr)
  on public.palabre_records to authenticated;
grant delete on public.palabre_records to authenticated;

-- Private bucket. The browser can only access objects under its own user-id folder.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'palabre-audio',
  'palabre-audio',
  false,
  104857600,
  array['audio/webm','audio/mp4','audio/mpeg','audio/wav','audio/x-wav','audio/ogg','audio/flac']
)
on conflict (id) do update set
  public = false,
  file_size_limit = 104857600,
  allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists "Users can read own Palabre audio" on storage.objects;
create policy "Users can read own Palabre audio"
  on storage.objects for select
  to authenticated
  using (
    bucket_id = 'palabre-audio'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );

drop policy if exists "Users can upload own Palabre audio" on storage.objects;
create policy "Users can upload own Palabre audio"
  on storage.objects for insert
  to authenticated
  with check (
    bucket_id = 'palabre-audio'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );

drop policy if exists "Users can update own Palabre audio" on storage.objects;
create policy "Users can update own Palabre audio"
  on storage.objects for update
  to authenticated
  using (
    bucket_id = 'palabre-audio'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  )
  with check (
    bucket_id = 'palabre-audio'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );

drop policy if exists "Users can delete own Palabre audio" on storage.objects;
create policy "Users can delete own Palabre audio"
  on storage.objects for delete
  to authenticated
  using (
    bucket_id = 'palabre-audio'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );
