# Snippets for supabase SQL

## Clone new sb auth.user to public
Create a users table in "public" that references "auth.users".
```sql
-- USERS
create table public.sb_users_profile (
  id uuid not null primary key, -- UUID from auth.users
  email text,
  first_name text,
  last_name text
);
comment on table public.sb_users_profile is 'Profile data for each user.';
comment on column public.sb_users_profile.id is 'References the internal Supabase Auth user.';

```


```sql
create or replace function public.handle_new_sb_user()
returns trigger as $$
begin
  insert into public.sb_users_profile (id, email)
  values (new.id, new.email);
  return new;
end;
$$ language plpgsql security definer;

create trigger on_sb_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_sb_user();


```

## Policy to read only authenticated user's table
* ref - https://supabase.com/docs/guides/auth/managing-user-data

Public
```sql
create policy "Public profiles are viewable by everyone."
  on profiles for select
  using ( true );

create policy "Users can insert their own profile."
  on profiles for insert
  with check ( auth.uid() = id );

create policy "Users can update own profile."
  on profiles for update
  using ( auth.uid() = id );
```

Private access
```sql
create policy "Profiles are viewable by users who created them."
  on sb_users_profile for select
  using ( auth.uid() = id );
```


```sql
CREATE POLICY "Only user can update"
ON public.sb_users_profile
FOR UPDATE USING (
  auth.uid() = id
) WITH CHECK (
  auth.uid() = id
);
```

```sql
create policy "Read only by users who created them."
  on contents_userdefaultprompt for select
  using ( auth.uid() = sb_user_id );
```


```sql
create policy "Read only by users who created them."
  on contents_prompt for select
  using ( auth.uid() = sb_user_id );
```

```
alter table "public"."sb_users_profile" enable row level security;

```

## RBAC and custom claims
https://github.com/supabase-community/supabase-custom-claims

https://github.com/supabase/supabase/tree/master/examples/slack-clone/nextjs-slack-clone#supabase-details


# Supabase CLI


supabase login
supabase link --project-ref $PROJECT_ID
supabase db remote commit

# docker for amd64
export DOCKER_DEFAULT_PLATFORM=linux/amd64
