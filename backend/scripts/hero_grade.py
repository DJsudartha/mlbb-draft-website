import argparse
import csv
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional
from page_scraper import DEFAULT_STAGE, DEFAULT_TOURNAMENT_NAME, get_liquipedia_hero_data


GRADE_ORDER = ["D", "C", "B", "A", "S"]
MANUAL_WEIGHTS = {
    "pick_rate": 0.35,
    "ban_rate": 0.40,
    "adjusted_win_rate": 0.25,
}


@dataclass
class HeroGradeRow:
    hero: str
    picks: int
    wins: float
    raw_win_rate: Optional[float]
    adjusted_win_rate: float
    pick_rate: float
    ban_rate: float
    presence: float
    ban_share: float
    priority_score: float
    hero_grade: str
    confidence: str
    notes: str


def parse_percent(value: str) -> Optional[float]:
    if value is None:
        return None
    normalized = str(value).strip().replace("%", "")
    if normalized in {"", "-"}:
        return None
    return float(normalized)


def parse_count(value: str) -> int:
    return int(float(str(value).strip()))


def parse_pick_input(stats: dict, total_games: Optional[int]) -> tuple[int, Optional[float]]:
    picks_value = stats.get("picks")
    pick_rate_value = parse_percent(stats.get("pick_rate"))

    if picks_value not in (None, "", "-"):
        return parse_count(picks_value), pick_rate_value

    legacy_pick_value = stats.get("pick_rate")
    if isinstance(legacy_pick_value, str) and "%" not in legacy_pick_value:
        return parse_count(legacy_pick_value), None

    if pick_rate_value is None:
        return 0, None

    if total_games is None:
        raise ValueError(
            "pick_rate is a percentage but total games are unknown. Pass --games explicitly."
        )
    return round((pick_rate_value / 100) * total_games), pick_rate_value


def infer_total_games(ban_rates: list[float]) -> Optional[int]:
    positive_rates = sorted(rate for rate in ban_rates if rate > 0)
    if not positive_rates:
        return None

    smallest_step = positive_rates[0]
    inferred_games = round(100 / smallest_step)
    if inferred_games <= 0:
        return None

    tolerance = 0.06
    for rate in positive_rates[:12]:
        nearest_bucket = round(rate * inferred_games / 100)
        rebuilt = (nearest_bucket / inferred_games) * 100
        if abs(rebuilt - rate) > tolerance:
            return None

    return inferred_games


def percentile_ranks(values: list[float]) -> list[float]:
    if not values:
        return []
    if len(values) == 1:
        return [1.0]

    indexed_values = list(enumerate(values))
    indexed_values.sort(key=lambda pair: pair[1])

    ranks = [0.0] * len(values)
    index = 0
    while index < len(indexed_values):
        start = index
        current_value = indexed_values[index][1]
        while index < len(indexed_values) and indexed_values[index][1] == current_value:
            index += 1
        average_rank = (start + index - 1) / 2
        percentile = average_rank / (len(values) - 1)
        for original_index, _ in indexed_values[start:index]:
            ranks[original_index] = percentile
    return ranks


def min_max_normalize(matrix: list[list[float]]) -> list[list[float]]:
    if not matrix:
        return []
    columns = list(zip(*matrix))
    normalized_columns: list[list[float]] = []
    for column in columns:
        minimum = min(column)
        maximum = max(column)
        spread = maximum - minimum
        if spread == 0:
            normalized_columns.append([0.0] * len(column))
        else:
            normalized_columns.append([(value - minimum) / spread for value in column])
    return [list(row) for row in zip(*normalized_columns)]


def correlation(x_values: list[float], y_values: list[float]) -> float:
    if not x_values or not y_values or len(x_values) != len(y_values):
        return 0.0
    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(y_values) / len(y_values)
    numerator = sum(
        (x_value - x_mean) * (y_value - y_mean)
        for x_value, y_value in zip(x_values, y_values)
    )
    x_variance = sum((x_value - x_mean) ** 2 for x_value in x_values)
    y_variance = sum((y_value - y_mean) ** 2 for y_value in y_values)
    denominator = math.sqrt(x_variance * y_variance)
    if denominator == 0:
        return 0.0
    return numerator / denominator


