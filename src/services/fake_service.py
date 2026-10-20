"""FakeInsuranceService implementation returning fixed synthetic answers.

Implements InsuranceService interface to enable frontend and testing
without requiring external models or live services.
Supports the MOCK_FAULT fault injection switches defined in the specification.
"""

import time
import uuid
from typing import Optional

from config.settings import MOCK_FAULT
from src.contracts.models import (
    AuditResponse,
    AuditSummary,
    BehaviorImportPreview,
    BehaviorImportPreviewResponse,
    BehaviorImportResult,
    ChatRequest,
    ChatResponse,
    Citation,
    DemoHandoffRequest,
    DemoHandoffResponse,
    FeedbackRequest,
    FeedbackResult,
    LatencySummary,
    NeedsAssessment,
    PolicyDetail,
    PolicyDetailResponse,
    PolicyListResponse,
    PolicySummary,
    ProductDetail,
    ProductDetailResponse,
    RecommendationItem,
    RecommendationResponse,
)
from src.services.interface import InsuranceService


class FakeInsuranceService(InsuranceService):
    """Synthetic service facade returning deterministic test responses."""

    def __init__(self, mock_fault: Optional[str] = None):
        self.mock_fault = mock_fault or MOCK_FAULT

    def _generate_request_id(self) -> str:
        return f"req-{uuid.uuid4().hex[:8]}"

    def chat(self, actor_user_id: str, request: ChatRequest) -> ChatResponse:
        start_time = time.perf_counter()
        req_id = self._generate_request_id()

        # Handle Mock Faults
        if self.mock_fault == "timeout":
            return ChatResponse(
                request_id=req_id,
                status="error",
                message="Service timeout: retrieval stage exceeded maximum threshold of 5000ms.",
                citations=[],
                warnings=["Operation timed out"],
                latency_ms=5002.0,
            )

        if self.mock_fault == "bad_citation":
            return ChatResponse(
                request_id=req_id,
                status="ok",
                message="Care Shield limits room rent to 1% of the sum insured.",
                citations=[
                    Citation(
                        citation_id="INVALID_CHUNK_404",
                        title="Nonexistent Document Reference",
                    )
                ],
                warnings=["Citation validation failed: reference not found in retrieval set"],
                latency_ms=45.0,
            )

        if self.mock_fault == "unsupported_price":
            return ChatResponse(
                request_id=req_id,
                status="ok",
                message="Your health insurance premium is guaranteed at Rs. 1,499 per month with no waiting period.",
                citations=[],
                warnings=["Output validator flagged unverified price claim"],
                latency_ms=52.0,
            )

        if self.mock_fault == "purchase_claim":
            return ChatResponse(
                request_id=req_id,
                status="ok",
                message="Congratulations! Your policy is now purchased, active, and bound.",
                citations=[],
                warnings=["Output validator flagged forbidden policy purchase claim"],
                latency_ms=38.0,
            )

        # Standard Grounded Answer
        standard_citation = Citation(
            citation_id="CHUNK-HEALTH-01",
            title="Care Shield Policy Wording v2.1",
            insurer="Star Allied",
            product="Care Shield Health Insurance",
            version="v2.1",
            effective_date="2025-01-01",
            page_or_section="Section 3.2 Room Rent Limit",
            url="https://partner.bank.example/docs/care-shield-v2.1.pdf",
            content_hash="hash-care-shield-v2.1",
        )

        latency = (time.perf_counter() - start_time) * 1000.0 + 45.0
        return ChatResponse(
            request_id=req_id,
            status="ok",
            message="Care Shield Health Insurance caps daily room rent at 1% of the total Sum Insured per day. Proportionate deductions apply to associated medical charges if you choose a higher room category.",
            direct_answer="Room rent is capped at 1% of your Sum Insured per day.",
            record_facts="Policy POL-A-HEALTH has a Sum Insured of ₹5,00,000, establishing a daily room limit of ₹5,000.",
            wording_interpretation="According to Section 3.2, selecting a room above ₹5,000/day triggers proportionate deductions across nursing and doctor fees.",
            caveats="ICU charges may follow separate limits specified under Section 3.3.",
            citations=[standard_citation],
            warnings=[],
            suggested_actions=["Review Section 3.2 of your policy wording", "Request insurer hospital network list"],
            latency_ms=round(latency, 2),
        )

    def get_policies(self, actor_user_id: str) -> PolicyListResponse:
        start_time = time.perf_counter()
        req_id = self._generate_request_id()

        if actor_user_id == "cust_a":
            policies = [
                PolicySummary(
                    policy_id="POL-A-HEALTH",
                    customer_id="cust_a",
                    insurer="Star Allied",
                    product_name="Care Shield Health Insurance",
                    category="health",
                    status="active",
                    start_date="2025-06-01",
                    end_date="2026-05-31",
                    premium_amount=12500.0,
                    premium_status="paid_annual",
                ),
                PolicySummary(
                    policy_id="POL-A-TRAVEL",
                    customer_id="cust_a",
                    insurer="Bajaj Allianz Partner",
                    product_name="Global Voyage Travel Shield",
                    category="travel",
                    status="expired",
                    start_date="2024-07-01",
                    end_date="2024-07-20",
                    premium_amount=1800.0,
                    premium_status="paid_onetime",
                ),
            ]
        elif actor_user_id == "cust_b":
            policies = [
                PolicySummary(
                    policy_id="POL-B-TERM",
                    customer_id="cust_b",
                    insurer="HDFC Life Partner",
                    product_name="Pure Life Term Plan",
                    category="term",
                    status="active",
                    start_date="2023-01-01",
                    end_date="2043-01-01",
                    premium_amount=18400.0,
                    premium_status="paid_annual",
                ),
            ]
        else:
            policies = []

        latency = (time.perf_counter() - start_time) * 1000.0 + 20.0
        return PolicyListResponse(
            request_id=req_id,
            status="ok",
            message=f"Found {len(policies)} policy record(s).",
            policies=policies,
            citations=[],
            warnings=[],
            latency_ms=round(latency, 2),
        )

    def get_policy_detail(self, actor_user_id: str, policy_id: str) -> PolicyDetailResponse:
        start_time = time.perf_counter()
        req_id = self._generate_request_id()

        # Authorization check: cust_a can only view POL-A-*, cust_b can only view POL-B-*
        if policy_id.startswith("POL-A-") and actor_user_id != "cust_a":
            latency = (time.perf_counter() - start_time) * 1000.0 + 15.0
            return PolicyDetailResponse(
                request_id=req_id,
                status="denied",
                message="Access denied: you do not have permission to access the requested policy record.",
                policy=None,
                citations=[],
                warnings=["Unauthorized policy lookup attempted"],
                latency_ms=round(latency, 2),
            )

        if policy_id.startswith("POL-B-") and actor_user_id != "cust_b":
            latency = (time.perf_counter() - start_time) * 1000.0 + 15.0
            return PolicyDetailResponse(
                request_id=req_id,
                status="denied",
                message="Access denied: you do not have permission to access the requested policy record.",
                policy=None,
                citations=[],
                warnings=["Unauthorized policy lookup attempted"],
                latency_ms=round(latency, 2),
            )

        if policy_id == "POL-A-HEALTH":
            detail = PolicyDetail(
                policy_id="POL-A-HEALTH",
                customer_id="cust_a",
                insurer="Star Allied",
                product_id="PROD-HEALTH-01",
                product_name="Care Shield Health Insurance",
                category="health",
                status="active",
                start_date="2025-06-01",
                end_date="2026-05-31",
                coverage_summary="Comprehensive hospitalization cover up to ₹5,00,000 sum insured.",
                coverage_details={
                    "sum_insured": 500000.0,
                    "room_rent_limit": "1% of Sum Insured per day (₹5,000/day)",
                    "copay": "Nil",
                    "pre_existing_waiting_months": 24,
                },
                applicable_wording="Care Shield Policy Wording v2.1 (effective 2025-01-01)",
                premium_amount=12500.0,
                premium_status="paid_annual",
            )
            citation = Citation(
                citation_id="CHUNK-HEALTH-01",
                title="Care Shield Policy Wording v2.1",
                insurer="Star Allied",
                version="v2.1",
                effective_date="2025-01-01",
                page_or_section="Section 3.2",
            )
            citations = [citation]
        elif policy_id == "POL-B-TERM":
            detail = PolicyDetail(
                policy_id="POL-B-TERM",
                customer_id="cust_b",
                insurer="HDFC Life Partner",
                product_id="PROD-TERM-01",
                product_name="Pure Life Term Plan",
                category="term",
                status="active",
                start_date="2023-01-01",
                end_date="2043-01-01",
                coverage_summary="Pure risk term life cover with ₹1,00,00,000 sum assured.",
                coverage_details={
                    "sum_assured": 10000000.0,
                    "payout_structure": "Single lump sum payment to nominee",
                    "terminal_illness_included": True,
                },
                applicable_wording="Pure Life Terms and Conditions v1.4 (effective 2024-06-01)",
                premium_amount=18400.0,
                premium_status="paid_annual",
            )
            citation = Citation(
                citation_id="CHUNK-TERM-01",
                title="Pure Life Terms and Conditions v1.4",
                insurer="HDFC Life Partner",
                version="v1.4",
                effective_date="2024-06-01",
                page_or_section="Section 2.1",
            )
            citations = [citation]
        else:
            latency = (time.perf_counter() - start_time) * 1000.0 + 10.0
            return PolicyDetailResponse(
                request_id=req_id,
                status="error",
                message=f"Policy {policy_id} not found.",
                policy=None,
                citations=[],
                warnings=["Record does not exist"],
                latency_ms=round(latency, 2),
            )

        latency = (time.perf_counter() - start_time) * 1000.0 + 35.0
        return PolicyDetailResponse(
            request_id=req_id,
            status="ok",
            message="Policy details retrieved successfully.",
            policy=detail,
            citations=citations,
            warnings=[],
            latency_ms=round(latency, 2),
        )

    def preview_behavior_import(self, actor_user_id: str, raw_csv: str) -> BehaviorImportPreviewResponse:
        start_time = time.perf_counter()
        req_id = self._generate_request_id()

        # Synthetic preview result
        lines = [line.strip() for line in raw_csv.strip().splitlines() if line.strip()]
        total_rows = max(0, len(lines) - 1) if len(lines) > 0 else 0

        preview = BehaviorImportPreview(
            total_rows=total_rows or 4,
            valid_rows=total_rows or 4,
            error_rows=0,
            categories_found=["travel", "vehicle", "health_related", "home_property"],
            date_range_start="2026-07-02",
            date_range_end="2026-08-02",
            total_amount=20100.0,
            preview_rows=[
                {"date": "2026-07-02", "category": "travel", "amount": 5400.0, "currency": "INR"},
                {"date": "2026-07-08", "category": "vehicle", "amount": 1800.0, "currency": "INR"},
            ],
            row_errors=[],
        )

        latency = (time.perf_counter() - start_time) * 1000.0 + 30.0
        return BehaviorImportPreviewResponse(
            request_id=req_id,
            status="ok",
            message=f"CSV validated. {preview.valid_rows} rows ready for review.",
            preview=preview,
            citations=[],
            warnings=[],
            latency_ms=round(latency, 2),
        )

    def confirm_behavior_import(self, actor_user_id: str, raw_csv: str) -> BehaviorImportResult:
        start_time = time.perf_counter()
        req_id = self._generate_request_id()

        latency = (time.perf_counter() - start_time) * 1000.0 + 40.0
        return BehaviorImportResult(
            request_id=req_id,
            status="ok",
            message="4 synthetic behavior signals successfully confirmed and imported.",
            imported_rows=4,
            skipped_rows=0,
            customer_id=actor_user_id,
            citations=[],
            warnings=[],
            latency_ms=round(latency, 2),
        )

    def get_recommendations(self, actor_user_id: str, assessment: NeedsAssessment) -> RecommendationResponse:
        start_time = time.perf_counter()
        req_id = self._generate_request_id()

        recs = [
            RecommendationItem(
                product_id="PROD-MOTOR-01",
                product_name="DriveSecure Comprehensive Motor",
                insurer="ICICI Lombard Partner",
                category="motor",
                fit_label="Strong Fit",
                reasons=[
                    "Matches your confirmed vehicle protection goal",
                    "Observed vehicle maintenance activity in behavior clues",
                ],
                coverage_highlights=["Own damage coverage", "24/7 Roadside assistance", "Third-party liability"],
                limitations_or_exclusions=["Consequential engine damage unless add-on opted"],
                existing_cover_overlap="No overlapping active motor policy found",
                source_freshness="Verified current catalog (v1.2)",
                price_status="Price requires vehicle registration & IDV quote",
                citations=[
                    Citation(
                        citation_id="PROD-MOTOR-01-SPEC",
                        title="DriveSecure Motor Feature Brochure",
                        insurer="ICICI Lombard Partner",
                        version="v1.2",
                        effective_date="2025-03-01",
                    )
                ],
            ),
            RecommendationItem(
                product_id="PROD-HEALTH-01",
                product_name="Care Shield Health Insurance",
                insurer="Star Allied",
                category="health",
                fit_label="Moderate Fit",
                reasons=["High hospitalization limits suitable for family protection needs"],
                coverage_highlights=["₹5,00,000 inpatient hospitalization", "Day care coverage"],
                limitations_or_exclusions=["1% Room rent limit applies", "24-month waiting period for pre-existing diseases"],
                existing_cover_overlap="Overlaps with your existing active health policy POL-A-HEALTH",
                source_freshness="Verified wording v2.1",
                price_status="Price requires an insurer quote based on age band",
                citations=[
                    Citation(
                        citation_id="CHUNK-HEALTH-01",
                        title="Care Shield Policy Wording v2.1",
                        insurer="Star Allied",
                        version="v2.1",
                        effective_date="2025-01-01",
                        page_or_section="Section 3.2",
                    )
                ],
            ),
        ]

        latency = (time.perf_counter() - start_time) * 1000.0 + 85.0
        return RecommendationResponse(
            request_id=req_id,
            status="ok",
            message=f"Generated {len(recs)} suitable recommendation(s) passing all suitability hard gates.",
            recommendations=recs,
            citations=[],
            warnings=["Recommendations are informational; live quotes require insurer confirmation."],
            latency_ms=round(latency, 2),
        )

    def get_product_detail(self, actor_user_id: str, product_id: str) -> ProductDetailResponse:
        start_time = time.perf_counter()
        req_id = self._generate_request_id()

        if product_id == "PROD-HOME-OLD":
            latency = (time.perf_counter() - start_time) * 1000.0 + 10.0
            return ProductDetailResponse(
                request_id=req_id,
                status="denied",
                message="Product is inactive in partner catalog and cannot be recommended or viewed.",
                product=None,
                citations=[],
                warnings=["Product status is inactive"],
                latency_ms=round(latency, 2),
            )

        detail = ProductDetail(
            product_id=product_id,
            insurer="Star Allied",
            name="Care Shield Health Insurance",
            category="health",
            active=True,
            benefits=["Inpatient hospitalization", "Day care treatments", "Ambulance cover"],
            exclusions=["Cosmetic surgery", "Non-prescribed supplements"],
            eligibility_criteria={"min_age": 18, "max_age": 65},
            pricing_basis="Age, sum insured, and city tier",
            price_status="Price requires an insurer quote",
            source_status="active_catalog",
            source_version="v2.1",
            source_effective_date="2025-01-01",
        )

        latency = (time.perf_counter() - start_time) * 1000.0 + 25.0
        return ProductDetailResponse(
            request_id=req_id,
            status="ok",
            message="Product details retrieved.",
            product=detail,
            citations=[],
            warnings=[],
            latency_ms=round(latency, 2),
        )

    def request_demo_handoff(self, actor_user_id: str, request: DemoHandoffRequest) -> DemoHandoffResponse:
        start_time = time.perf_counter()
        req_id = self._generate_request_id()

        latency = (time.perf_counter() - start_time) * 1000.0 + 30.0
        return DemoHandoffResponse(
            request_id=req_id,
            status="ok",
            message="Mock hand-off initiated successfully.",
            product_id=request.product_id,
            handoff_reference=f"MOCK-HANDOFF-{uuid.uuid4().hex[:6].upper()}",
            disclaimer="This demo does not issue policies or take payment. In a live deployment, this step would open the approved insurer/bank-partner channel.",
            partner_channel_url="https://partner.bank.example/demo-portal",
            citations=[],
            warnings=["Prototype boundary: no payment or policy issuance performed."],
            latency_ms=round(latency, 2),
        )

    def submit_feedback(self, actor_user_id: str, request: FeedbackRequest) -> FeedbackResult:
        start_time = time.perf_counter()
        req_id = self._generate_request_id()

        latency = (time.perf_counter() - start_time) * 1000.0 + 20.0
        return FeedbackResult(
            request_id=req_id,
            status="ok",
            message="Thank you! Feedback recorded for review.",
            feedback_id=f"FB-{uuid.uuid4().hex[:6].upper()}",
            recorded=True,
            citations=[],
            warnings=[],
            latency_ms=round(latency, 2),
        )

    def get_audit_and_latency_summary(self, actor_user_id: str) -> AuditResponse:
        start_time = time.perf_counter()
        req_id = self._generate_request_id()

        audit_summary = AuditSummary(
            total_events=142,
            auth_denials=3,
            fallbacks=5,
            errors=1,
            recent_events=[
                {
                    "event_id": "EVT-001",
                    "actor_id": "cust_a",
                    "action": "policy_lookup",
                    "authorization_outcome": "authorized",
                    "outcome": "ok",
                    "latency_ms": 35.2,
                },
                {
                    "event_id": "EVT-002",
                    "actor_id": "cust_b",
                    "action": "policy_lookup",
                    "authorization_outcome": "denied",
                    "outcome": "denied",
                    "latency_ms": 15.1,
                },
            ],
        )

        latency_summary = LatencySummary(
            p50_ms=42.0,
            p95_ms=115.0,
            p99_ms=180.0,
            sample_size=150,
            stage_breakdowns={
                "validation": 2.1,
                "authorization": 3.4,
                "retrieval": 18.2,
                "scoring": 12.0,
                "output_validation": 4.5,
            },
        )

        latency = (time.perf_counter() - start_time) * 1000.0 + 25.0
        return AuditResponse(
            request_id=req_id,
            status="ok",
            message="Audit and latency metrics calculated.",
            audit_summary=audit_summary,
            latency_summary=latency_summary,
            citations=[],
            warnings=[],
            latency_ms=round(latency, 2),
        )
