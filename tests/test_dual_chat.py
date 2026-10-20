"""Tests for Dual-Mode Grounded Chatbot Service."""

from src.contracts.models import ChatRequest
from src.services.chat_service import DualModeChatService


def test_dual_mode_my_policies_room_rent():
    """Customer A asks about room rent limit; gets record facts and wording citation."""
    svc = DualModeChatService()
    req = ChatRequest(text="What is my room rent limit?")
    resp = svc.answer_query("cust_a", req, mode="my_policies")

    assert resp.status == "ok"
    assert "1%" in resp.direct_answer
    assert "POL-A-HEALTH" in resp.record_facts
    assert resp.citations is not None
    assert len(resp.citations) > 0
    assert resp.latency_ms < 500.0  # Fast local retrieval benchmark


def test_dual_mode_general_qa():
    """General insurance question returns evidence and citations via RAG."""
    svc = DualModeChatService()
    req = ChatRequest(text="Explain waiting periods in health insurance")
    resp = svc.answer_query("cust_a", req, mode="general_qa")

    assert resp.status == "ok"
    assert len(resp.message) > 20
    assert len(resp.citations) > 0
    assert resp.latency_ms < 500.0
