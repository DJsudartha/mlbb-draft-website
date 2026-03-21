from __future__ import annotations

import argparse
import sys
from pathlib import Path

from xgboost import XGBRanker

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from backend.services.common.file_utils import load_json, save_json
from backend.services.liquipedia.counter_stats import (
    build_counter_matrix_from_tournament,
    finalize_counter_stats,
    merge_counter_matrices,
)
from backend.services.liquipedia.hero_stats import (
    build_hero_stats_from_grouped_tournament,
    calculate_win_rates,
    combine_all_hero_stats,
    merge_hero_stats,
)
from backend.services.liquipedia.synergy_stats import (
    build_synergy_matrix_from_tournament,
    finalize_synergy_stats,
    merge_synergy_matrices,
)
from backend.services.modeling.dataset_builder import build_ban_dataset
from backend.services.modeling.training import (
    chronological_split,
    feature_columns,
    load_dataset_frame,
    query_group_sizes,
    rank_metrics,
    sort_for_grouped_ranking,
)

DATASET_PATH = Path("backend/data/modeling/ban_dataset.json")
OUTPUT_DIR = Path("backend/data/modeling/models")
RAW_TOURNAMENTS_DIR = Path("backend/data/raw/tournaments")
PROCESSED_DIR = Path("backend/data/processed")


def _ban_feature_columns(df, excluded_columns: set[str]) -> list[str]:
    columns = feature_columns(df, excluded_columns)
    blocked_tokens = (
        "ban_priority",
        "average_ban_order_priority",
    )
    return [
        column_name
        for column_name in columns
        if not any(blocked_token in column_name for blocked_token in blocked_tokens)
    ]


def _evaluate_prediction_frame(frame):
    return {
        "ranking": rank_metrics(frame, "query_id", "label_is_ban", "score"),
        "by_ban_order": {
            str(int(ban_order)): rank_metrics(
                subset,
                "query_id",
                "label_is_ban",
                "score",
            )
            for ban_order, subset in frame.groupby("ban_order", sort=True)
        },
        "by_phase": {
            str(int(phase_index)): rank_metrics(
                subset,
                "query_id",
                "label_is_ban",
                "score",
            )
            for phase_index, subset in frame.groupby("phase_index", sort=True)
        },
        "by_team": {
            team_name: rank_metrics(
                subset,
                "query_id",
                "label_is_ban",
                "score",
            )
            for team_name, subset in frame.groupby("team", sort=True)
        },
    }


def _attach_scores(df, scores, score_name):
    frame = df[
        [
            "query_id",
            "team",
            "ban_order",
            "phase_index",
            "candidate_hero",
            "label_is_ban",
        ]
    ].copy()
    frame["score"] = scores
    return score_name, frame


