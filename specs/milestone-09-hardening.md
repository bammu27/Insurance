# Milestone 9 — Hardening

**Feature:** The app behaves well when things go wrong and runs the same way every time.

Read `00-common-setup.md` first.

## Scope

**Backend**
- Timeouts and at most one retry for retrieval, model and optional web calls.
- Cache keys with user scope, normalized query, document/product versions, access context. Invalidate on source or catalog change.
- Logging without secrets or raw transactions.
- Reset and seed scripts. DB indexes on customer, policy, product, category, date.
- Documents ingested ahead of time, never parsed per request.

**Frontend**
- Every screen has: empty, loading, validation error, safe fallback, offline/mock, and success states.
- Accessibility: form labels, text next to every color, keyboard use, no horizontal scroll at laptop width.
- Retry never creates duplicate recommendations or audit rows.

## Acceptance criteria

- M9.1 Full regression suite passes.
- M9.2 Repeated runs give stable percentiles with sample sizes.
- M9.3 Cache never leaks one user's data to another.
- M9.4 The core demo works with no network.

## Manual test — frontend

| # | Do | Expect |
|---|---|---|
| 1 | Turn off Wi-Fi, run the whole customer demo | Works in mock mode. |
| 2 | Visit every page with a brand-new empty DB | Helpful empty states, no stack traces. |
| 3 | Use Tab and Enter only | Every form and button reachable. |
| 4 | Shrink to a typical laptop width | No sideways scrolling. |
| 5 | Force each `MOCK_FAULT` value | Calm message with a next step each time. |

## Manual test — backend

| # | Do | Expect |
|---|---|---|
| 1 | Ask a policy question as `cust_a`, then ask for A's policy as `cust_b` | Second call denied. No cached answer. |
| 2 | Change a document version, ask again | New answer with new version. |
| 3 | 50-request loop per workflow | p50/p95 with sample size, warm and cold. |
| 4 | Search logs for "api_key", raw descriptions, full transaction rows | Nothing found. |
| 5 | Reset and seed, `pytest -q` | All green. |

## Exit checklist

- [ ] Latency table written (workflow, stage, p50, p95, p99, n).
- [ ] No unfinished states left on any screen.