def critic_weights(matrix: list[list[float]]) -> dict[str, float]:
    feature_names = ["pick_rate", "ban_rate", "adjusted_win_rate"]
    normalized = min_max_normalize(matrix)
    if not normalized:
        return MANUAL_WEIGHTS.copy()

    columns = list(zip(*normalized))
    scores: list[float] = []
    for index, column in enumerate(columns):
        mean = sum(column) / len(column)
        variance = sum((value - mean) ** 2 for value in column) / len(column)
        standard_deviation = math.sqrt(variance)
        contrast = sum(1 - correlation(list(column), list(other_column)) for other_column in columns)
        scores.append(standard_deviation * contrast)

    total_score = sum(scores)
    if total_score == 0:
        return MANUAL_WEIGHTS.copy()

    return {
        feature_name: score / total_score
        for feature_name, score in zip(feature_names, scores)
    }


def entropy_weights(matrix: list[list[float]]) -> dict[str, float]:
    feature_names = ["pick_rate", "ban_rate", "adjusted_win_rate"]
    normalized = min_max_normalize(matrix)
    if not normalized:
        return MANUAL_WEIGHTS.copy()

    columns = list(zip(*normalized))
    feature_scores: list[float] = []
    entropy_scale = 1 / math.log(len(normalized)) if len(normalized) > 1 else 0

    for column in columns:
        shifted = [value + 1e-12 for value in column]
        denominator = sum(shifted)
        probabilities = [value / denominator for value in shifted] if denominator else shifted
        entropy = -entropy_scale * sum(
            probability * math.log(probability) for probability in probabilities if probability > 0
        )
        feature_scores.append(1 - entropy)

    total_score = sum(feature_scores)
    if total_score == 0:
        return MANUAL_WEIGHTS.copy()

    return {
        feature_name: score / total_score
        for feature_name, score in zip(feature_names, feature_scores)
    }


def resolve_weights(matrix: list[list[float]], weighting_method: str) -> dict[str, float]:
    if weighting_method == "manual":
        return MANUAL_WEIGHTS.copy()
    if weighting_method == "entropy":
        return entropy_weights(matrix)
    return critic_weights(matrix)


def weighted_priority_score(
    pick_rate_ranks: list[float],
    ban_rate_ranks: list[float],
    adjusted_win_rate_ranks: list[float],
    weights: dict[str, float],
) -> list[float]:
    scores = []
    for pick_rate, ban_rate, adjusted_win_rate in zip(
        pick_rate_ranks, ban_rate_ranks, adjusted_win_rate_ranks
    ):
        score = (
            weights["pick_rate"] * pick_rate
            + weights["ban_rate"] * ban_rate
            + weights["adjusted_win_rate"] * adjusted_win_rate
        )
        scores.append(score)
    return scores


def base_grade(priority_score: float) -> str:
    if priority_score >= 0.80:
        return "S"
    if priority_score >= 0.65:
        return "A"
    if priority_score >= 0.50:
        return "B"
    if priority_score >= 0.30:
        return "C"
    return "D"


def lower_grade(current_grade: str, max_grade: str) -> str:
    return GRADE_ORDER[min(GRADE_ORDER.index(current_grade), GRADE_ORDER.index(max_grade))]


def confidence_label(picks: int, presence: float, games: int) -> str:
    high_sample_threshold = max(8, math.ceil(games * 0.16))
    medium_sample_threshold = max(5, math.ceil(games * 0.08))

    if picks >= high_sample_threshold or presence >= 65:
        return "high"
    if picks >= medium_sample_threshold or presence >= 35:
        return "medium"
    return "low"


def grade_cap(picks: int, ban_rate: float, presence: float, games: int) -> str:
    high_sample_threshold = max(8, math.ceil(games * 0.16))
    medium_sample_threshold = max(5, math.ceil(games * 0.08))

    if picks >= high_sample_threshold:
        return "S"
    if picks >= medium_sample_threshold:
        return "A" if ban_rate >= 20 or presence >= 35 else "B"
    if picks > 0:
        return "B" if ban_rate >= 20 or presence >= 25 else "C"
    return "C" if ban_rate >= 10 else "D"


