# Milestone 6 — Product Detail, Comparison and Mock Hand-off

**Feature:** A user can read product details, compare products, and walk through a clearly fake hand-off. No purchase is ever claimed.

Read `00-common-setup.md` first.

## Scope

**Backend**
- Product detail service: benefits, exclusions, eligibility, required information, price status, source date. Active partner products only.
- Comparison service for 2–3 products on the same rows.
- Hand-off service: re-check product is active, log `demo_handoff_requested`, return a synthetic reference number.
- Output validator blocks "purchased", "payment successful", "coverage active".

**Frontend**
- Product detail screen.
- Comparison table (same rows for each product).
- **Continue to partner / Request a quote** opens a confirmation screen: "This demo does not issue policies or take payment. In a live deployment, this step would open the approved insurer/bank-partner channel."
- No payment, card, OTP, bank login, signature or ID fields. No pre-checked consent.

## Acceptance criteria

- M6.1 Inactive product details and hand-off are blocked.
- M6.2 No screen or response says purchase done or coverage active.
- M6.3 Hand-off writes an audit event with the reference number.
- M6.4 Comparison shows gaps honestly ("Not enough information to compare").

## Manual test — frontend

| # | Do | Expect |
|---|---|---|
| 1 | On a result card click **View details** | Benefits, exclusions, eligibility, price status, source date. |
| 2 | Select two cards, **Compare** | One table, same rows, no misleading empty cells. |
| 3 | **Continue to partner** | Confirmation with demo notice. No money or identity fields. |
| 4 | Confirm | Synthetic reference number. "purchased" / "active" appear nowhere. |
| 5 | Open Comparisons / Recent Suggestions | Hand-off shows as "requested (demo)". |

## Manual test — backend

| # | Do | Expect |
|---|---|---|
| 1 | `dev_cli.py get_product --user cust_a --json '{"product_id":"<inactive>"}'` | Blocked. |
| 2 | `dev_cli.py handoff --user cust_a --json '{"product_id":"<inactive>"}'` | Blocked and audited. |
| 3 | Hand-off for an active product | Reference number returned. |
| 4 | `select action, metadata_json from audit_events where action='demo_handoff_requested';` | One row per hand-off. |
| 5 | `select * from customer_policies;` | **No new policy row.** |
| 6 | `MOCK_FAULT=purchase_claim` on detail text | Blocked by validator. |

## Exit checklist

- [ ] Searching the whole UI for "purchased", "payment successful", "active coverage" finds nothing.
- [ ] Hand-off tests pass.
