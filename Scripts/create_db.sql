create table public.users (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  name text,
  created_at timestamp with time zone default now()
);

create table public.incidents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references public.users(id) on delete cascade,
  type text not null, -- e.g. 'phishing_email', 'shodan', 'browser_url'
  description text,
  source text, -- where it came from (email, Shodan, extension, etc)
  severity integer check (severity between 1 and 5),
  detected_at timestamp with time zone default now(),
  resolved boolean default false
);

create table public.recommendations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references public.users(id) on delete cascade,
  incident_id uuid references public.incidents(id) on delete set null,
  message text not null,
  created_at timestamp with time zone default now()
);

alter table public.users enable row level security;
alter table public.incidents enable row level security;
alter table public.recommendations enable row level security;
create policy "Users can view their own data" on public.users
  for select using (auth.uid() = id);

create policy "Users can insert their own data" on public.users
  for insert with check (auth.uid() = id);  

create policy "Users can update their own data" on public.users
  for update using (auth.uid() = id)
  with check (auth.uid() = id);

create policy "Users can delete their own data" on public.users
    for delete using (auth.uid() = id);

create policy "Users can view their own incidents" on public.incidents
    for select using (auth.uid() = user_id);

create policy "Users can insert their own incidents" on public.incidents
    for insert with check (auth.uid() = user_id);