def build_notes(picks: int, presence: float, ban_share: float, raw_win_rate: Optional[float]) -> str:
    notes: list[str] = []
    if presence >= 70:
        notes.append("high presence")
    elif presence >= 45:
        notes.append("solid presence")

    if ban_share >= 0.55 and presence >= 25:
        notes.append("ban pressure")

    if raw_win_rate is not None and raw_win_rate >= 60 and picks >= 5:
        notes.append("strong win rate")
    elif raw_win_rate is not None and raw_win_rate <= 40 and picks >= 5:
        notes.append("weak win rate")

    if picks < 5:
        notes.append("small sample")

    return ", ".join(notes) if notes else "balanced profile"


def build_hero_grades(
    tournament_name: Optional[str] = None,
    stage: Optional[str] = None,
    total_games: Optional[int] = None,
    smoothing_games: int = 8,
    weighting_method: str = "critic",
) -> tuple[list[HeroGradeRow], int, dict[str, float]]:
    tournament_name = tournament_name or DEFAULT_TOURNAMENT_NAME
    stage = DEFAULT_STAGE if stage is None else stage
    hero_data = get_liquipedia_hero_data(tournament_name, stage)
    if not hero_data:
        raise ValueError("No hero data returned from page_scraper.")

    raw_rows = []
    for hero, stats in hero_data.items():
        picks, scraped_pick_rate = parse_pick_input(stats, total_games)
        raw_win_rate = parse_percent(stats["win_rate"])
        ban_rate = parse_percent(stats["ban_rate"]) or 0.0
        wins = 0.0 if raw_win_rate is None else picks * (raw_win_rate / 100)
        raw_rows.append(
            {
                "hero": hero,
                "picks": picks,
                "wins": wins,
                "raw_win_rate": raw_win_rate,
                "scraped_pick_rate": scraped_pick_rate,
                "ban_rate": ban_rate,
            }
        )

    if total_games is None:
        total_games = infer_total_games([row["ban_rate"] for row in raw_rows])
    if total_games is None:
        raise ValueError(
            "Could not infer total games from ban-rate increments. Pass --games explicitly."
        )

    total_picks = sum(row["picks"] for row in raw_rows)
    total_wins = sum(row["wins"] for row in raw_rows)
    global_win_rate = 0.5 if total_picks == 0 else total_wins / total_picks

    for row in raw_rows:
        row["pick_rate"] = (
            row["scraped_pick_rate"]
            if row["scraped_pick_rate"] is not None
            else (row["picks"] / total_games) * 100
        )
        row["presence"] = row["pick_rate"] + row["ban_rate"]
        row["ban_share"] = 0.0 if row["presence"] == 0 else row["ban_rate"] / row["presence"]
        row["adjusted_win_rate"] = (
            ((row["wins"] + (smoothing_games * global_win_rate)) / (row["picks"] + smoothing_games))
            * 100
            if row["picks"] > 0
            else global_win_rate * 100
        )

    weights = resolve_weights(
        [
            [row["pick_rate"], row["ban_rate"], row["adjusted_win_rate"]]
            for row in raw_rows
        ],
        weighting_method,
    )

    pick_rate_ranks = percentile_ranks([row["pick_rate"] for row in raw_rows])
    ban_rate_ranks = percentile_ranks([row["ban_rate"] for row in raw_rows])
    adjusted_win_rate_ranks = percentile_ranks([row["adjusted_win_rate"] for row in raw_rows])
    priority_scores = weighted_priority_score(
        pick_rate_ranks, ban_rate_ranks, adjusted_win_rate_ranks, weights
    )

    graded_rows: list[HeroGradeRow] = []
    for row, priority_score in zip(raw_rows, priority_scores):
        capped_grade = grade_cap(row["picks"], row["ban_rate"], row["presence"], total_games)
        computed_grade = lower_grade(base_grade(priority_score), capped_grade)
        graded_rows.append(
            HeroGradeRow(
                hero=row["hero"],
                picks=row["picks"],
                wins=round(row["wins"], 2),
                raw_win_rate=row["raw_win_rate"],
                adjusted_win_rate=round(row["adjusted_win_rate"], 2),
                pick_rate=round(row["pick_rate"], 2),
                ban_rate=round(row["ban_rate"], 2),
                presence=round(row["presence"], 2),
                ban_share=round(row["ban_share"], 4),
                priority_score=round(priority_score, 4),
                hero_grade=computed_grade,
                confidence=confidence_label(row["picks"], row["presence"], total_games),
                notes=build_notes(
                    row["picks"], row["presence"], row["ban_share"], row["raw_win_rate"]
                ),
            )
        )

    graded_rows.sort(
        key=lambda row: (
            GRADE_ORDER.index(row.hero_grade),
            row.priority_score,
            row.presence,
            row.adjusted_win_rate,
        ),
        reverse=True,
    )
    return graded_rows, total_games, weights