def _refresh_processed_stats(
    raw_dir: Path = RAW_TOURNAMENTS_DIR,
    processed_dir: Path = PROCESSED_DIR,
) -> None:
    raw_files = sorted(raw_dir.glob("*.json"))
    if not raw_files:
        raise FileNotFoundError(f"No tournament files found in {raw_dir}")

    combined_stats = {}
    combined_counters = {}
    combined_synergy = {}

    for file_path in raw_files:
        tournament_data = load_json(file_path)
        if not isinstance(tournament_data, dict):
            continue

        hero_stats = build_hero_stats_from_grouped_tournament(tournament_data)
        counter_matrix = build_counter_matrix_from_tournament(tournament_data)
        synergy_matrix = build_synergy_matrix_from_tournament(tournament_data)

        combined_stats = merge_hero_stats(combined_stats, hero_stats)
        combined_counters = merge_counter_matrices(combined_counters, counter_matrix)
        combined_synergy = merge_synergy_matrices(combined_synergy, synergy_matrix)

    final_hero_stats = calculate_win_rates(combined_stats)
    final_counter = finalize_counter_stats(combined_counters)
    final_synergy = finalize_synergy_stats(combined_synergy)
    combined_complete_stats = combine_all_hero_stats(final_hero_stats, final_counter, final_synergy)

    save_json(processed_dir / "all_hero_stats.json", final_hero_stats)
    save_json(processed_dir / "counter_matrices.json", final_counter)
    save_json(processed_dir / "synergy_matrices.json", final_synergy)
    save_json(processed_dir / "complete_hero_stats.json", combined_complete_stats)

    print(
        "Refreshed processed stats from "
        f"{len(raw_files)} raw tournament file{'s' if len(raw_files) != 1 else ''}."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train the ban ranker from the latest raw tournament data."
    )
    parser.add_argument(
        "--reuse-dataset",
        action="store_true",
        help="Reuse the existing ban_dataset.json instead of rebuilding it from raw tournament data.",
    )
    parser.add_argument(
        "--skip-processed-refresh",
        action="store_true",
        help="Skip rebuilding processed stats from raw tournament files before training.",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not args.skip_processed_refresh:
        _refresh_processed_stats()

    if args.reuse_dataset and DATASET_PATH.exists():
        print(f"Reusing existing ban dataset at {DATASET_PATH}")
    else:
        save_json(DATASET_PATH, build_ban_dataset())
        print(f"Rebuilt ban dataset from raw tournaments at {DATASET_PATH}")

    metadata, df = load_dataset_frame(DATASET_PATH)
    if df.empty:
        raise ValueError(
            "Ban dataset is empty. Fetch tournament data and rebuild processed stats before training."
        )
    excluded_columns = {
        "query_id",
        "game_id",
        "date",
        "patch",
        "tournament",
        "source_file",
        "team",
        "actual_ban",
        "candidate_hero",
        "label_is_ban",
    }
    columns = _ban_feature_columns(df, excluded_columns)

    train_df, test_df = chronological_split(df, entity_column="query_id")
    train_sorted = sort_for_grouped_ranking(train_df, "query_id")
    test_sorted = sort_for_grouped_ranking(test_df, "query_id")

    xgb_ranker = XGBRanker(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.8,
        objective="rank:pairwise",
        eval_metric="ndcg@3",
        random_state=42,
        tree_method="hist",
    )
    xgb_ranker.fit(
        train_sorted[columns].fillna(0.0),
        train_sorted["label_is_ban"],
        group=query_group_sizes(train_sorted, "query_id"),
    )

    prediction_frames: dict[str, object] = {}
    prediction_name, prediction_frame = _attach_scores(
        test_sorted,
        xgb_ranker.predict(test_sorted[columns].fillna(0.0)).tolist(),
        "xgb_ranker_global",
    )
    prediction_frames[prediction_name] = prediction_frame

    heuristic_specs = {
        "heuristic_ban_rate": "candidate_ban_rate",
        "heuristic_current_slot_share": "candidate_current_slot_share",
        "heuristic_phase_fit_share": "candidate_phase_fit_share",
        "heuristic_hero_power": "candidate_hero_power",
    }
    for heuristic_name, column_name in heuristic_specs.items():
        name, frame = _attach_scores(test_df, test_df[column_name].tolist(), heuristic_name)
        prediction_frames[name] = frame

    report = {
        "dataset_metadata": metadata,
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "feature_count": len(columns),
        "features": columns,
        "top_global_ranker_features": [
            {
                "feature": feature_name,
                "importance": float(importance),
            }
            for feature_name, importance in sorted(
                zip(columns, xgb_ranker.feature_importances_.tolist()),
                key=lambda item: item[1],
                reverse=True,
            )[:20]
        ],
        "models": {
            model_name: _evaluate_prediction_frame(frame)
            for model_name, frame in prediction_frames.items()
        },
    }

    xgb_ranker.save_model(OUTPUT_DIR / "ban_xgb_ranker_global.json")
    save_json(OUTPUT_DIR / "ban_ranker_report.json", report)

    best_global = report["models"]["xgb_ranker_global"]["ranking"]["top3_hit_rate"]
    print(f"Saved ban ranker report to {OUTPUT_DIR / 'ban_ranker_report.json'}")
    print(f"Global ranker top-3 hit rate: {best_global:.4f}")
