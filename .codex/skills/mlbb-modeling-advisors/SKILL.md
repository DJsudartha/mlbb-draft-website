---
name: mlbb-modeling-advisors
description: Workflow for MLBB draft recommenders, advisor text generation, ranking logic, and backend tests. Use when changing pick or ban recommenders, advisor_pipeline, local advisor text builders, order-profile behavior, or recommendation payload semantics.
---

# MLBB Modeling Advisors

Read the repo-root `AGENTS.md` first.

## Workflow

1. Start from tests before editing logic. Read the most relevant files in `tests/`, especially recommender and advisor tests.
2. Inspect `backend/services/modeling/advisor_pipeline.py` and then the specific recommender or advisor modules the task touches.
3. Keep recommendation payloads stable unless the task explicitly changes the contract.
4. Prefer logic changes plus test updates over undocumented model or artifact regeneration.

## Guardrails

- Preserve turn resolution, unavailable-hero filtering, phase and order fields, and exposed metadata such as `order_profile`, `base_model_source`, and `base_model_name` unless the task changes those intentionally.
- The advisor layer currently uses a local semantic flow. Tests expect `uses_llm` to stay `False` and `provider` to stay `local-semantic` unless the task says otherwise.
- `sentence-transformers` may be unavailable at runtime. Keep the TF-IDF fallback path working.
- Do not retrain models or rewrite committed artifacts under `backend/data/` unless the task explicitly includes that work.

## Done

Run focused tests first when possible, then finish with:

- `python -m pytest -q`
- `ruff check backend tests`