def print_report(
    rows: list[HeroGradeRow],
    tournament_name: str,
    stage: str,
    total_games: int,
    weights: dict[str, float],
    weighting_method: str,
) -> None:
    label = tournament_name if not stage else f"{tournament_name} / {stage}"
    print(f"Hero Grade report for {label}")
    print(f"Inferred total games: {total_games}")
    print(
        "Weights "
        f"({weighting_method}): "
        f"pick_rate={weights['pick_rate']:.3f}, "
        f"ban_rate={weights['ban_rate']:.3f}, "
        f"adjusted_win_rate={weights['adjusted_win_rate']:.3f}"
    )
    print(
        f"{'Hero':20} {'Grade':5} {'Score':6} {'Picks':5} {'Pick%':6} {'Ban%':6} "
        f"{'Presence':8} {'AdjWR%':7} {'Conf':6} Notes"
    )
    for row in rows:
        print(
            f"{row.hero:20} {row.hero_grade:5} {row.priority_score:6.3f} {row.picks:5d} "
            f"{row.pick_rate:6.2f} {row.ban_rate:6.2f} {row.presence:8.2f} "
            f"{row.adjusted_win_rate:7.2f} {row.confidence:6} {row.notes}"
        )


def write_csv(rows: list[HeroGradeRow], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate tournament hero grades from Liquipedia statistics."
    )
    parser.add_argument(
        "tournament_name",
        nargs="?",
        default=None,
        help=(
            "Optional Liquipedia tournament name override. If omitted, uses "
            f"page_scraper.DEFAULT_TOURNAMENT_NAME ({DEFAULT_TOURNAMENT_NAME})."
        ),
    )
    parser.add_argument(
        "--stage",
        default=None,
        help=(
            "Optional Liquipedia stage override. If omitted, uses "
            f"page_scraper.DEFAULT_STAGE ({DEFAULT_STAGE})."
        ),
    )
    parser.add_argument(
        "--games",
        type=int,
        default=None,
        help="Override total games if ban-rate inference is not possible.",
    )
    parser.add_argument(
        "--smoothing-games",
        type=int,
        default=8,
        help="Pseudo-games used to smooth win rate for small samples.",
    )
    parser.add_argument(
        "--weighting",
        choices=["critic", "entropy", "manual"],
        default="critic",
        help="How to determine feature weights for pick rate, ban rate, and adjusted win rate.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional CSV output path.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    tournament_name = args.tournament_name or DEFAULT_TOURNAMENT_NAME
    stage = DEFAULT_STAGE if args.stage is None else args.stage
    rows, total_games, weights = build_hero_grades(
        tournament_name=tournament_name,
        stage=stage,
        total_games=args.games,
        smoothing_games=args.smoothing_games,
        weighting_method=args.weighting,
    )
    print_report(rows, tournament_name, stage, total_games, weights, args.weighting)
    if args.output is not None:
        write_csv(rows, args.output)
        print(f"\nSaved CSV to {args.output}")


if __name__ == "__main__":
    main()
