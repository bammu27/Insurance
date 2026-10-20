"""Shared typed contracts and response envelopes.

All request and response models enforce extra="forbid" to reject unexpected
or untrusted fields (such as actor_role or customer_id).
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class Citation(BaseModel):
    """Citation mapping claims directly to retrieved sources."""

    model_config = ConfigDict(extra="forbid")

    citation_id: str
    title: str
    insurer: Optional[str] = None
    product: Optional[str] = None
    version: Optional[str] = None
    effective_date: Optional[str] = None
    page_or_section: Optional[str] = None
    url: Optional[str] = None
    content_hash: Optional[str] = None


class BaseResponse(BaseModel):
    """Standard response envelope applied to every backend response."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    status: Literal["ok", "denied", "fallback", "error"]
    message: str
    citations: List[Citation] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    latency_ms: float = 0.0


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    """Chat query sent by a user.
    
    extra="forbid" rejects any attempt to pass actor_role or customer_id in payload.
    """

    model_config = ConfigDict(extra="forbid")

    text: str = Field(..., min_length=1, description="Non-empty user query")
    session_id: Optional[str] = Field(None, description="Optional conversation session ID")


class ChatResponse(BaseResponse):
    """Chat answer with grounding evidence and next steps."""

    model_config = ConfigDict(extra="forbid")

    direct_answer: Optional[str] = None
    record_facts: Optional[str] = None
    wording_interpretation: Optional[str] = None
    caveats: Optional[str] = None
    suggested_actions: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Policies
# ---------------------------------------------------------------------------


class PolicySummary(BaseModel):
    """High-level summary of a customer policy."""

    model_config = ConfigDict(extra="forbid")

    policy_id: str
    customer_id: str
    insurer: str
    product_name: str
    category: str
    status: Literal["active", "expired", "lapsed", "cancelled"]
    start_date: str
    end_date: str
    premium_amount: float
    premium_status: str


class PolicyListResponse(BaseResponse):
    """List of policies owned by the current customer."""

    model_config = ConfigDict(extra="forbid")

    policies: List[PolicySummary] = Field(default_factory=list)


class PolicyDetail(BaseModel):
    """Full details of a specific policy."""

    model_config = ConfigDict(extra="forbid")

    policy_id: str
    customer_id: str
    insurer: str
    product_id: str
    product_name: str
    category: str
    status: str
    start_date: str
    end_date: str
    coverage_summary: str
    coverage_details: Dict[str, Any] = Field(default_factory=dict)
    applicable_wording: Optional[str] = None
    premium_amount: float
    premium_status: str


class PolicyDetailResponse(BaseResponse):
    """Response envelope containing detailed policy facts."""

    model_config = ConfigDict(extra="forbid")

    policy: Optional[PolicyDetail] = None


# ---------------------------------------------------------------------------
# Behavior Import (CSV / Manual)
# ---------------------------------------------------------------------------


class BehaviorImportPreview(BaseModel):
    """Preview of parsed behavior signals before user confirmation."""

    model_config = ConfigDict(extra="forbid")

    total_rows: int
    valid_rows: int
    error_rows: int
    categories_found: List[str] = Field(default_factory=list)
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    total_amount: float = 0.0
    preview_rows: List[Dict[str, Any]] = Field(default_factory=list)
    row_errors: List[Dict[str, Any]] = Field(default_factory=list)


class BehaviorImportPreviewResponse(BaseResponse):
    """Envelope wrapping behavior import preview."""

    model_config = ConfigDict(extra="forbid")

    preview: Optional[BehaviorImportPreview] = None


class BehaviorImportResult(BaseResponse):
    """Result of confirmed behavior signals import."""

    model_config = ConfigDict(extra="forbid")

    imported_rows: int = 0
    skipped_rows: int = 0
    customer_id: str = ""


# ---------------------------------------------------------------------------
# Needs Assessment & Recommendations
# ---------------------------------------------------------------------------


