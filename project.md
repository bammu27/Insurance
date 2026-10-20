# AI Insurance Assistant --- Complete Product, UX, Architecture & Test-Driven Delivery Specification

**Version:** 1.1\
**Date:** 20 October 2026\
**Status:** Implementation specification for a local prototype\
**Primary stack:** Python, Streamlit, LangGraph, SQLite, hybrid
retrieval where feasible\
**Data:** Synthetic only\
**Default model runtime:** Deterministic mock adapter; optional approved
endpoint\
**Primary quality goals:** Correctness, grounded answers, authorization,
low latency, explainability, excellent user experience

------------------------------------------------------------------------

## 1. Executive summary

Build a polished, highly responsive insurance assistant web application for an Indian bank serving authenticated customers and administrators. It supports:

1.  **Secure Authentication**:
    -   Customer sign-in with **Customer ID & Password**.
    -   Admin sign-in gated by an **Admin Key & Admin Password** configured in `.env`.
2.  **Customer Main Dashboard**:
    -   Immediate **Personalized Recommendations** displayed at the top with fit labels, pricing status, and evidence-backed rationale.
    -   Direct **Buy Policy Navigation**: Users click a "Buy Policy" button on any recommended product to navigate to an interactive purchase configuration page. Completing the purchase commits an active policy record directly to the database.
    -   **Signal Upload**: Upload JSON or CSV files or manually enter signals to refine recommendations.
    -   **Dual-Mode Chatbot**:
        -   *My Bought Policies*: Queries grounded in policies the user currently owns (distinguishing record facts from contractual wording).
        -   *General Policy & Insurance Q&A*: Grounded answers sourced from approved documents via the RAG pipeline.
3.  **Admin Document Portal & Advanced RAG Pipeline**:
    -   Admins securely upload new policy documents (PDF, text, Markdown).
    -   Automated ingestion triggers document validation, semantic chunking, and high-speed keyword + hybrid indexing.
4.  **Priority on Latency & Quality**:
    -   Target low-latency response times (<2s local lookup/FAQ, <4s RAG answers).
    -   Evidence-grounded answers with mandatory citation validation and strict authorization boundaries.

### Priority order

1.  Correctness, evidence, access control and suitability guardrails.
2.  Response quality and clarity.
3.  End-to-end latency and perceived responsiveness.
4.  Explainable recommendations and user control.
5.  Polished UX, reliable demo and repeatable tests.

Do not sacrifice authorization or factual grounding to hit a latency
target. If the system cannot verify an answer, it should say what is
known, what is missing, and what the user can do next.

## 2. Product principles

-   **Evidence before eloquence:** policy-specific claims require
    evidence from the relevant record or applicable wording.
-   **Fast first, deeper second:** render the UI quickly and show
    meaningful progress by stage.
-   **User control:** explain behavior signals, allow
    correction/ignore/delete, and provide manual input when no CSV
    exists.
-   **Transactions are clues, not facts about a person:** a travel
    purchase does not prove a future trip; pharmacy spending does not
    prove a diagnosis; childcare purchases do not prove parenthood.
-   **Suitability before ranking:** eligibility, active partner status,
    evidence sufficiency and duplicate-cover checks are hard gates.
-   **No invented prices:** show a verified price only when
    authoritative current pricing/quote data supports it. Otherwise say
    "Price requires an insurer quote" or "Price not verified."
-   **Visible provenance:** show sources, version/effective date and
    relevant limitations.
-   **No dark patterns:** no false urgency, misleading "Buy now" claims,
    preselected purchase consent or hidden exclusions.
-   **Privacy by default:** synthetic data only; minimize stored free
    text and raw transactions.
-   **Honest prototype boundary:** product detail and mock partner
    hand-off are allowed; policy purchase/issuance/payment are out of
    scope.

## 3. User groups and permissions

### Customer

Can ask general questions, see only their own policies, enter/import
synthetic behavior data, review and correct signals, complete a needs
questionnaire, see recommendations, compare products, give feedback, and
use the mock hand-off flow.

Cannot see another customer's data, internal audit records, or
employee/admin pages. Cannot purchase or activate a policy in the
prototype.

### Employee

Can search synthetic customers, start an explicit assistance session
with a purpose, and view permitted customer details within that session.
The UI must clearly show the active assisted-customer context. The
employee must end the session when done.

Cannot browse arbitrary customer records without authorization or
override eligibility/suitability controls.

### Administrator

Can review catalog status, source freshness, feedback, evaluation
results, latency and minimized audit events. Admin status does not
automatically grant unrestricted access to customer policy content.

## 4. Core journeys

