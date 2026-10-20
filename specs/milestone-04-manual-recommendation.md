# Milestone 4 — Manual Recommendation (No CSV Yet)

**Feature:** A customer answers a few needs questions and gets up to three explainable, safe product suggestions.

Read `00-common-setup.md` first.

## Scope

**Backend**
- `features.py`: aggregate confirmed needs and existing cover (no transactions yet).
- `guardrails.py` hard gates: active approved partner; eligibility confirmed and passed; enough evidence; existing cover reviewed; no source conflict; price "verified" only with real quote data.
- `scoring.py`: need 35, behavior 20, gap 20, eligibility 15, verified info 10. A score never overrides a failed or unknown gate.
- Explanation builder: 2–3 reasons, highlights, exclusions, overlap, price status, source date.
- Save `recommendations` and `feedback`. Audit with gate results. Retry does not duplicate records.

**Frontend**
- Find Cover wizard with progress and Back: Step 1 choose source (only "Answer a few questions" works now), Step 3 needs questions, Step 4 review and confirm, Step 5 results.
- Cards: product, insurer, category, fit label ("May fit based on the information you confirmed"), reasons, highlights, exclusions, overlap, price status, source date, **Helpful / Not helpful**. Compare and Continue buttons appear but work in Milestone 6.

## Acceptance criteria

- M4.1 At most three results.
- M4.2 Inactive products never appear.
- M4.3 Unknown eligibility means excluded.
- M4.4 Existing cover of the same type shows overlap or lowers the result.
- M4.5 No fake probability, "best" or "guaranteed" wording.
- M4.6 Changing the confirmed need changes the results.

## Manual test — frontend

| # | Do | Expect |
|---|---|---|
| 1 | As `cust_a`: Find Cover → questions → "Health costs", already have health cover | Review lists answers and unknowns. |
| 2 | Confirm | Up to 3 cards. Health overlap shown. |
| 3 | Go Back, change need to "Vehicle" | Different results. |
| 4 | Check every card | "Price requires an insurer quote". Source date present. |
| 5 | Click **Not helpful** | Thank-you message. Second click adds nothing. |
| 6 | Refresh results page | No duplicate cards or records. |

## Manual test — backend

| # | Do | Expect |
|---|---|---|
| 1 | `dev_cli.py recommend --user cust_a --json '{...needs...}' --explain` | Per-product gate table: pass / fail / unknown. |
| 2 | Find the inactive product | `active_partner = fail`. Not in results. |
| 3 | Find the unknown-eligibility product | `eligibility = unknown`. Not in results. |
| 4 | Same request twice | No duplicate rows. |
| 5 | `select * from recommendations;` | Reasons and assumptions saved. |
| 6 | `select * from feedback;` | One row per feedback click. |
| 7 | Audit SQL | Guardrail outcome recorded per candidate. |

## Exit checklist

- [ ] Hard-gate unit tests: zero violations.
- [ ] Ranking test shows weights change order as expected.
- [ ] Local recommendation p50 under 3 seconds (record numbers).
