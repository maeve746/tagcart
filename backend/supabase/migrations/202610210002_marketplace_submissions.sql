-- Persist TagCart marketplace submission simulations and their audit history.
-- This migration is intentionally separate from marketplace connections and
-- has NOT been assumed to be applied by the application.

do $$
begin
  if to_regclass('public.listings') is null then
    raise exception using
      message = 'Required table public.listings does not exist.',
      hint = 'Apply the TagCart listings migration first. It must expose id uuid, user_id uuid, and status.';
  end if;
end
$$;

-- Enables an ownership-preserving composite foreign key. The existing listing
-- id remains the primary identifier; this index simply includes its owner.
create unique index if not exists tagcart_listings_id_user_id_uidx
  on public.listings(id, user_id);

create table if not exists public.marketplace_submissions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  listing_id uuid not null,
  marketplace text not null check (marketplace in ('amazon', 'myntra')),
  mode text not null check (mode in ('mock', 'production')),
  status text not null check (status in ('accepted', 'processing', 'completed', 'rejected')),
  final_mock_outcome text check (final_mock_outcome in ('completed', 'rejected')),
  mock_reference text not null,
  request_payload jsonb not null default '{}'::jsonb,
  validation_snapshot jsonb not null default '{}'::jsonb,
  poll_count integer not null default 0 check (poll_count >= 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  completed_at timestamptz,
  constraint marketplace_submission_owner_matches_listing
    foreign key (listing_id, user_id)
    references public.listings(id, user_id)
    on delete restrict
);

comment on table public.marketplace_submissions is
  'TagCart marketplace workflow records. mode=mock records are simulations and never prove a live marketplace listing.';

create index if not exists marketplace_submissions_user_created_idx
  on public.marketplace_submissions(user_id, created_at desc);
create index if not exists marketplace_submissions_user_listing_idx
  on public.marketplace_submissions(user_id, listing_id);
create index if not exists marketplace_submissions_marketplace_status_idx
  on public.marketplace_submissions(marketplace, status);

create table if not exists public.marketplace_submission_history (
  id bigint generated always as identity primary key,
  submission_id uuid not null references public.marketplace_submissions(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  from_status text check (from_status is null or from_status in ('accepted', 'processing', 'completed', 'rejected')),
  to_status text not null check (to_status in ('accepted', 'processing', 'completed', 'rejected')),
  reason text not null,
  created_at timestamptz not null default now()
);

create index if not exists marketplace_submission_history_submission_idx
  on public.marketplace_submission_history(submission_id, created_at);
create index if not exists marketplace_submission_history_user_idx
  on public.marketplace_submission_history(user_id, created_at desc);

alter table public.marketplace_submissions enable row level security;
alter table public.marketplace_submission_history enable row level security;

drop policy if exists "Users read own marketplace submissions" on public.marketplace_submissions;
create policy "Users read own marketplace submissions"
  on public.marketplace_submissions for select
  to authenticated
  using (auth.uid() = user_id);

drop policy if exists "Users read own marketplace submission history" on public.marketplace_submission_history;
create policy "Users read own marketplace submission history"
  on public.marketplace_submission_history for select
  to authenticated
  using (auth.uid() = user_id);

-- Mutations are only exposed to the server-side service role through these
-- functions so clients cannot approve, forge, or advance their own records.
revoke insert, update, delete on public.marketplace_submissions from anon, authenticated;
revoke insert, update, delete on public.marketplace_submission_history from anon, authenticated;

create or replace function public.create_mock_marketplace_submission(
  p_user_id uuid,
  p_listing_id uuid,
  p_marketplace text,
  p_payload jsonb,
  p_validation jsonb,
  p_final_outcome text,
  p_reference text
)
returns setof public.marketplace_submissions
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  v_submission public.marketplace_submissions%rowtype;
begin
  if p_marketplace not in ('amazon', 'myntra') then
    raise exception 'Unsupported marketplace';
  end if;
  if p_final_outcome not in ('completed', 'rejected') then
    raise exception 'Invalid mock final outcome';
  end if;
  if not exists (
    select 1 from public.listings
    where id = p_listing_id and user_id = p_user_id and lower(status) = 'approved'
  ) then
    raise exception 'Listing is missing, not owned by the user, or not approved';
  end if;

  insert into public.marketplace_submissions (
    user_id, listing_id, marketplace, mode, status, final_mock_outcome,
    mock_reference, request_payload, validation_snapshot
  ) values (
    p_user_id, p_listing_id, p_marketplace, 'mock', 'accepted', p_final_outcome,
    p_reference, p_payload, p_validation
  ) returning * into v_submission;

  insert into public.marketplace_submission_history (
    submission_id, user_id, from_status, to_status, reason
  ) values (
    v_submission.id, p_user_id, null, 'accepted',
    'Deterministic mock submission accepted for simulation.'
  );

  return next v_submission;
end
$$;

create or replace function public.advance_mock_marketplace_submission(
  p_submission_id uuid,
  p_user_id uuid
)
returns setof public.marketplace_submissions
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  v_submission public.marketplace_submissions%rowtype;
  v_previous text;
  v_next text;
begin
  select * into v_submission
  from public.marketplace_submissions
  where id = p_submission_id and user_id = p_user_id and mode = 'mock'
  for update;

  if not found then
    return;
  end if;

  v_previous := v_submission.status;
  v_next := case
    when v_previous = 'accepted' then 'processing'
    when v_previous = 'processing' then v_submission.final_mock_outcome
    else v_previous
  end;

  if v_next <> v_previous then
    update public.marketplace_submissions
    set status = v_next,
        poll_count = poll_count + 1,
        updated_at = now(),
        completed_at = case when v_next in ('completed', 'rejected') then now() else completed_at end
    where id = p_submission_id
    returning * into v_submission;

    insert into public.marketplace_submission_history (
      submission_id, user_id, from_status, to_status, reason
    ) values (
      v_submission.id, p_user_id, v_previous, v_next,
      case when v_next = 'processing'
        then 'Deterministic mock processing step.'
        else 'Deterministic mock terminal outcome; no marketplace publication occurred.'
      end
    );
  end if;

  return next v_submission;
end
$$;

revoke all on function public.create_mock_marketplace_submission(uuid, uuid, text, jsonb, jsonb, text, text) from public, anon, authenticated;
revoke all on function public.advance_mock_marketplace_submission(uuid, uuid) from public, anon, authenticated;
grant execute on function public.create_mock_marketplace_submission(uuid, uuid, text, jsonb, jsonb, text, text) to service_role;
grant execute on function public.advance_mock_marketplace_submission(uuid, uuid) to service_role;
