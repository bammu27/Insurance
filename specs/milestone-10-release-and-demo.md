# Milestone 10 — Release, Full Evaluation and Demo Rehearsal

**Feature:** The prototype is ready to show and ready to hand over.

Read `00-common-setup.md` first.

## Scope

- Grow `cases.json` to 30–40 cases: grounded Q&A, unsupported questions, correct clause/version, cross-customer access, employee with and without session, inactive product, unknown eligibility, overlap, sparse signals, CSV problems, unverified price, invalid citation, timeouts, audit on denial, hand-off wording.
- Write the README: setup, reset, limits, demo steps.
- Run the demo script (section 21 of `project.md`) three times.
- Complete the readiness checklist (section 23 of `project.md`).
- Only now, optionally add local embeddings or an approved model endpoint. Keep mock mode as default. Without embeddings, keep calling it keyword-only.

## Release gates (all must pass)

- All authorization tests pass, no cross-customer leak.
- Policy answers cite valid sources or fall back.
- No unsupported price or coverage claim in the suite.
- No ineligible product recommended.
- Hand-off never claims purchase or active cover.
- Seed recreates the same data every time.
- Core app works offline in mock mode.
- Latency measured and written down.
- README lists limits: synthetic data, mock model by default, no live quote or purchase, prototype security only.

## Manual test

| # | Do | Expect |
|---|---|---|
| 1 | Fresh clone, follow only the README | App runs. |
| 2 | Walk the 12-step demo script | Every step works, no surprises. |
| 3 | `python src/evaluation/run_tests.py` | All release gates pass. |
| 4 | Have someone else try the demo | They finish without help. Fix any confusing text. |

## Exit checklist

- [ ] 30–40 eval cases pass.
- [ ] README complete and tested from a fresh clone.
- [ ] Readiness checklist fully ticked.
- [ ] Latency table with sample sizes saved.