### Journey A --- General insurance question

Ask → validate request → retrieve relevant approved evidence → draft
answer → validate citations/claims → show answer and sources → audit.

### Journey B --- Existing policy

Open My Policies or ask a question → backend verifies ownership → fetch
structured policy facts → retrieve applicable policy wording → answer
with record facts separated from wording interpretation → validate
citations → audit. If ownership fails, return a neutral denial without
revealing whether another person's policy exists.

### Journey C --- Personalized recommendation

Choose input source → review behavior signals → answer needs questions →
confirm summary → apply hard gates → rank eligible partner products →
show explanations/coverage/limitations/price status → compare or view
details → optional mock partner hand-off → feedback and audit.

### Journey D --- Employee assistance

Search synthetic customer → select purpose → start scoped session → show
persistent assistance banner → perform authorized work → end session and
clear target context.

### Journey E --- Admin quality review

Review p50/p95 latency, citation validity, evaluation pass rate,
fallback rate, auth denials, stale sources and failed test cases. Raw
prompts and transaction descriptions are not shown by default.

## 5. Navigation and visual direction

### Visual style

Modern, calm financial-services product rather than a generic developer
dashboard: - Light neutral surfaces, restrained navy/blue accent,
generous whitespace. - Consistent spacing, typography and button
hierarchy. - Use green only for verified/success states, amber for
attention, red for blocked/error; never rely on color alone. - Avoid a
large hero that pushes useful tasks below the fold. - Keep content
readable at typical laptop width and avoid horizontal scrolling. - Use
clear labels beside important icons and accessible form labels.

### Customer navigation

-   Home
-   Chat
-   My Policies
-   Find Cover
-   Comparisons / Recent Suggestions
-   Help & Data Controls

### Employee navigation

-   Employee Workspace
-   Customer Search
-   Active Assistance Session
-   Policy Review / Chat
-   Recent Sessions

### Admin navigation

-   Quality Dashboard
-   Product Catalog
-   Source Library & Freshness
-   Feedback Review
-   Audit Events
-   Evaluation Lab

Navigation visibility is not security. Backend authorization is required
for every sensitive operation.

## 6. Screen-by-screen UX specification

### 6.1 Global header

-   App title: "Bank Insurance Assistant"
-   Role indicator: Customer / Employee / Admin
-   Persistent "DEMO --- synthetic data" environment label
-   "How my data is used" link
-   Optional request/session details in a quiet expandable panel
-   Show whether model runtime is `Mock` or an approved configured
    endpoint; never imply the mock is a real insurer service.

### 6.2 Home

Show: - Welcome message and concise description. - Three primary cards:
"Ask a question", "Review my policies", "Find cover that fits". - Policy
summary counts and statuses, limited to the current user's own
records. - Recent suggestions/activity, if available. - Source status:
demo catalog loaded, policy library freshness, live quote unavailable. -
Clear note that recommendations are informational and require insurer
confirmation.

Never invent savings, ratings, claim success rates or trust statistics.

### 6.3 Chat

-   Readable chat bubbles and message composer.
-   Useful starter prompts: "Explain an exclusion in my policy",
    "Compare health and term insurance", "What information is missing to
    recommend cover?"
-   Answer format: direct answer; evidence-supported explanation;
    unknowns/caveats; citations; one or two next actions.
-   Policy answers distinguish "From your policy record" from "From
    policy wording".
-   Each citation shows title, insurer/product, version/effective date
    and page/section when available.
-   Citations open a source detail view. They must refer to retrieved
    source IDs, never model-invented URLs.
-   Stage-based progress: "Checking access", "Searching policy sources",
    "Verifying citations".
-   Do not expose internal chain-of-thought.
-   Prevent duplicate submissions. Keep request ID accessible in
    details/debug panel.
-   For slow requests, show useful progress and a safe alternative
    instead of a frozen page.

### 6.4 My Policies

Cards show insurer, product, status, start/end dates and "View details".
Detail screen contains structured policy facts, source-backed coverage
summary, applicable wording, "Ask about this policy", and
insurer-confirmation guidance for ambiguity. Do not let current
marketing pages overwrite the contractual terms for an existing policy.

### 6.5 Find Cover wizard

Use a short multi-step wizard with progress, back navigation, editable
answers, and a review screen before recommendation generation.

**Step 1 --- Choose input source** - "Answer a few questions" --- always
available. - "Enter behavior signals manually". - "Upload transaction
CSV" --- optional. - "Use a synthetic demo profile". Explain that
transactions are optional and cannot prove personal circumstances.

