-- Marketplace connection metadata and encrypted server-side credentials.
-- Tokens are encrypted by the FastAPI service before insertion. No plaintext
-- marketplace token is stored by this migration.

create extension if not exists pgcrypto;

create table if not exists public.marketplace_connections (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    marketplace text not null check (marketplace in ('amazon', 'myntra')),
    status text not null default 'not_connected'
        check (status in ('not_connected', 'connected', 'error', 'expired')),
    external_account_id text,
    encrypted_credentials text,
    token_expires_at timestamptz,
    connected_at timestamptz,
    last_error_code text,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (user_id, marketplace)
);

create table if not exists public.marketplace_oauth_states (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    marketplace text not null check (marketplace = 'amazon'),
    state_hash text not null unique,
    expires_at timestamptz not null,
    consumed_at timestamptz,
    created_at timestamptz not null default now()
);

create index if not exists marketplace_connections_user_id_idx
    on public.marketplace_connections(user_id);
create index if not exists marketplace_oauth_states_lookup_idx
    on public.marketplace_oauth_states(state_hash, marketplace, expires_at)
    where consumed_at is null;

alter table public.marketplace_connections enable row level security;
alter table public.marketplace_oauth_states enable row level security;

drop policy if exists "Users can read their marketplace connection metadata"
    on public.marketplace_connections;
create policy "Users can read their marketplace connection metadata"
    on public.marketplace_connections
    for select
    to authenticated
    using (auth.uid() = user_id);

-- Do not grant browser clients access to the encrypted credential column.
revoke all on public.marketplace_connections from anon, authenticated;
grant select (
    id, user_id, marketplace, status, external_account_id, token_expires_at,
    connected_at, last_error_code, metadata, created_at, updated_at
) on public.marketplace_connections to authenticated;
revoke all on public.marketplace_oauth_states from anon, authenticated;

-- Atomically validates and consumes one OAuth state. Only the server-side
-- service role can execute this function.
create or replace function public.consume_marketplace_oauth_state(
    p_state_hash text,
    p_marketplace text
)
returns table (user_id uuid)
language plpgsql
security definer
set search_path = public
as $$
begin
    return query
    update public.marketplace_oauth_states
       set consumed_at = now()
     where state_hash = p_state_hash
       and marketplace = p_marketplace
       and consumed_at is null
       and expires_at > now()
    returning marketplace_oauth_states.user_id;
end;
$$;

revoke all on function public.consume_marketplace_oauth_state(text, text)
    from public, anon, authenticated;
grant execute on function public.consume_marketplace_oauth_state(text, text)
    to service_role;
