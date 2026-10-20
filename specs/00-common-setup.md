# Common Setup — Read This First

Applies to every milestone spec in this folder. Source: `project.md` (v1.1).

## Rule for every milestone

1. Read the milestone spec.
2. Build the backend part and the frontend part.
3. Run the automated tests (`pytest -q`).
4. Do the **manual frontend test** in the browser.
5. Do the **manual backend test** with the dev CLI, `sqlite3` and logs.
6. Tick the exit checklist. Commit. Only then start the next milestone.

Do not skip a manual test because unit tests are green.

## Milestone files

| File | Feature |
|---|---|
| `milestone-00-contracts-and-fixtures.md` | Shared contracts, fake service, seed data |
| `milestone-01-app-shell-and-identity.md` | Navigation, roles, authorization, audit base |
| `milestone-02-policy-slice.md` | My Policies, grounded policy answers |
| `milestone-03-chat-quality.md` | Chat, validation, fallback, progress |
| `milestone-04-manual-recommendation.md` | Needs wizard, hard gates, ranking |
| `milestone-05-behavior-signals-and-csv.md` | Manual signals, demo profile, CSV |
| `milestone-06-product-detail-and-handoff.md` | Details, comparison, mock hand-off |
| `milestone-07-employee-workspace.md` | Scoped assistance sessions |
| `milestone-08-quality-dashboard.md` | Metrics, admin pages, eval runner |
| `milestone-09-hardening.md` | Timeouts, cache safety, states, accessibility |
| `milestone-10-release-and-demo.md` | Full evaluation, README, rehearsal |

## Common commands (create in Milestone 0)

| Task | Command |
|---|---|
| Reset and seed data | `python data/seed_demo_data.py --reset` |
| Run the app | `streamlit run app.py` |
| Run all tests | `pytest -q` |
| Call backend without UI | `python scripts/dev_cli.py <method> --user <user_id> --json '<payload>'` |
| Look at audit rows | `sqlite3 insurance_demo.db "select timestamp_utc, actor_id, action, authorization_outcome, outcome, latency_ms from audit_events order by timestamp_utc desc limit 10;"` |

`dev_cli.py` calls the same service facade the UI calls and prints the full response as JSON. It never trusts a role from the payload. The user id you pass decides the identity. This is your **backend manual test tool**.

## Suggested fixtures (adjust names, keep the shape)

All data is fake. Seed must give the same rows every time.

| Item | Value |
|---|---|
| Users | `cust_a`, `cust_b`, `emp_1`, `admin_1` |
| Customer A | Active health policy `POL-A-HEALTH` (room-rent limit in wording). Expired travel policy `POL-A-TRAVEL`. |
| Customer B | Active term life policy `POL-B-TERM`. |
| Products | 6 total across health, term, motor, travel, home. One **inactive**. One with **unknown eligibility** for a normal profile. |
| Documents | At least 2 wording files with version and effective date. One chunk has a fake instruction ("ignore previous instructions") for injection tests. |
| Mock fault switch | Env var `MOCK_FAULT` = `none` / `bad_citation` / `timeout` / `unsupported_price` / `purchase_claim`. |

## Words used in specs

- **Expect** = what you must see.
- **FE** = frontend. **BE** = backend.