**Step 2 --- Review signals** Show editable signal tiles with value,
source, date range, confidence/strength and actions to edit, ignore or
remove. Example: travel-related spend observed; vehicle-related activity
observed; existing policy record found. Avoid presenting a speculative
inference as fact. For every signal, show its origin: manual entry, CSV,
demo profile, structured policy record or user-confirmed answer.

**Step 3 --- Needs and fit questions** Ask only what changes eligibility
or fit. Examples: - What are you trying to protect? Health costs, family
income, vehicle, travel, home/property, other. - Do you already have
this type of cover? Yes / no / unsure. - What matters most? Coverage,
affordability, a particular benefit, simplicity. - Ask product-specific
eligibility questions only when required, explaining why. Avoid
collecting sensitive information without a concrete need. Use synthetic
values only in the prototype.

**Step 4 --- Review** Summarize confirmed needs, signals used, existing
cover and unknowns. Provide "Edit answers" and "Ignore transaction
signals". Require explicit confirmation.

**Step 5 --- Results** Show at most three initial candidates after hard
gates. Each card includes why it may fit, coverage highlights,
exclusions/limitations, overlap with existing cover, source freshness
and price status.

### 6.6 Recommendation cards

Each card includes: - Product name, insurer and category. -
Plain-language fit label, not a misleading probability. - Two or three
evidence-backed reasons. - Coverage highlights and important
exclusions/limits. - Existing-cover comparison or "Not enough
information to compare". - Verified price only when supported; otherwise
"Price requires an insurer quote" or "Price not verified". - Source
version/effective date. - Actions: Compare, View details, Helpful / Not
helpful, Continue to partner. - "May fit based on the information you
confirmed" rather than "best", "guaranteed", or "you need this".

Unknown eligibility is not equivalent to passing eligibility. Failed
hard gates exclude a product.

### 6.7 Product details and buying/hand-off journey

The UI should make the journey clear without pretending to sell
insurance:

1.  User selects **View details**.
2.  Detail screen shows source-backed benefits, exclusions, eligibility,
    required information, price status and source date.
3.  User selects **Continue to partner** or **Request a quote**.
4.  Confirmation screen explains: "This demo does not issue policies or
    take payment. In a live deployment, this step would open the
    approved insurer/bank-partner channel."
5.  Demo may log `demo_handoff_requested` and show a synthetic reference
    number.
6.  Never ask for card details, bank credentials, OTPs, signatures or
    real identity documents.
7.  Never show "Policy purchased", "Payment successful" or "Coverage
    active".

### 6.8 Employee workspace

Search by synthetic customer ID/name; choose purpose; explicitly start
assistance session. Show persistent banner with employee, customer,
purpose and session state. End session clears target context. Backend
validates every access.

### 6.9 Admin quality dashboard

Metric cards: - End-to-end p50/p95 latency. -
Retrieval/model/output-validation latency. - Citation validity. -
Evaluation pass rate. - Safe fallback rate. - Authorization denials. -
Recommendation hard-gate violations (target zero). - Current
provider/mock status.

Visuals: - Latency by workflow/stage. - Fallback reasons. - Evaluation
results by category. - Stale/missing sources. - Recent audit events with
minimal fields.

### 6.10 States for every screen

Provide meaningful empty, loading, validation error, safe fallback,
offline/mock and success states. Retry must not create duplicate
recommendation or audit records. Status text must accompany colors.

## 7. Behavior data input: UI, CSV and prefilled data

Support all three; CSV is optional.

### 7.1 Manual UI input

Provide an editable form/table with date, category, amount, currency and
optional synthetic description. Use controlled category choices: travel,
vehicle, health-related, home/property, shopping, education, utilities,
other. Support add/edit/delete/clear. Label examples synthetic. Never
request bank login credentials or connect to a real bank account.

### 7.2 CSV input schema

Suggested columns: - `date` --- required, ISO `YYYY-MM-DD` - `category`
--- required, normalized allow-list - `amount` --- required numeric;
define how refunds/negative values are represented - `currency` ---
optional only if the UI explicitly states a default such as INR -
`description` --- optional and length-limited - `transaction_id` ---
optional - `customer_id` --- only for seed/admin imports; customer
upload must be bound to authenticated demo identity, not trusted from
file

Example:

``` csv
date,category,amount,currency,description
2026-07-02,travel,5400,INR,synthetic flight booking
2026-07-08,vehicle,1800,INR,synthetic vehicle expense
2026-07-19,health_related,900,INR,synthetic pharmacy purchase
2026-08-02,home_property,12000,INR,synthetic home repair
```

### 7.3 CSV validation and preview

