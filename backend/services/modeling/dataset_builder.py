from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from backend.services.common.file_utils import load_json
from backend.services.modeling.ban_constants import BAN_SEQUENCE
from backend.services.modeling.features import (
    PROCESSED_STATS_PATH,
    build_ban_candidate_feature_row,
    build_hero_feature_table,
)

RAW_TOURNAMENTS_DIR = Path("backend/data/raw/tournaments")


def _extract_hero_names(items: list[dict[str, Any]]) -> list[str]:
    return [item["hero"] for item in items if item.get("hero")]


def _iter_games(raw_dir: Path = RAW_TOURNAMENTS_DIR) -> Iterator[dict[str, Any]]:
    for tournament_path in sorted(raw_dir.glob("*.json")):
        tournament_data = load_json(tournament_path)
        if not isinstance(tournament_data, dict):
            continue

        tournament_name = tournament_data.get("tournament")
        pagename = tournament_data.get("pagename")

        for series_index, series in enumerate(tournament_data.get("series", []), start=1):
            series_date = series.get("date")
            series_patch = series.get("patch")
            blue_team_name = series.get("blue_team_name")
            red_team_name = series.get("red_team_name")

            for game_index, game in enumerate(series.get("games", []), start=1):
                yield {
                    "source_file": tournament_path.name,
                    "tournament": tournament_name,
                    "pagename": pagename,
                    "series_index": series_index,
                    "game_index": game_index,
                    "date": series_date,
                    "patch": series_patch,
                    "blue_team_name": blue_team_name,
                    "red_team_name": red_team_name,
                    "game_no": game.get("game_no"),
                    "winner": game.get("winner"),
                    "blue_picks": _extract_hero_names(game.get("blue_team", [])),
                    "red_picks": _extract_hero_names(game.get("red_team", [])),
                    "blue_bans": _extract_hero_names(game.get("blue_bans", [])),
                    "red_bans": _extract_hero_names(game.get("red_bans", [])),
                }


def _game_identifier(game_row: dict[str, Any]) -> str:
    return (
        f"{game_row['source_file']}::series{game_row['series_index']}::"
        f"game{game_row['game_index']}::{game_row['game_no']}"
    )


def build_ban_dataset(
    processed_stats_path: Path = PROCESSED_STATS_PATH,
    raw_dir: Path = RAW_TOURNAMENTS_DIR,
) -> dict[str, Any]:
    hero_table = build_hero_feature_table(processed_stats_path)
    all_heroes = sorted(hero_table["heroes"].keys())

    rows: list[dict[str, Any]] = []
    for game_row in _iter_games(raw_dir):
        blue_ban_map = {index + 1: hero for index, hero in enumerate(game_row["blue_bans"])}
        red_ban_map = {index + 1: hero for index, hero in enumerate(game_row["red_bans"])}

        prior_blue_bans: list[str] = []
        prior_red_bans: list[str] = []

        for acting_team, ban_order, turn_index in BAN_SEQUENCE:
            actual_ban = blue_ban_map.get(ban_order) if acting_team == "blue" else red_ban_map.get(ban_order)
            if actual_ban is None:
                continue

            query_id = f"{_game_identifier(game_row)}::{acting_team}::ban{ban_order}"
            unavailable_heroes = set(prior_blue_bans) | set(prior_red_bans)

            for candidate_hero in all_heroes:
                if candidate_hero in unavailable_heroes:
                    continue

                feature_row = build_ban_candidate_feature_row(
                    candidate_hero=candidate_hero,
                    acting_team=acting_team,
                    ban_order=ban_order,
                    prior_blue_bans=prior_blue_bans,
                    prior_red_bans=prior_red_bans,
                    hero_table=hero_table,
                )
                rows.append(
                    {
                        "query_id": query_id,
                        "game_id": _game_identifier(game_row),
                        "date": game_row["date"],
                        "patch": game_row["patch"],
                        "tournament": game_row["tournament"],
                        "source_file": game_row["source_file"],
                        "team": acting_team,
                        "ban_order": ban_order,
                        "turn_index": turn_index,
                        "actual_ban": actual_ban,
                        "candidate_hero": candidate_hero,
                        "label_is_ban": 1 if candidate_hero == actual_ban else 0,
                        **feature_row,
                    }
                )

            if acting_team == "blue":
                prior_blue_bans.append(actual_ban)
            else:
                prior_red_bans.append(actual_ban)

    return {
        "metadata": {
            "row_count": len(rows),
            "model_target": "label_is_ban",
            "source_processed_stats": str(processed_stats_path),
            "source_raw_dir": str(raw_dir),
            "note": (
                "Ban dataset is order-sensitive on real ban slots and prior bans. "
                "It does not include pick-context features because pick order is unavailable."
            ),
        },
        "rows": rows,
    }
