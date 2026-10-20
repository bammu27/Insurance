"""Contract and schema validation tests.

Verifies acceptance criterion M0.1:
- No request has a trusted actor_role or customer_id. Sending one is rejected.
- Request payload models enforce strict schema validation.
- All response envelopes contain standard observability fields.
"""

import pytest
from pydantic import ValidationError

from src.contracts.models import (
    BaseResponse,
    ChatRequest,
    ChatResponse,
    Citation,
    DemoHandoffRequest,
    FeedbackRequest,
    NeedsAssessment,
    PolicyDetailResponse,
    PolicyListResponse,
    RecommendationResponse,
)


def test_chat_request_valid():
    """ChatRequest accepts valid input."""
    req = ChatRequest(text="What is my deductible?")
    assert req.text == "What is my deductible?"
    assert req.session_id is None


def test_chat_request_rejects_empty_text():
    """ChatRequest rejects empty string."""
    with pytest.raises(ValidationError) as exc_info:
        ChatRequest(text="")
    assert "String should have at least 1 character" in str(exc_info.value)


def test_chat_request_rejects_actor_role():
    """Criterion M0.1: Rejects client-supplied actor_role."""
    with pytest.raises(ValidationError) as exc_info:
        ChatRequest.model_validate({"text": "hello", "actor_role": "admin"})
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_chat_request_rejects_customer_id():
    """Criterion M0.1: Rejects client-supplied customer_id."""
    with pytest.raises(ValidationError) as exc_info:
        ChatRequest.model_validate({"text": "hello", "customer_id": "cust_b"})
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_needs_assessment_rejects_untrusted_fields():
    """NeedsAssessment rejects unexpected fields."""
    with pytest.raises(ValidationError) as exc_info:
        NeedsAssessment.model_validate(
            {
                "protection_goal": "health",
                "already_covered": "no",
                "priority": "coverage",
                "actor_role": "admin",
            }
        )
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_feedback_request_rating_boundary():
    """Feedback rating must be between 1 and 5."""
    req = FeedbackRequest(rating=5, comment="Excellent")
    assert req.rating == 5

    with pytest.raises(ValidationError):
        FeedbackRequest(rating=0)

    with pytest.raises(ValidationError):
        FeedbackRequest(rating=6)


def test_response_envelope_fields():
    """Every response envelope has request_id, status, message, citations, warnings, latency_ms."""
    citation = Citation(
        citation_id="CHUNK-01",
        title="Test Document",
        version="v1.0",
        effective_date="2025-01-01",
    )
    res = BaseResponse(
        request_id="req-123",
        status="ok",
        message="Operation successful",
        citations=[citation],
        warnings=[],
        latency_ms=12.5,
    )
    dumped = res.model_dump()
    assert dumped["request_id"] == "req-123"
    assert dumped["status"] == "ok"
    assert dumped["message"] == "Operation successful"
    assert len(dumped["citations"]) == 1
    assert dumped["citations"][0]["citation_id"] == "CHUNK-01"
    assert dumped["warnings"] == []
    assert dumped["latency_ms"] == 12.5
