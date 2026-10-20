# Milestone 7 — Employee Workspace

**Feature:** An employee can help a customer only inside a clear, purpose-bound, revocable session.

Read `00-common-setup.md` first.

## Scope

**Backend**
- `assistance_sessions`: start (customer id + purpose), end, status.
- Authorization checks the active session on **every** call touching customer data, including cache hits.
- Ending a session removes access at once.
- Audit for start, each access, end, and every denial.

**Frontend**
- Customer search by fake id or name. Purpose picker. **Start assistance session**.
- Persistent banner: employee, customer, purpose, session state. On every page.
- Policy review and chat for that customer inside the session.
- **End session** clears customer context from the page.
- Recent Sessions list.

## Acceptance criteria

- M7.1 No customer data without an active session.
- M7.2 A session is tied to one customer. Another customer is denied.
- M7.3 After End session, the same call is denied.
- M7.4 Employee cannot override eligibility gates.

## Manual test — frontend

| # | Do | Expect |
|---|---|---|
| 1 | Sign in as `emp_1`, search "Customer A" | Minimal info only. |
| 2 | Open A's policies without a session | Blocked with a clear message. |
| 3 | Pick purpose, start session | Banner appears and stays on every page. |
| 4 | Open A's policy, ask a question | Works, same format as customer view. |
| 5 | Try to switch to Customer B inside the session | Not possible without ending and starting a new session. |
| 6 | **End session** | Banner gone, data cleared. Browser Back does not show it. |

## Manual test — backend

| # | Do | Expect |
|---|---|---|
| 1 | `dev_cli.py get_policies --user emp_1 --customer cust_a` (no session) | Denied, audited. |
| 2 | `dev_cli.py start_session --user emp_1 --json '{"customer_id":"cust_a","purpose":"policy_question"}'` | Session id returned. |
| 3 | Repeat step 1 | `ok`. |
| 4 | Same call for `cust_b` | Denied. |
| 5 | `dev_cli.py end_session ...`, then step 1 again | Denied. |
| 6 | Repeat a cached question after ending the session | Denied (auth before cache). |
| 7 | `select * from assistance_sessions;` | `ended_at` filled. |

## Exit checklist

- [ ] Session tests cover start, use, wrong customer, end, and cache.
- [ ] Banner test passes.
