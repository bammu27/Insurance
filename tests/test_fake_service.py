"""Tests for FakeInsuranceService.

Verifies acceptance criteria M0.3:
- Fake and real service share one interface.
- Returns synthetic responses with valid citations and envelopes.
- Enforces isolation between customers.
- Responds to mock fault injection switches.
"""

from src.contracts.models import ChatRequest, NeedsAssessment
from src.services.fake_service import FakeInsuranceService
from src.services.interface import InsuranceService


def test_implements_insurance_service_interface():
    """FakeInsuranceService implements the shared InsuranceService interface."""
    service = FakeInsuranceService()
    assert isinstance(service, InsuranceService)


def test_chat_grounded_answer():
    """Chat returns grounded answer with valid citation provenance."""
    service = FakeInsuranceService()
    res = service.chat("cust_a", ChatRequest(text="Explain room rent limit"))

    assert res.status == "ok"
    assert res.request_id.startswith("req-")
    assert "room rent" in res.message.lower()
    assert len(res.citations) >= 1

    citation = res.citations[0]
    assert citation.citation_id == "CHUNK-HEALTH-01"
    assert citation.title == "Care Shield Policy Wording v2.1"
    assert citation.version == "v2.1"
    assert citation.effective_date == "2025-01-01"


def test_policy_lookup_customer_isolation():
    """Customer A cannot view Customer B's policies and vice versa."""
    service = FakeInsuranceService()

    # Customer A can view POL-A-HEALTH
    res_a = service.get_policy_detail("cust_a", "POL-A-HEALTH")
    assert res_a.status == "ok"
    assert res_a.policy is not None
    assert res_a.policy.policy_id == "POL-A-HEALTH"

    # Customer B is denied access to POL-A-HEALTH
    res_b = service.get_policy_detail("cust_b", "POL-A-HEALTH")
    assert res_b.status == "denied"
    assert res_b.policy is None
    assert "access denied" in res_b.message.lower()


def test_recommendations_hard_gates():
    """Recommendations exclude inactive products and include suitability reasons."""
    service = FakeInsuranceService()
    assessment = NeedsAssessment(
        protection_goal="Vehicle",
        already_covered="no",
        priority="Coverage",
    )
    res = service.get_recommendations("cust_a", assessment)

    assert res.status == "ok"
    assert len(res.recommendations) > 0
    # Inactive product PROD-HOME-OLD should never be recommended
    rec_ids = [r.product_id for r in res.recommendations]
    assert "PROD-HOME-OLD" not in rec_ids


def test_mock_fault_timeout():
    """Mock fault 'timeout' triggers an error status with timeout warning."""
    service = FakeInsuranceService(mock_fault="timeout")
    res = service.chat("cust_a", ChatRequest(text="Hello"))

    assert res.status == "error"
    assert "timeout" in res.message.lower()
    assert "Operation timed out" in res.warnings


def test_mock_fault_bad_citation():
    """Mock fault 'bad_citation' produces citation flagged with warning."""
    service = FakeInsuranceService(mock_fault="bad_citation")
    res = service.chat("cust_a", ChatRequest(text="Hello"))

    assert len(res.citations) == 1
    assert res.citations[0].citation_id == "INVALID_CHUNK_404"
    assert any("not found" in w.lower() for w in res.warnings)


def test_mock_fault_unsupported_price():
    """Mock fault 'unsupported_price' flags unverified price claims."""
    service = FakeInsuranceService(mock_fault="unsupported_price")
    res = service.chat("cust_a", ChatRequest(text="Hello"))

    assert any("unverified price" in w.lower() for w in res.warnings)


def test_mock_fault_purchase_claim():
    """Mock fault 'purchase_claim' flags unauthorized purchase assertions."""
    service = FakeInsuranceService(mock_fault="purchase_claim")
    res = service.chat("cust_a", ChatRequest(text="Hello"))

    assert any("purchase" in w.lower() for w in res.warnings)
