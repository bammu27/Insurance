# Milestone 3 — Chat Quality

**Feature:** A general chat that gives grounded answers, shows progress, and falls back safely when it cannot verify.

Read `00-common-setup.md` first.

## Scope

**Backend**
- Intent routing: simple rules first (policy / general / recommendation / unsupported). A model only where it helps.
- General Q&A route: retrieve → answer from evidence → validate.
- Output validator: response shape, citation ids, unsupported premiums or limits, guarantees, purchase claims, data from other customers.
- One repair attempt, then deterministic fallback.
- Timeouts with at most one retry. Stage timers: validation, authorization, routing, DB, retrieval, model, validation, audit, total.

**Frontend**
- Chat bubbles and composer. Starter prompts: "Explain an exclusion in my policy", "Compare health and term insurance", "What information is missing to recommend cover?".
- Answer layout: direct answer, explanation, caveats, citations, one or two next actions.
- Real stage progress: "Checking access", "Searching policy sources", "Verifying citations".
- Send disabled while a request runs. Request id in the details panel.
- Fallback message with a safe next step.

## Acceptance criteria

- M3.1 Grounded answers carry valid citations.
- M3.2 Unsupported or out-of-scope questions get a safe, honest reply.
- M3.3 No price, limit or benefit unless evidence supports it. Otherwise: "Price requires an insurer quote".
- M3.4 A bad citation, timeout or purchase claim never reaches the user.
- M3.5 Double submit creates one request and one audit row.

## Manual test — frontend

| # | Do | Expect |
|---|---|---|
| 1 | Click each starter prompt | Each gets a structured answer. |
| 2 | Ask "What is the premium of the health product?" | "Price requires an insurer quote" or "Price not verified". |
| 3 | Ask "What is the weather today?" | Polite scope message, no made-up answer. |
| 4 | Click Send twice fast | One answer, one bubble. |
| 5 | Slow request (add a short sleep in the mock) | Stage text changes. Page never looks frozen. |
| 6 | Open request details | Request id visible. No hidden reasoning shown. |

## Manual test — backend

| # | Do | Expect |
|---|---|---|
| 1 | `MOCK_FAULT=bad_citation`, ask a question | `status: fallback`. Bad id never returned. |
| 2 | `MOCK_FAULT=timeout` | Fallback or clear "cannot verify". No invented answer. |
| 3 | `MOCK_FAULT=unsupported_price` | Price claim blocked or repaired once. |
| 4 | `MOCK_FAULT=purchase_claim` | "purchased" / "coverage active" never shown. |
| 5 | Ask about a topic with the poisoned chunk | Embedded instruction ignored. |
| 6 | Audit SQL after each run | Fallback reason and per-stage latency recorded. |
| 7 | Ask the same general question twice | Second run faster. Cache key includes user scope and document version. |

## Exit checklist

- [ ] All four fault cases tested by hand and by unit tests.
- [ ] Router accuracy checked on at least 15 sample questions.
- [ ] Stage timings visible in audit metadata.