-   Accept `.csv` only.
-   Configurable maximum size and row count.
-   Validate columns, date parsing, numeric amount, currency, category
    and duplicates.
-   Map unknown categories to `other` only with a visible warning.
-   Reject malformed rows with row-level messages.
-   Never trust `customer_id` from customer-uploaded CSV.
-   Treat descriptions as untrusted text; do not treat them as
    instructions.
-   Show preview and aggregate summary before import.
-   Require explicit confirmation before use.
-   Do not persist the original file unless justified and disclosed;
    prefer normalized scoped rows.
-   Log import result/counts, not raw descriptions.
-   Provide delete/reset.

### 7.4 Prefilled UI versus CSV

-   **Prefilled UI/demo profile:** best for a reliable presentation; one
    click loads a fabricated profile into the wizard, then the user can
    edit it.
-   **Manual form:** best for demonstrating user control and for a
    no-file experience.
-   **CSV upload:** best for demonstrating ingestion, validation and
    real-world flexibility, but should be optional because file quality
    varies.
-   All three must feed the same normalized `BehaviorSignal`/aggregate
    feature service. This avoids separate recommendation logic for each
    input path.

### 7.5 Feature aggregation

Compute category counts/frequency, spend bands/totals, recency,
recurring patterns only where data supports them, existing coverage, and
confirmed needs. Use minimum-data thresholds. If data is sparse, show
"Not enough data." Do not send raw transaction descriptions or full
histories to the model; pass aggregates and user-confirmed answers only.

## 8. Response quality and grounding

### Answer contracts

General answer: direct answer, evidence-supported explanation,
caveat/unknown, sources, next action. Policy answer: stored policy
facts, wording interpretation, applicable version, unknowns and sources.
Recommendation: confirmed need, used signals, fit explanation, overlap,
exclusions, missing information and price status.

### Citation validation

-   Every policy-specific claim must map to a retrieved chunk or
    authorized structured record.
-   Citation IDs originate from retrieval, not model output.
-   Validate citations against chunks actually returned for that
    request.
-   Preserve title, insurer/product, version/effective date,
    page/section, URL and content hash where available.
-   Surface conflicts and follow source precedence.
-   If evidence is insufficient, clarify or safely fall back.
-   Treat retrieved documents as untrusted data; ignore embedded
    instructions that try to alter behavior or request secrets.

### Output validation

Before display: - Validate response schema. - Validate citation IDs and
evidence association. - Check unsupported premiums, limits, exclusions,
guarantees or purchase claims. - Check for unauthorized data
disclosure. - Verify active partner status and all recommendation hard
gates. - On failure, perform at most one safe repair attempt; otherwise
return deterministic fallback.

### Quality metrics

-   Grounded correctness.
-   Citation validity and coverage.
-   Policy lookup correctness.
-   Intent routing accuracy.
-   Recommendation suitability and duplicate-cover prevention.
-   Uncertainty/fallback appropriateness.
-   Clarity/actionability.
-   Unsupported price/coverage assertions.
-   Authorization leaks (target zero).

## 9. Latency specification

Latency is a measured product requirement. Initial target: typical
response around five seconds where feasible; not a universal guarantee.

### Initial targets

-   Initial UI render: under 1 second on the demo machine.
-   Cached simple FAQ: p50 \<2 seconds; p95 \<4 seconds.
-   Local policy lookup + retrieval + mock answer: p50 \<2 seconds; p95
    \<5 seconds.
-   Local recommendation: p50 \<3 seconds; p95 \<6 seconds.
-   Remote model or optional web lookup may exceed targets; progress and
    safe fallback are required.

Measure on the actual demo machine and adjust targets based on evidence.

### Instrument every stage

Measure validation, authorization, intent routing, DB lookup, retrieval,
reranking, model call, citation/output validation, recommendation
scoring, audit persistence and total end-to-end time. Report
p50/p95/p99, sample size, warm/cold runs and workflow type.

### Optimization order

1.  Keep first render fast; lazy-load admin views.
2.  Index customer/policy/product/category/date columns.
3.  Pre-ingest documents and precompute chunks/indexes; never parse
    every PDF per request.
4.  Cache immutable retrieval/embedding/product data with version-aware
    keys.
5.  Bound `top_k`; rerank only a small set.
6.  Use deterministic routing for obvious/simple intents; use a model
    only where it adds value.
7.  Send compact evidence and aggregated features, not full transaction
    histories.
8.  Set timeouts and at most one retry.
9.  Keep audit writes small and avoid blocking on nonessential dashboard
    aggregates.
10. Keep mock mode reliable and offline; remote endpoint optional.
11. Use optional official-source web lookup only when local evidence is
    insufficient and policy allows it.
