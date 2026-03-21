from __future__ import annotations

from typing import Any

from backend.services.llm.ban_advisor import build_ban_advice
from backend.services.modeling.ban_recommender import (
    recommend_next_bans,
    simulate_ban_sequence,
)


def recommend_bans(
    team: str = "blue",
    blue_picks: list[str] | None = None,
    red_picks: list[str] | None = None,
    blue_bans: list[str] | None = None,
    red_bans: list[str] | None = None,
    top_k: int = 3,
    strict_turn: bool = True,
    rerank_pool_size: int | None = None,
) -> dict[str, Any]:
    return recommend_next_bans(
        blue_picks=blue_picks,
        red_picks=red_picks,
        blue_bans=blue_bans,
        red_bans=red_bans,
        team=team,
        top_k=top_k,
        strict_turn=strict_turn,
        rerank_pool_size=rerank_pool_size,
    )


def advise_bans(
    team: str = "blue",
    blue_picks: list[str] | None = None,
    red_picks: list[str] | None = None,
    blue_bans: list[str] | None = None,
    red_bans: list[str] | None = None,
    top_k: int = 3,
    strict_turn: bool = True,
    rerank_pool_size: int | None = None,
) -> dict[str, Any]:
    recommendation = recommend_bans(
        team=team,
        blue_picks=blue_picks,
        red_picks=red_picks,
        blue_bans=blue_bans,
        red_bans=red_bans,
        top_k=top_k,
        strict_turn=strict_turn,
        rerank_pool_size=rerank_pool_size,
    )
    advisor = build_ban_advice(
        recommendation=recommendation,
        blue_picks=blue_picks,
        red_picks=red_picks,
        blue_bans=blue_bans,
        red_bans=red_bans,
    )
    return {
        "recommendation": recommendation,
        "advisor": advisor,
    }


def simulate_bans(
    blue_picks: list[str] | None = None,
    red_picks: list[str] | None = None,
    blue_bans: list[str] | None = None,
    red_bans: list[str] | None = None,
    top_k: int = 3,
) -> dict[str, Any]:
    return simulate_ban_sequence(
        blue_picks=blue_picks,
        red_picks=red_picks,
        blue_bans=blue_bans,
        red_bans=red_bans,
        top_k=top_k,
    )
