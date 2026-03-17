import re

from liquipedia_api import fetch_table

def build_tournament_conditions(start_date: str, end_date: str, allowed_tiers: set[str]) -> str:
    tier_clause = " OR ".join(f"[[liquipediatier::{tier}]]" for tier in sorted(allowed_tiers))
    return (
        f"[[startdate::>{start_date}]] AND "
        f"[[startdate::<{end_date}]] AND "
        f"({tier_clause})"
    )

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")

def normalize_tournament_row(row: dict, wiki: str) -> dict:
    pagename = row.get("pagename") or row.get("parent") or row.get("name")
    display_name = row.get("name") or row.get("displayname") or pagename
    return {
        "name": slugify(display_name),
        "wiki": wiki,
        "pagename": pagename,
        "display_name": display_name,
        "liquipediatier": row.get("liquipediatier"),
        "startdate": row.get("startdate"),
        "enddate": row.get("enddate"),
        "conditions": f"[[pagename::{pagename}]]",
    }

def discover_tournaments_via_match_table(
    api_key: str,
    wiki: str,
    start_date: str,
    end_date: str,
    allowed_tiers: set[str],
) -> list[dict]:
    conditions = build_tournament_conditions(start_date, end_date, allowed_tiers)
    data = fetch_table(api_key, "tournament", wiki, conditions, limit=1000)
    
    rows = data.get("result", [])
    return [normalize_tournament_row(row, wiki) for row in rows if row.get("pagename")]