12. Show real stage progress; do not fake progress or hide a long wait.

### Cache correctness

Authorization must run before returning cached sensitive results. Keys
must include user scope, normalized query, relevant document/product
versions and access context. Never reuse customer-specific results
across users. Invalidate on source/catalog updates. Preserve source
metadata with cached answers.

### Failure behavior

-   Auth/DB failure: fail closed.
-   Retrieval timeout: safe fallback or verified local index.
-   Model timeout: deterministic fallback for supported questions;
    otherwise explain inability to verify.
-   Web timeout: use local evidence and state freshness limitation.
-   Never turn timeout into certainty.

## 10. Technical architecture

Use a modular monolith: Streamlit UI, Python services, LangGraph
orchestration, SQLite and local retrieval. Avoid
React/FastAPI/microservices for the first prototype unless a real
requirement emerges.

Layers: 1. Streamlit pages/components. 2. Application services. 3.
Authentication/authorization. 4. LangGraph workflows. 5. Domain logic
and recommendation guardrails. 6. SQLite repositories. 7.
Curated-document retrieval. 8. Model adapter. 9. Audit, metrics and
evaluation.

### Repository layout

``` text
insurance_assistant/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── config/settings.py
├── data/seed_demo_data.py
├── data/documents/
├── src/auth/{demo_auth.py,authorization.py}
├── src/db/{database.py,models.py,repositories.py}
├── src/rag/{ingest.py,chunking.py,keyword_search.py,semantic_search.py,retrieval.py}
├── src/llm/{base.py,mock_adapter.py,endpoint_adapter.py}
├── src/recommendations/{features.py,scoring.py,guardrails.py}
├── src/graph/{state.py,nodes.py,workflow.py}
├── src/services/{chat_service.py,policy_service.py,product_service.py,import_service.py,audit_service.py}
├── src/evaluation/{cases.json,run_tests.py}
└── tests/{test_authorization.py,test_retrieval.py,test_recommendations.py,test_imports.py,test_workflows.py}
```

For a short prototype, create only the files needed for the first
vertical slice, then expand.

### LangGraph workflow

`validate_request → authenticate_context → authorize_request → classify_intent → route`

Routes: - General Q&A: retrieve → answer from evidence → validate
citations/output. - Policy: ownership check → structured record →
applicable wording retrieval → answer → validate. - Recommendation:
aggregate signals → ask missing questions → candidate generation → hard
gates → rank → explain → validate. - CSV: parse/validate → preview →
user confirmation → persist scoped normalized rows → audit. - Hand-off:
verify active partner product → show details → explicit mock hand-off
confirmation → audit. - Ambiguous/unsupported: clarify or safe fallback.

Every successful or denied request creates an application-constructed
audit event. LLM never authorizes or overrides guardrails.

### Model adapter

Provide `classify_intent`, `answer_from_evidence`, and optional
`propose_candidates`. The default `MockModelAdapter` supports offline
demos/tests. Add an endpoint adapter only when an approved URL, model,
credentials, network path and data-handling permission are confirmed. A
coding assistant is not assumed to be the runtime model.

### Retrieval

Ingest curated official insurer/product pages and policy PDFs with
source/version/page metadata. Use SQLite FTS5/BM25 keyword retrieval
plus optional local embeddings/vector search. If embeddings are
unavailable, label the implementation keyword-only; do not claim hybrid
search. Structured records govern ownership/status; applicable wording
governs existing contractual terms; current official sources support
current product facts.

## 11. Data model

Minimum tables: - `users(user_id, role, customer_id, password_hash, active)` -
`customers(customer_id, display_name, synthetic_attributes_json)` -
`transactions(transaction_id, customer_id, date, category, amount, currency, source, imported_at)` -
`insurance_products(product_id, insurer, name, category, active, eligibility_json, benefits_json, exclusions_json, pricing_basis, source_status)` -
`customer_policies(policy_id, customer_id, product_id, status, start_date, end_date, coverage_json, premium_amount, premium_status)` -
`documents(document_id, product_id, title, source_url, source_type, version, effective_date, retrieved_at, content_hash)` -
`document_chunks(chunk_id, document_id, section_title, page_number, chunk_text, metadata_json)` -
`recommendations(recommendation_id, customer_id, product_id, score_internal, status, reasons_json, assumptions_json, created_at)` -
`feedback(feedback_id, recommendation_id, customer_id, rating, comment_optional, created_at)` -
`assistance_sessions(session_id, employee_id, customer_id, purpose, authorization_status, started_at, ended_at)` -
`audit_events(event_id, request_id, timestamp_utc, actor_id, actor_role, action, intent, target_type, target_id, authorization_outcome, outcome, source_ids_json, model_metadata_json, latency_ms, error_code, metadata_json)`

