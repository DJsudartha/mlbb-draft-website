#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: GitHub CLI (gh) is not installed."
  echo "Install: https://cli.github.com/"
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Error: gh is not authenticated. Run: gh auth login"
  exit 1
fi

create_issue() {
  local title="$1"
  local body="$2"
  local labels="$3"

  echo "Creating issue: ${title}"
  gh issue create \
    --title "$title" \
    --body "$body" \
    --label "$labels"
}

create_issue \
"Frontend: verify production build locally" \
"## Goal
Verify the frontend is production-ready before deployment.

## Tasks
- [ ] Install dependencies
- [ ] Run lint
- [ ] Run typecheck
- [ ] Run build
- [ ] Record any errors in issue comments

## Done when
- [ ] Build completes with no errors" \
"epic:mvp-deploy,size:xs,priority:high,area:frontend"

create_issue \
"Backend: run FastAPI app in production-like mode" \
"## Goal
Confirm backend can boot and serve core API routes.

## Tasks
- [ ] Install backend dependencies
- [ ] Start backend with uvicorn
- [ ] Verify / health endpoint
- [ ] Verify one draft endpoint with sample payload

## Done when
- [ ] Backend starts cleanly and returns valid JSON" \
"epic:mvp-deploy,size:xs,priority:high,area:backend"

create_issue \
"Frontend: configure API base URL for deployed backend" \
"## Goal
Use environment-based API URLs instead of hardcoded values.

## Tasks
- [ ] Add env-based API URL for dev/prod
- [ ] Replace hardcoded API URL usage
- [ ] Validate local dev behavior

## Done when
- [ ] Frontend uses correct API URL per environment" \
"epic:mvp-deploy,size:s,priority:high,area:frontend"

create_issue \
"Backend: allow deployed frontend origin in CORS" \
"## Goal
Prevent CORS failures from production frontend.

## Tasks
- [ ] Add production frontend domain to CORS allowlist
- [ ] Keep localhost origins for dev
- [ ] Verify browser requests succeed

## Done when
- [ ] No CORS errors in production browser console" \
"epic:mvp-deploy,size:xs,priority:high,area:backend"

create_issue \
"Docs: add post-deploy smoke test checklist" \
"## Goal
Document a quick deployment verification flow.

## Tasks
- [ ] Add smoke test checklist to README/docs
- [ ] Include recommendation request validation
- [ ] Include expected outcomes

## Done when
- [ ] A collaborator can validate deployment in <10 minutes" \
"epic:mvp-deploy,size:xs,priority:medium,area:docs"

create_issue \
"Backend: create draft evaluator API contract" \
"## Goal
Define stable evaluator request/response schema.

## Tasks
- [ ] Define request fields
- [ ] Define response fields (scores, insights, risks)
- [ ] Provide sample payloads

## Done when
- [ ] Contract is documented and agreed" \
"epic:draft-evaluator,size:s,priority:high,area:backend"

create_issue \
"Backend: add /draft/evaluate route" \
"## Goal
Expose evaluator via API endpoint.

## Tasks
- [ ] Add route handler
- [ ] Validate request body
- [ ] Return structured placeholder response

## Done when
- [ ] Endpoint responds with valid schema" \
"epic:draft-evaluator,size:s,priority:high,area:backend"

create_issue \
"Evaluator: compute team role coverage score" \
"## Goal
Score role balance/completeness for both teams.

## Tasks
- [ ] Define role-coverage rules
- [ ] Implement score calculation
- [ ] Include score in evaluator response

## Done when
- [ ] Response includes role coverage metrics for blue/red" \
"epic:draft-evaluator,size:s,priority:medium,area:modeling"

create_issue \
"Evaluator: add synergy and counter insights" \
"## Goal
Explain why evaluator score looks the way it does.

## Tasks
- [ ] Return top synergy insights
- [ ] Return top counter insights
- [ ] Add short readable explanations

## Done when
- [ ] Evaluator includes useful text insights" \
"epic:draft-evaluator,size:s,priority:medium,area:modeling"

create_issue \
"Frontend: add Draft Evaluator panel" \
"## Goal
Allow users to run and view evaluator results in UI.

## Tasks
- [ ] Add Evaluate Draft button
- [ ] Call evaluator endpoint
- [ ] Render score + insights
- [ ] Handle loading and error states