class NeedsAssessment(BaseModel):
    """User questionnaire answers regarding insurance needs."""

    model_config = ConfigDict(extra="forbid")

    protection_goal: str = Field(..., description="e.g. Health, Family Income, Vehicle, Travel, Home")
    already_covered: Literal["yes", "no", "unsure"]
    priority: str = Field(..., description="Coverage, Affordability, Specific Benefit, Simplicity")
    budget_band: Optional[str] = None
    dependents_count: Optional[int] = 0
    health_conditions: List[str] = Field(default_factory=list)


class RecommendationItem(BaseModel):
    """A recommended insurance product passing all hard gates."""

    model_config = ConfigDict(extra="forbid")

    product_id: str
    product_name: str
    insurer: str
    category: str
    fit_label: str
    reasons: List[str] = Field(default_factory=list)
    coverage_highlights: List[str] = Field(default_factory=list)
    limitations_or_exclusions: List[str] = Field(default_factory=list)
    existing_cover_overlap: str
    source_freshness: str
    price_status: str
    score_internal: Optional[float] = None
    citations: List[Citation] = Field(default_factory=list)


class RecommendationResponse(BaseResponse):
    """Response envelope for product recommendations."""

    model_config = ConfigDict(extra="forbid")

    recommendations: List[RecommendationItem] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Product Details & Demo Hand-off
# ---------------------------------------------------------------------------


class ProductDetail(BaseModel):
    """Catalog product details with authoritative facts."""

    model_config = ConfigDict(extra="forbid")

    product_id: str
    insurer: str
    name: str
    category: str
    active: bool
    benefits: List[str] = Field(default_factory=list)
    exclusions: List[str] = Field(default_factory=list)
    eligibility_criteria: Dict[str, Any] = Field(default_factory=dict)
    pricing_basis: str
    price_status: str
    source_status: str
    source_version: Optional[str] = None
    source_effective_date: Optional[str] = None


class ProductDetailResponse(BaseResponse):
    """Envelope containing product details."""

    model_config = ConfigDict(extra="forbid")

    product: Optional[ProductDetail] = None


class DemoHandoffRequest(BaseModel):
    """Request to initiate a mock hand-off."""

    model_config = ConfigDict(extra="forbid")

    product_id: str


class DemoHandoffResponse(BaseResponse):
    """Mock hand-off acknowledgement."""

    model_config = ConfigDict(extra="forbid")

    product_id: str
    handoff_reference: str
    disclaimer: str
    partner_channel_url: Optional[str] = None


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------


class FeedbackRequest(BaseModel):
    """User feedback for an answer or recommendation."""

    model_config = ConfigDict(extra="forbid")

    recommendation_id: Optional[str] = None
    rating: int = Field(..., ge=1, le=5, description="1 to 5 rating scale")
    comment: Optional[str] = None


class FeedbackResult(BaseResponse):
    """Outcome of submitting user feedback."""

    model_config = ConfigDict(extra="forbid")

    feedback_id: str = ""
    recorded: bool = False


# ---------------------------------------------------------------------------
# Audit & Latency Summaries
# ---------------------------------------------------------------------------


class LatencySummary(BaseModel):
    """Percentile summary of request latencies."""

    model_config = ConfigDict(extra="forbid")

    p50_ms: float
    p95_ms: float
    p99_ms: float
    sample_size: int
    stage_breakdowns: Dict[str, float] = Field(default_factory=dict)


class AuditSummary(BaseModel):
    """High-level metrics for quality monitoring."""

    model_config = ConfigDict(extra="forbid")

    total_events: int
    auth_denials: int
    fallbacks: int
    errors: int
    recent_events: List[Dict[str, Any]] = Field(default_factory=list)


class AuditResponse(BaseResponse):
    """Envelope with audit events and latency metrics."""

    model_config = ConfigDict(extra="forbid")

    audit_summary: Optional[AuditSummary] = None
    latency_summary: Optional[LatencySummary] = None