All records must be fabricated. No real customer/account data.

## 12. Security and privacy

-   Server-controlled identity; never trust role/customer ID in prompt
    or user-editable request fields.
-   Customer access limited to own records.
-   Employee access requires active scoped assistance session and
    purpose.
-   Authorize each sensitive service call and before cache hits.
-   UI hiding is not security.
-   Neutral denial messages avoid revealing another customer's record
    existence.
-   Explicitly scope admin permissions.
-   Do not log credentials, tokens, raw transaction histories or
    unnecessary free text.
-   CSV and retrieved documents are untrusted input.
-   Demo authentication is not production auth; production requires
    approved SSO/MFA and security review.

## 13. Recommendation algorithm

Hard gates: - Active approved partner product. - Eligibility
requirements confirmed and passed. - Adequate evidence for important
benefits/terms. - Existing coverage reviewed enough to avoid obvious
duplication. - No unresolved material source conflict. - Price shown as
verified only when authoritative quote/pricing data exists.

Only products passing gates may be ranked.

Initial weights (hypothesis, requires evaluation): - Confirmed need:
35% - Behavior relevance: 20% - Coverage gap: 20% - Eligibility fit:
15% - Verified information/availability: 10%

`score = Σ(weight_i × normalized_feature_i)`

A score never compensates for a failed/unknown hard gate. Do not present
internal score as a calibrated probability. Feedback is recorded for
review and does not auto-tune weights in the prototype.

## 14. Audit and observability

Capture request/event ID, UTC time, actor/role, action/intent, permitted
target identifiers, authorization outcome, source IDs, normalized
recommendation features/reasons/guardrail outcomes,
model/provider/version, stage and total latency, outcome, fallback
reason and error code. Minimize raw content. Application code builds
audit records; the LLM does not.

## 15. Evaluation suite and acceptance gates

Create 30--40 deterministic cases covering: - Grounded general Q&A and
unsupported questions. - Correct policy clause/version. - Customer A
attempting to access B's policy. - Employee access without/with active
authorized session. - Inactive/non-partner product. - Unknown
eligibility. - Existing-cover overlap. - Sparse or misleading behavior
signals. - CSV malformed rows, duplicates, unknown categories and
identity mismatch. - Unverified price. - Invalid citation. -
Model/retrieval timeout. - Audit event on denial. - Hand-off never
claims purchase.

Metrics: grounded correctness, citation validity/coverage, retrieval
recall@k, policy correctness, routing accuracy, recommendation
precision@k/expert review, guardrail violations, authorization
violations, fallback correctness, CSV validation correctness, and
p50/p95/p99 latency by stage/workflow.

Release gates: - All authorization tests pass. - No cross-customer
leakage. - Policy answers cite valid sources or explicitly fall back. -
No unsupported price/coverage assertions in test suite. - No ineligible
product is recommended. - Mock hand-off never claims purchase or active
cover. - Seed data recreates deterministically. - Core app works offline
in mock mode. - Latency measured and documented. - README documents
limitations.

## 16. Build in parallel: frontend and backend testable together

**Key rule:** define API/service contracts and synthetic fixtures first.
The frontend must not wait for the real retrieval/model layer; backend
and frontend can be developed against the same mock service contracts.

### Contract-first interfaces

Define typed request/response models (Pydantic or dataclasses) for: -
`ChatRequest` → `ChatResponse` - `PolicySummary` / `PolicyDetail` -
`BehaviorImportPreview` → `BehaviorImportResult` - `NeedsAssessment` →
`RecommendationResponse` - `ProductDetail` → `DemoHandoffResponse` -
`FeedbackRequest` → `FeedbackResult` - `AuditSummary` / `LatencySummary`

A response should include a `request_id`, status, user-facing message,
source citations when relevant, structured warnings, and `latency_ms`.
Never accept `actor_role` as trusted authorization input.

### Parallel development lanes

**Lane A --- UI** - Build Streamlit navigation, layout, chat, policy
cards, recommendation wizard, CSV preview, product detail/hand-off and
admin quality page. - Initially call a `FakeInsuranceService` that
returns fixed synthetic responses with the same schemas as production
services. - Include loading, empty, error and fallback states from the
start. - UI tests check that user actions call the expected service and
render response fields.

**Lane B --- backend/domain** - Build repositories, authorization,
policy service, CSV validator, retrieval, recommendation gates/scoring,
audit and latency instrumentation. - Use unit tests and deterministic
fixtures. - Implement the same service interfaces that the UI fake
implements. - No dependency on Streamlit in domain modules.

