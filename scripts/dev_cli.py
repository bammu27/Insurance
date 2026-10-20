"""Developer CLI for backend manual testing and contract verification.

Calls the InsuranceService facade directly without UI dependencies.
Never trusts role or customer IDs from payload JSON.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from pydantic import ValidationError
from src.contracts.models import (
    ChatRequest,
    DemoHandoffRequest,
    FeedbackRequest,
    NeedsAssessment,
)
from src.services.fake_service import FakeInsuranceService


def parse_json_payload(json_str: str) -> Dict[str, Any]:
    """Parse JSON payload string safely."""
    if not json_str or not json_str.strip():
        return {}
    try:
        data = json.loads(json_str)
        if not isinstance(data, dict):
            raise ValueError("Payload must be a JSON object (dictionary)")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Malformed JSON payload: {e}")


def main():
    parser = argparse.ArgumentParser(description="Insurance Assistant Developer CLI")
    parser.add_argument(
        "method",
        choices=[
            "chat",
            "policies",
            "policy_detail",
            "preview_csv",
            "confirm_csv",
            "recommendations",
            "product_detail",
            "demo_handoff",
            "feedback",
            "audit",
        ],
        help="Backend service method to invoke",
    )
    parser.add_argument(
        "--user",
        required=True,
        help="Authenticated actor user ID (e.g. cust_a, cust_b, emp_1, admin_1)",
    )
    parser.add_argument(
        "--json",
        dest="payload_json",
        default="{}",
        help="JSON payload for the method request",
    )

    args = parser.parse_args()
    service = FakeInsuranceService()

    try:
        payload = parse_json_payload(args.payload_json)
    except ValueError as e:
        error_response = {
            "request_id": "error-cli",
            "status": "error",
            "message": f"Payload parsing error: {e}",
            "citations": [],
            "warnings": ["Invalid JSON passed to CLI"],
            "latency_ms": 0.0,
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)

    try:
        response_model = None

        if args.method == "chat":
            # Extra fields like actor_role or customer_id are rejected by extra='forbid'
            chat_req = ChatRequest(**payload)
            response_model = service.chat(args.user, chat_req)

        elif args.method == "policies":
            response_model = service.get_policies(args.user)

        elif args.method == "policy_detail":
            policy_id = payload.get("policy_id")
            if not policy_id:
                raise ValueError("Payload missing required field: 'policy_id'")
            response_model = service.get_policy_detail(args.user, policy_id)

        elif args.method == "preview_csv":
            csv_content = payload.get("csv", "")
            response_model = service.preview_behavior_import(args.user, csv_content)

        elif args.method == "confirm_csv":
            csv_content = payload.get("csv", "")
            response_model = service.confirm_behavior_import(args.user, csv_content)

        elif args.method == "recommendations":
            assessment = NeedsAssessment(**payload)
            response_model = service.get_recommendations(args.user, assessment)

        elif args.method == "product_detail":
            product_id = payload.get("product_id")
            if not product_id:
                raise ValueError("Payload missing required field: 'product_id'")
            response_model = service.get_product_detail(args.user, product_id)

        elif args.method == "demo_handoff":
            handoff_req = DemoHandoffRequest(**payload)
            response_model = service.request_demo_handoff(args.user, handoff_req)

        elif args.method == "feedback":
            fb_req = FeedbackRequest(**payload)
            response_model = service.submit_feedback(args.user, fb_req)

        elif args.method == "audit":
            response_model = service.get_audit_and_latency_summary(args.user)

        if response_model is not None:
            print(json.dumps(response_model.model_dump(), indent=2))

    except ValidationError as e:
        # Pydantic validation errors (including forbidden fields or min_length violation)
        errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        error_response = {
            "request_id": "error-validation",
            "status": "error",
            "message": f"Validation failed: {'; '.join(errors)}",
            "citations": [],
            "warnings": [err["msg"] for err in e.errors()],
            "latency_ms": 0.0,
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)
    except Exception as e:
        error_response = {
            "request_id": "error-general",
            "status": "error",
            "message": str(e),
            "citations": [],
            "warnings": ["Unexpected error occurred"],
            "latency_ms": 0.0,
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
