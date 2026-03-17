from services.liquipedia_api import fetch_table
from services.tournament_finder import discover_tournaments_via_match_table
from services.file_utils import load_json, save_json

from pathlib import Path
import os
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("LIQUIPEDIA_API_KEY")

    tournaments = discover_tournaments_via_match_table(
        api_key=api_key,
        wiki="mobilelegends",
        start_date="2023-01-01",
        end_date="2024-01-01",
        allowed_tiers={"1", "2"}, # S and A Tier tournaments only
    )

    existing = load_json(Path("backend/data/tournaments.json"))
    merged = existing + tournaments  # you’ll later replace with merge()

    save_json(Path("backend/data/tournaments.json"), merged)

    print(f"Saved {len(merged)} tournaments")