**Lane C --- integration/evaluation** - Wire UI to the real service
facade. - Run contract tests against both fake and real
implementations. - Run end-to-end tests on seeded data. - Benchmark
stage latency and inspect quality failures.

### Incremental milestones and frontend/backend test matrix

  ---------------------------------------------------------------------------------------------------
  Milestone         Frontend implementation             Backend            Test both immediately
                                                        implementation     
  ----------------- ----------------------------------- ------------------ --------------------------
  0\. Contracts +   Shared schemas, fake service,       Request/response   Schema/contract tests;
  fixtures          seeded UI states                    schemas, synthetic render success/error
                                                        seed data          examples

  1\. App shell +   Navigation, role switch for demo,   Demo identity,     Customer/employee/admin
  identity          environment banner                  role policy, audit navigation; backend denies
                                                        base               forbidden service calls

  2\. Policy slice  Policy list/detail, "Ask about      Ownership checks,  Customer A sees own
                    policy", citation panel             structured lookup, policy; cross-customer
                                                        retrieval,         request denied and audited
                                                        grounded answer,   
                                                        audit              

  3\. Chat quality  Chat bubbles, starter prompts,      Intent route,      Test grounded answer,
                    citations, progress/fallback        retrieval,         invalid citation,
                                                        adapter,           insufficient evidence,
                                                        citation/output    timeout
                                                        validator          

  4\. Manual        Wizard, editable signals, needs     Feature            Confirmed need changes
  recommendation    questions, review screen            aggregation, hard  results; unknown
                                                        gates, ranking,    eligibility is excluded
                                                        explanation        

  5\. CSV import    Upload, row errors, preview,        Parser, schema     Valid/invalid/mismatched
                    aggregate summary, confirm/delete   validation,        CSV cases; UI shows
                                                        identity binding,  row-specific errors
                                                        duplicate          
                                                        detection          

  6\. Product       Comparison, details, price status,  Active catalog     Inactive product blocked;
  detail/handoff    mock continue flow                  check, hand-off    no path marks policy
                                                        event, audit       purchased

  7\. Employee      Customer search, purpose modal,     Scoped assistance  Unauthorized access
  workspace         persistent session banner           sessions and       denied; end session
                                                        per-call           revokes access
                                                        authorization      

  8\. Quality       Latency cards, citations,           Stage timers,      Synthetic test run updates
  dashboard         fallback/eval charts                metrics            metrics; p50/p95
                                                        aggregation, eval  calculated correctly
                                                        runner             

  9\. Hardening     Empty/error/loading/accessibility   Timeout handling,  Full regression suite and
                    polish                              cache scopes,      repeated latency runs
                                                        logging, reset     
                                                        scripts            
  ---------------------------------------------------------------------------------------------------

### Suggested test pyramid

1.  **Unit tests** for CSV parsing, authorization, ranking, citations,
    aggregation and output validation.
2.  **Contract tests** for service request/response shapes.
3.  **Component/UI tests** for form validation, wizard navigation, state
    transitions and display of citations/errors.
4.  **Integration tests** for real service facade + SQLite + retrieval +
    mock adapter.
5.  **End-to-end tests** for full customer, employee and admin journeys.
6.  **Evaluation tests** for answer quality and recommendation
    suitability.
7.  **Performance tests** with repeated runs to report percentiles, not
    a single timing.

### Definition of done per feature

A feature is not done when its screen exists. It is done when: - UI
state and validation work. - Service contract is implemented. -
Authorization and data validation are enforced server-side. - Unit and
contract tests pass. - At least one end-to-end case passes. - Latency
and failure behavior are measured. - Audit behavior is verified. -
Error, empty and fallback states are present.

## 17. Suggested implementation sequence

1.  **First vertical slice:** synthetic customer asks about an existing
    policy → ownership checked → LangGraph route → structured record +
    wording retrieval → mock adapter answer → citation validation →
    audit → Streamlit displays result.
2.  Add chat starter prompts, citation/source detail and latency
    display.
3.  Add manual needs questionnaire and deterministic recommendation
    cards.
4.  Add prefilled demo profile, then CSV upload/preview/confirmation.
5.  Add product detail and mock partner hand-off.
6.  Add employee assistance session and admin quality dashboard.
7.  Add optional semantic embeddings or approved endpoint only after the
    offline path is solid.
8.  Run the full evaluation and rehearse the demo.

Manual UI entry should be implemented before CSV because it makes the
recommendation flow testable without files. A prefilled synthetic
profile is ideal for a repeatable demo. CSV is an additional input path,
not a prerequisite.

