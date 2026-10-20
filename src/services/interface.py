"""Interface definition for the Insurance Service facade."""

from abc import ABC, abstractmethod

from src.contracts.models import (
    AuditResponse,
    BehaviorImportPreviewResponse,
    BehaviorImportResult,
    ChatRequest,
    ChatResponse,
    DemoHandoffRequest,
    DemoHandoffResponse,
    FeedbackRequest,
    FeedbackResult,
    NeedsAssessment,
    PolicyDetailResponse,
    PolicyListResponse,
    ProductDetailResponse,
    RecommendationResponse,
)


class InsuranceService(ABC):
    """Abstract facade for all customer, employee, and admin insurance capabilities."""

    @abstractmethod
    def chat(self, actor_user_id: str, request: ChatRequest) -> ChatResponse:
        """Process general or policy-specific chat queries."""
        pass

    @abstractmethod
    def get_policies(self, actor_user_id: str) -> PolicyListResponse:
        """Fetch all policies accessible to the actor."""
        pass

    @abstractmethod
    def get_policy_detail(self, actor_user_id: str, policy_id: str) -> PolicyDetailResponse:
        """Fetch details for a specific policy with authorization checks."""
        pass

    @abstractmethod
    def preview_behavior_import(self, actor_user_id: str, raw_csv: str) -> BehaviorImportPreviewResponse:
        """Parse, validate, and preview uploaded behavior signals without persisting."""
        pass

    @abstractmethod
    def confirm_behavior_import(self, actor_user_id: str, raw_csv: str) -> BehaviorImportResult:
        """Confirm and persist valid scoped behavior signals."""
        pass

    @abstractmethod
    def get_recommendations(self, actor_user_id: str, assessment: NeedsAssessment) -> RecommendationResponse:
        """Generate and rank suitable insurance product recommendations."""
        pass

    @abstractmethod
    def get_product_detail(self, actor_user_id: str, product_id: str) -> ProductDetailResponse:
        """Fetch verified product catalog details."""
        pass

    @abstractmethod
    def request_demo_handoff(self, actor_user_id: str, request: DemoHandoffRequest) -> DemoHandoffResponse:
        """Simulate a mock hand-off to a partner channel."""
        pass

    @abstractmethod
    def submit_feedback(self, actor_user_id: str, request: FeedbackRequest) -> FeedbackResult:
        """Record user feedback for recommendations or answers."""
        pass

    @abstractmethod
    def get_audit_and_latency_summary(self, actor_user_id: str) -> AuditResponse:
        """Retrieve audit summary and latency percentiles."""
        pass
