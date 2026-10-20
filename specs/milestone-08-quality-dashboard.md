# Milestone 8 — Quality Dashboard and Evaluation Runner

**Feature:** An admin sees how fast and how correct the system is, from real measured data.

Read `00-common-setup.md` first.

## Scope

**Backend**
- Metrics: p50 / p95 / p99 latency (overall, per workflow, per stage), sample size, warm vs cold.
- Citation validity, fallback rate and reasons, authorization denials, hard-gate violations (target 0), stale or missing sources, provider status.
- Evaluation runner `src/evaluation/run_tests.py` with `cases.json` (start with 15 cases, grow to 30–40 by Milestone 10). Results saved for the dashboard.
- Admin sees minimal audit fields. No raw prompts or transaction text.

**Frontend**
- Admin pages, lazy loaded: Quality Dashboard, Product Catalog, Source Library & Freshness, Feedback Review, Audit Events, Evaluation Lab.
- Metric cards and charts: latency by stage, fallback reasons, eval results by category.
- Every number shows its sample size.

## Acceptance criteria

- M8.1 p50/p95 match a hand calculation on a small known data set.
- M8.2 Running the eval updates the dashboard.
- M8.3 Admin cannot read customer policy content from these pages.
- M8.4 Non-admin cannot call any admin service.

## Manual test — frontend

| # | Do | Expect |
|---|---|---|
| 1 | Sign in as `admin_1`, open Quality Dashboard | Cards load with sample sizes. No customer pages here. |
| 2 | **Run evaluation** in Evaluation Lab | Progress, then pass/fail per case with reasons. |
| 3 | Return to dashboard | Eval pass rate updated. |
| 4 | Open Audit Events | Minimal fields only. No question text or transaction descriptions. |
| 5 | Open Source Library & Freshness | Stale or missing sources flagged with words, not only color. |

## Manual test — backend

| # | Do | Expect |
|---|---|---|
| 1 | In a test DB insert 5 audit rows with latencies 100, 200, 300, 400, 500. Call `get_latency_summary`. | p50 = 300. p95 matches your hand calculation. |
| 2 | `python src/evaluation/run_tests.py` | Prints summary, writes results. Non-zero exit if any release gate fails. |
| 3 | Break a rule on purpose (let an inactive product through) | Eval fails. Dashboard shows a hard-gate violation. Undo it. |
| 4 | Call admin methods as `cust_a` and `emp_1` | Denied, audited. |

## Exit checklist

- [ ] Metric math has unit tests.
- [ ] Dashboard reads the same audit data the app writes.
