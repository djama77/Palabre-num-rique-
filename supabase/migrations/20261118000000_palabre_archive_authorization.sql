-- Separate permission to retain an audio recording/transcript in private cloud archives.
-- Existing rows default to false: do not infer archive permission from recording consent.
alter table public.palabre_records
  add column if not exists archive_authorized boolean not null default false;

drop policy if exists "Owners and approved public records can be read" on public.palabre_records;
create policy "Owners and approved public records can be read"
  on public.palabre_records for select
  to anon, authenticated
  using (
    owner_id = (select auth.uid())
    or (
      status = 'published'
      and consent_recorded = true
      and archive_authorized = true
      and publication_authorized = true
    )
  );

drop policy if exists "Users can create private drafts" on public.palabre_records;
create policy "Users can create private drafts"
  on public.palabre_records for insert
  to authenticated
  with check (
    owner_id = (select auth.uid())
    and consent_recorded = true
    and archive_authorized = true
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

grant insert (owner_id, title_so, transcript_so, audio_path, consent_recorded, archive_authorized)
  on public.palabre_records to authenticated;
