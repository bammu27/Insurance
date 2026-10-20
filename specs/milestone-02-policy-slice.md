# Milestone 2 — Policy Slice (First Full Vertical Slice)

**Feature:** A customer sees their own policies and asks about one. The answer is grounded and cited. Another customer cannot reach it.

Read `00-common-setup.md` first.

## Scope

**Backend**
- Ownership check on every policy call.
- Structured policy lookup (status, dates, coverage JSON).
- Ingest wording documents into `documents` and `document_chunks`. SQLite FTS5 keyword search. Label it **keyword-only**.
- LangGraph flow: `validate → authenticate → authorize → classify → policy route → retrieve → mock answer → validate citations → audit`.
- Mock adapter builds the answer only from the record and retrieved chunks.
- Neutral denial: same message for "not yours" and "does not exist".

**Frontend**
- My Policies cards (insurer, product, status, dates, View details).
- Policy detail: structured facts, coverage summary, wording, **Ask about this policy**.
- Answer has two labeled parts: **From your policy record** and **From policy wording**.
- Citation list. A click opens source detail (title, insurer/product, version, effective date, page/section).

## Acceptance criteria

- M2.1 Customer A sees only A's policies.
- M2.2 Answer separates record facts from wording.
- M2.3 Every citation id is one of the chunks retrieved in this request.
- M2.4 Customer B asking for A's policy gets a neutral denial and an audit row.
- M2.5 Marketing text never overrides contract wording for an existing policy.

## Manual test — frontend

| # | Do | Expect |
|---|---|---|
| 1 | Sign in as `cust_a`, open My Policies | Two cards: health (active), travel (expired). No B policy. |
| 2 | Open health detail | Facts match seed data. |
| 3 | **Ask about this policy**: "Is there a room rent limit?" | Both labeled sections and at least one citation. |
| 4 | Click a citation | Source detail with version and effective date. |
| 5 | Ask something the wording does not cover | Says not found, suggests asking the insurer. No invented clause. |
| 6 | Sign in as `cust_b`, open My Policies | Only B's term policy. |

## Manual test — backend

| # | Do | Expect |
|---|---|---|
| 1 | `dev_cli.py ask_policy --user cust_a --json '{"policy_id":"POL-A-HEALTH","text":"Is there a room rent limit?"}'` | `status: ok`, citations, `request_id`, `latency_ms`. |
| 2 | Same call with `--user cust_b` | `status: denied`, neutral message. |
| 3 | `policy_id: POL-DOES-NOT-EXIST` as `cust_b` | **Exactly the same** message as step 2. |
| 4 | Audit SQL | Rows for the success and both denials. No raw question text beyond what the spec allows. |
| 5 | Check each citation id against `document_chunks` | All exist and were in the retrieval result. |
| 6 | Run step 1 twenty times, note times | Typical local run under 2 seconds. Record p50/p95. |

## Exit checklist

- [ ] Cross-customer test passes.
- [ ] Citation validator test passes.
- [ ] Audit row exists for success and denial.
- [ ] First timing numbers written down.
