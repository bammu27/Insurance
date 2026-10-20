"""Policy purchase service allowing customers to buy active insurance products.

Upon purchase, an active policy record is created directly in SQLite customer_policies,
making it immediately queryable in the customer's 'My Policies' tab and Chatbot.
"""

import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from src.db.database import get_db_connection


def purchase_insurance_policy(
    customer_id: str,
    product_id: str,
    sum_insured: float,
    tenure_years: int = 1,
    nominee_name: str = "Nominated Family Member",
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """Execute policy purchase and store in customer_policies table.
    
    Returns:
        (success: bool, policy_data: dict | None, message: str)
    """
    if not customer_id or not product_id:
        return False, None, "Customer ID and product ID are required."

    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Verify product exists and is active
    cur.execute(
        "SELECT product_id, insurer, name, category, active, benefits_json, exclusions_json FROM insurance_products WHERE product_id = ?;",
        (product_id,),
    )
    product = cur.fetchone()

    if not product:
        conn.close()
        return False, None, f"Product {product_id} not found."

    if not product["active"]:
        conn.close()
        return False, None, f"Product '{product['name']}' is currently inactive in the catalog."

    # 2. Generate policy dates and deterministic/clean ID
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=365 * tenure_years)).strftime("%Y-%m-%d")
    clean_cat = product["category"].upper()
    policy_id = f"POL-{customer_id.upper()}-{clean_cat}-{uuid.uuid4().hex[:4].upper()}"

    # Calculate synthetic annual premium (e.g. 2.5% of sum insured for health/motor, 0.2% for term)
    if product["category"] == "term":
        annual_premium = round(sum_insured * 0.002, 2)
    elif product["category"] == "health":
        annual_premium = round(sum_insured * 0.025, 2)
    else:
        annual_premium = round(sum_insured * 0.03, 2)

    coverage_data = {
        "sum_insured": sum_insured,
        "tenure_years": tenure_years,
        "nominee_name": nominee_name,
        "benefits_summary": json.loads(product["benefits_json"]) if product["benefits_json"] else [],
        "exclusions_summary": json.loads(product["exclusions_json"]) if product["exclusions_json"] else [],
    }

    # 3. Insert active policy
    cur.execute(
        """
        INSERT INTO customer_policies (
            policy_id, customer_id, product_id, status, start_date, end_date,
            coverage_json, premium_amount, premium_status
        ) VALUES (?, ?, ?, 'active', ?, ?, ?, ?, 'paid_annual');
        """,
        (
            policy_id,
            customer_id,
            product_id,
            start_date,
            end_date,
            json.dumps(coverage_data, sort_keys=True),
            annual_premium,
        ),
    )

    # 4. Record audit event
    cur.execute(
        """
        INSERT INTO audit_events (
            event_id, request_id, timestamp_utc, actor_id, actor_role, action,
            intent, target_type, target_id, authorization_outcome, outcome,
            source_ids_json, model_metadata_json, latency_ms, error_code, metadata_json
        ) VALUES (?, ?, ?, ?, 'customer', 'policy_purchase', 'buy', 'policy', ?, 'authorized', 'ok', ?, '{}', 15.0, NULL, ?);
        """,
        (
            f"EVT-{uuid.uuid4().hex[:8]}",
            f"REQ-{uuid.uuid4().hex[:8]}",
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            customer_id,
            policy_id,
            json.dumps([product_id]),
            json.dumps({"product_name": product["name"], "premium": annual_premium}),
        ),
    )

    conn.commit()
    conn.close()

    result = {
        "policy_id": policy_id,
        "product_name": product["name"],
        "insurer": product["insurer"],
        "category": product["category"],
        "status": "active",
        "start_date": start_date,
        "end_date": end_date,
        "sum_insured": sum_insured,
        "premium_amount": annual_premium,
        "nominee_name": nominee_name,
    }

    return True, result, f"Policy {policy_id} for {product['name']} successfully issued and activated!"