## 18. Five-hour fallback plan

If a short deadline returns: - 45 min: app shell, schemas, synthetic
seed data and SQLite. - 45 min: demo identity, roles, ownership
checks. - 60 min: policy retrieval, citations and fallback. - 60 min:
LangGraph routing, manual needs form and deterministic recommendation
gates. - 45 min: behavior UI/CSV basic validation and audit. - 45 min:
critical tests, UX polish and demo rehearsal.

If time slips, defer semantic embeddings, optional live web lookup and
admin charts before removing authorization, citations or recommendation
hard gates.

## 19. Development tooling --- no Copilot restriction

The specification does not depend on Microsoft Copilot or any particular
coding assistant. Use an ordinary Python IDE/editor, virtual
environment, Git, tests and debugger. Coding assistants are optional
productivity tools, not runtime dependencies. The actual environment may
impose its own package/network/security restrictions; inspect those
rather than assuming either access or restriction. Follow organizational
rules for source code and data transfer; do not move company code to a
personal machine if policy disallows it.

First inspect: - Python version. - Whether dependencies can be
installed. - Whether Streamlit, LangGraph, SQLite and PDF parsing are
available. - Whether outbound network access is allowed. - Whether an
approved model endpoint is configured. - Whether local embeddings are
feasible. - Whether Git and test execution are available.

If packages or network are restricted, retain the deterministic mock
adapter and local SQLite/keyword search, and label reduced capabilities
honestly.

## 20. Example configuration

``` env
APP_MODE=demo
DATABASE_URL=sqlite:///./insurance_demo.db
LLM_PROVIDER=mock
LLM_ENDPOINT=
LLM_MODEL=
LLM_API_KEY=
ADMIN_API_KEY=secret_admin_key_2026
ADMIN_PASSWORD=AdminSecurePass@2026
WEB_LOOKUP_ENABLED=false
SEMANTIC_SEARCH_ENABLED=false
MAX_CSV_ROWS=5000
MAX_UPLOAD_MB=5
```

These are configuration examples, not credentials. Never commit secrets;
use environment variables or an approved secret store.

## 21. Demo script

1.  Sign in as synthetic customer A.
2.  Ask a general question and open a citation.
3.  Open My Policies and ask a policy-specific question.
4.  Switch to customer B and verify customer A's policy is inaccessible.
5.  Open Find Cover and complete manual needs questions.
6.  Load a synthetic prefilled profile, edit one signal, and compare
    results.
7.  Upload a synthetic CSV, preview it, correct a category and confirm
    import.
8.  Show how existing coverage affects recommendations.
9.  Open product details and use mock partner hand-off; verify no
    purchase is claimed.
10. Start and end an employee assistance session.
11. Show p50/p95 latency, citation validity, fallbacks and test results
    on the quality dashboard.
12. Explain limitations: synthetic data, mock model by default, no live
    quote/purchase, prototype security only.

## 22. Out of scope

-   Real banking/customer data or live bank-account connections.
-   Real policy purchase, issuance, payment, renewal or claims.
-   Live premium calculation without an approved insurer quote
    integration.
-   Unreviewed autonomous browsing for contractual facts.
-   Automatic learning from feedback.
-   Production security, legal or regulatory compliance claims.

## 23. Final readiness checklist

-   [ ] Local app launches and shows synthetic-demo status.
-   [ ] Seed data is reproducible.
-   [ ] Roles and ownership checks work; denied access is audited.
-   [ ] Employee assistance is purpose-bound and revocable.
-   [ ] Policy answers use applicable wording and valid citations.
-   [ ] Manual input works without a CSV.
-   [ ] Prefilled synthetic demo profile works and is editable.
-   [ ] CSV validation, preview, confirmation, mismatch handling and
    reset work.
-   [ ] Behavior signals are editable and not treated as proof of
    personal facts.
-   [ ] Only active partner products passing hard gates are recommended.
-   [ ] Existing coverage/overlap is considered.
-   [ ] No fabricated premiums or unsupported benefits.
-   [ ] Product hand-off never claims purchase/active coverage.
-   [ ] Audit and stage latency are captured.
-   [ ] Unit, contract, integration, UI and evaluation tests pass.
-   [ ] p50/p95 measurements and sample sizes are documented.
-   [ ] Core demo works offline in mock mode.
-   [ ] README contains setup, reset, limitations and demo steps.

**Recommended first move:** implement the shared contracts and fake
service, then build the policy-answer vertical slice end-to-end. This
allows frontend and backend work to proceed in parallel while every
milestone remains testable.
