# Milestone 0 — Contracts and Fixtures

**Feature:** All screens and services agree on one set of request/response shapes. A fake service lets the UI be built first.

Read `00-common-setup.md` first.

## Scope

**Backend**
- Typed models (Pydantic, `extra="forbid"`): `ChatRequest/ChatResponse`, `PolicySummary/PolicyDetail`, `BehaviorImportPreview/BehaviorImportResult`, `NeedsAssessment/RecommendationResponse`, `ProductDetail/DemoHandoffResponse`, `FeedbackRequest/FeedbackResult`, `AuditSummary/LatencySummary`.
- Every response has: `request_id`, `status` (`ok` / `denied` / `fallback` / `error`), `message`, `citations`, `warnings`, `latency_ms`.
- `InsuranceService` interface and `FakeInsuranceService` returning fixed synthetic answers.
- SQLite schema (all tables from section 11 of the spec) and a deterministic seed script.
- `scripts/dev_cli.py`.

**Frontend**
- `app.py` with a temporary **UI States** page showing fake service output: success, denied, fallback, error, empty, loading.

## Acceptance criteria

- M0.1 No request has a trusted `actor_role` or `customer_id`. Sending one is rejected.
- M0.2 Running the seed twice gives identical data.
- M0.3 Fake and (later) real service share one interface.
- M0.4 UI shows all six states without crashing.

## Manual test — frontend

| # | Do | Expect |
|---|---|---|
| 1 | `streamlit run app.py`, open **UI States** | Loads in under 1 second. |
| 2 | Look at the success sample | Message, one citation (title, version, date), `request_id`, `latency_ms`. |
| 3 | Look at denied, fallback, error samples | Clear words, not only color. |
| 4 | Look at empty and loading samples | Empty says what to do next. Loading shows a stage name. |

## Manual test — backend

| # | Do | Expect |
|---|---|---|
| 1 | Seed with `--reset` twice. After each: `sqlite3 insurance_demo.db ".dump" \| sha256sum` | Same hash both times. |
| 2 | `dev_cli.py chat --user cust_a --json '{"text":"hello"}'` | Valid JSON with all envelope fields. |
| 3 | Same call with `"actor_role":"admin"` in the JSON | Validation error. Request not run. |
| 4 | Send empty text | Clear validation error, status `error`. |

## Exit checklist

- [x] Contract tests pass for the fake service.
- [x] Seed hash is stable.
- [x] All six UI states render.

