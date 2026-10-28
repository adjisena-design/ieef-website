alter table public.news add column if not exists featured boolean not null default false;

-- one headline at a time: one featured news article, one featured policy brief (research keeps multiple highlights)
create or replace function public.one_headline() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  if new.featured and (tg_op = 'INSERT' or not coalesce(old.featured, false)) then
    if tg_table_name = 'news' then
      update public.news set featured = false where featured and id <> new.id;
    elsif tg_table_name = 'publications' and new.kind = 'policy_brief' then
      update public.publications set featured = false where featured and kind = 'policy_brief' and id <> new.id;
    end if;
  end if;
  return new;
end $$;
revoke all on function public.one_headline() from public, anon, authenticated;
create trigger news_one_headline after insert or update of featured on public.news for each row when (new.featured) execute function public.one_headline();
create trigger publications_one_headline after insert or update of featured on public.publications for each row when (new.featured) execute function public.one_headline();
