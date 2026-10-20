# Milestone 1 — App Shell and Identity

**Feature:** A signed-in demo user sees the right navigation. The backend blocks actions that user is not allowed to do.

Read `00-common-setup.md` first.

## Scope

**Backend**
- `demo_auth`: identity comes from the server session, never from request fields.
- `authorization`: table of `role → allowed actions`. `authorize(identity, action, target)`.
- `audit_service`: one audit row per call, including denials. Fails closed if auth or DB fails.

**Frontend**
- Global header: "Bank Insurance Assistant", role label, **DEMO — synthetic data** label, `Mock` / endpoint label, "How my data is used" link, quiet expandable request details.
- Demo sign-in switcher (customer A, customer B, employee, admin).
- Role-based navigation (lists from the spec). Placeholder pages are fine.

## Acceptance criteria

- M1.1 Each role sees only its own menu.
- M1.2 A customer calling an admin or employee action is denied by the backend, even via URL or state tampering.
- M1.3 Every denial creates an audit row with `authorization_outcome=denied`.
- M1.4 If the DB is unavailable, the call fails closed with no data.

## Manual test — frontend

| # | Do | Expect |
|---|---|---|
| 1 | Sign in as `cust_a` | Menu: Home, Chat, My Policies, Find Cover, Comparisons, Help & Data Controls. Header shows Customer + DEMO label. |
| 2 | Switch to `emp_1` | Employee menu. |
| 3 | Switch to `admin_1` | Admin menu. |
| 4 | Open "How my data is used" | Plain page about synthetic data and the mock model. |
| 5 | Expand request details | Request id and runtime (`Mock`). |

## Manual test — backend

| # | Do | Expect |
|---|---|---|
| 1 | `dev_cli.py get_latency_summary --user cust_a` | `status: denied`. No metrics. |
| 2 | Run the audit SQL | New row: actor `cust_a`, `authorization_outcome=denied`. |
| 3 | `dev_cli.py get_latency_summary --user admin_1` | `status: ok`. |
| 4 | `dev_cli.py ... --user cust_a --claim-role admin` | Claimed role ignored. Still denied. |
| 5 | Rename `insurance_demo.db`, call any method | Error, no data. Rename it back. |

## Exit checklist

- [ ] Authorization unit tests pass for every role and action.
- [ ] Denials are audited.
- [ ] Header labels always visible.
