from __future__ import annotations

from pathlib import Path
import sys

from fastapi import APIRouter
from pydantic import BaseModel

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from backend.services.modeling.advisor_pipeline import recommend_bans

router = APIRouter()


class DraftRecommendationRequest(BaseModel):
    team: str
    blue_picks: list[str] = []
    red_picks: list[str] = []
    blue_bans: list[str] = []
    red_bans: list[str] = []
    top_k: int = 3
    strict_turn: bool = True
    rerank_pool_size: int | None = None


@router.post("/recommend")
def recommend(request: DraftRecommendationRequest):
    return recommend_bans(
        team=request.team,
        blue_picks=request.blue_picks,
        red_picks=request.red_picks,
        blue_bans=request.blue_bans,
        red_bans=request.red_bans,
        top_k=request.top_k,
        strict_turn=request.strict_turn,
        rerank_pool_size=request.rerank_pool_size,
    )
