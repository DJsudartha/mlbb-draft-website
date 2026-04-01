---
name: mlbb-data-refresh-scripts
description: Workflow for MLBB Draft Website scraping, data refresh, processed-data rebuilds, and model retraining. Use when running or editing scripts under backend/scripts, Liquipedia ingestion, tournament refresh, counter or synergy rebuilds, or model artifact generation.
---

# MLBB Data Refresh Scripts

Read the repo-root `AGENTS.md` first.

## Workflow

1. Classify the task before doing work: raw-data refresh, processed-data rebuild, or model retraining.
2. Start with the smallest script set inside `backend/scripts/` that can satisfy the task.
3. Check `backend/.env.example` and confirm whether Liquipedia keys or network access are required.
4. Treat generated outputs under `backend/data/raw/`, `backend/data/processed/`, and `backend/data/modeling/models/` as intentional artifacts that should only change when the task calls for it.

## Guardrails

- Do not run broad scrape or training pipelines casually. They can create large committed diffs.
- If credentials or network access are missing, stop and report that blocker instead of guessing.
- Keep raw ingestion, processed rebuilds, and model training as separate concerns in both code changes and explanations.
- After data work, summarize exactly which scripts ran and which artifact paths changed.

## Done

When script or Python source code changes, run:

- `python -m pytest -q`
- `ruff check backend tests`

When the task is artifact-only, report the changed data or model files explicitly even if no tests were needed.