## Done when
- [ ] User can evaluate current draft from frontend" \
"epic:draft-evaluator,size:s,priority:high,area:frontend"

create_issue \
"Tests: add evaluator backend test coverage" \
"## Goal
Protect evaluator behavior from regressions.

## Tasks
- [ ] Add valid request test
- [ ] Add invalid/edge-case tests
- [ ] Assert response shape

## Done when
- [ ] Evaluator tests pass in CI" \
"epic:draft-evaluator,size:s,priority:high,area:tests"

create_issue \
"Frontend: create default home route" \
"## Goal
Introduce a landing page at /. 

## Tasks
- [ ] Add home page component
- [ ] Make / default route
- [ ] Keep simulator accessible via dedicated route

## Done when
- [ ] App lands on home page by default" \
"epic:homepage,size:s,priority:medium,area:frontend"

create_issue \
"Home page: add feature navigation cards" \
"## Goal
Help users discover available and planned features.

## Tasks
- [ ] Add Draft Simulator card
- [ ] Add Draft Evaluator card
- [ ] Add Profile Dashboard (coming soon) card

## Done when
- [ ] Home page clearly routes users to features" \
"epic:homepage,size:xs,priority:medium,area:frontend"

create_issue \
"UI: add top navigation component" \
"## Goal
Provide simple navigation across Home and Simulator.

## Tasks
- [ ] Add navbar component
- [ ] Show active route state
- [ ] Verify mobile behavior

## Done when
- [ ] Navigation is usable on desktop and mobile" \
"epic:homepage,size:s,priority:medium,area:frontend,ux"

create_issue \
"Frontend: validate GitHub Pages route behavior" \
"## Goal
Ensure SPA routes work with Pages base path.

## Tasks
- [ ] Test direct route access
- [ ] Test browser refresh on nested routes
- [ ] Document caveats/workarounds

## Done when
- [ ] Deployed route behavior is stable and documented" \
"epic:homepage,size:xs,priority:medium,area:frontend"

create_issue \
"Architecture: choose DB and ORM stack" \
"## Goal
Pick a stable database foundation for auth/profile features.

## Tasks
- [ ] Compare candidate stacks briefly
- [ ] Select DB + ORM
- [ ] Record decision in docs

## Done when
- [ ] Team has one documented database direction" \
"epic:database-foundation,size:s,priority:medium,area:backend,area:data"

create_issue \
"Database: define v1 schema (users/profiles/saved_drafts)" \
"## Goal
Create minimal schema for future user features.

## Tasks
- [ ] Define users table
- [ ] Define profiles table
- [ ] Define saved_drafts table
- [ ] Set PK/FK constraints

## Done when
- [ ] v1 schema is reviewed and documented" \
"epic:database-foundation,size:s,priority:medium,area:data"

create_issue \
"Backend: add migration workflow" \
"## Goal
Enable reproducible database schema setup.

## Tasks
- [ ] Configure migration tool
- [ ] Create initial migration
- [ ] Document migration commands

## Done when
- [ ] Fresh environment can run migrations successfully" \
"epic:database-foundation,size:s,priority:medium,area:backend"

create_issue \
"Backend: add env-based DB connection config" \
"## Goal
Connect backend to database using env vars.

## Tasks
- [ ] Add DB connection env vars
- [ ] Wire startup DB connection
- [ ] Add clear startup error handling

## Done when
- [ ] Backend starts successfully with DB configured" \
"epic:database-foundation,size:s,priority:medium,area:backend"

create_issue \
"Backend: add DB healthcheck endpoint" \
"## Goal
Expose operational visibility for DB connectivity.

## Tasks
- [ ] Add DB healthcheck route
- [ ] Return pass/fail JSON status
- [ ] Document expected output

## Done when
- [ ] Endpoint reflects live DB connectivity" \
"epic:database-foundation,size:xs,priority:low,area:backend"

create_issue \
"Backend: add saved draft CRUD endpoints" \
"## Goal
Support storing and retrieving drafts for future accounts.

## Tasks
- [ ] Add create saved draft endpoint
- [ ] Add list saved drafts endpoint
- [ ] Add get draft by id endpoint

## Done when
- [ ] Draft records can be saved and fetched" \
"epic:database-foundation,size:s,priority:medium,area:backend"

echo "All issues have been submitted via GitHub CLI."
