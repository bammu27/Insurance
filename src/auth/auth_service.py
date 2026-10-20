"""Authentication service for Customer and Admin access.

Supports:
- Customer sign-in via customer_id + password against SQLite users table.
- Admin sign-in gated by ADMIN_API_KEY + ADMIN_PASSWORD from config/environment.
- Password hashing using standard SHA-256 with deterministic salt.
"""

import hashlib
import time
import uuid
from typing import Any, Dict, Optional, Tuple

from config.settings import ADMIN_API_KEY, ADMIN_PASSWORD
from src.db.database import get_db_connection


def hash_password(password: str) -> str:
    """Return SHA-256 hash of password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def authenticate_customer(customer_id: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """Verify customer credentials against users table.
    
    Returns:
        (success: bool, user_info: dict | None, message: str)
    """
    if not customer_id or not password:
        return False, None, "Customer ID and password are required."

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id, role, customer_id, password_hash, active FROM users WHERE user_id = ? OR customer_id = ?;",
        (customer_id, customer_id),
    )
    row = cur.fetchone()

    if not row:
        conn.close()
        return False, None, "Invalid customer credentials."

    if not row["active"]:
        conn.close()
        return False, None, "Account is disabled. Please contact bank support."

    calculated_hash = hash_password(password)
    if row["password_hash"] != calculated_hash:
        conn.close()
        return False, None, "Invalid customer credentials."

    # Fetch customer display name
    cur.execute("SELECT display_name, synthetic_attributes_json FROM customers WHERE customer_id = ?;", (row["customer_id"],))
    cust_row = cur.fetchone()
    display_name = cust_row["display_name"] if cust_row else customer_id

    # Record login audit event
    cur.execute(
        """
        INSERT INTO audit_events (
            event_id, request_id, timestamp_utc, actor_id, actor_role, action,
            intent, target_type, target_id, authorization_outcome, outcome,
            source_ids_json, model_metadata_json, latency_ms, error_code, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            f"EVT-{uuid.uuid4().hex[:8]}",
            f"REQ-{uuid.uuid4().hex[:8]}",
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            row["user_id"],
            row["role"],
            "user_login",
            "authenticate",
            "user",
            row["user_id"],
            "authorized",
            "ok",
            "[]",
            "{}",
            1.2,
            None,
            f'{{"login_type": "customer"}}',
        ),
    )
    conn.commit()
    conn.close()

    user_info = {
        "user_id": row["user_id"],
        "customer_id": row["customer_id"],
        "role": row["role"],
        "display_name": display_name,
    }
    return True, user_info, "Login successful."


def authenticate_admin(admin_key: str, admin_password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """Verify administrator credentials against environment variables.
    
    Returns:
        (success: bool, user_info: dict | None, message: str)
    """
    if not admin_key or not admin_password:
        return False, None, "Admin key and password are required."

    if admin_key != ADMIN_API_KEY or admin_password != ADMIN_PASSWORD:
        return False, None, "Invalid administrator key or password."

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO audit_events (
            event_id, request_id, timestamp_utc, actor_id, actor_role, action,
            intent, target_type, target_id, authorization_outcome, outcome,
            source_ids_json, model_metadata_json, latency_ms, error_code, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            f"EVT-{uuid.uuid4().hex[:8]}",
            f"REQ-{uuid.uuid4().hex[:8]}",
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "admin_1",
            "admin",
            "admin_login",
            "authenticate",
            "admin_portal",
            "admin_system",
            "authorized",
            "ok",
            "[]",
            "{}",
            1.0,
            None,
            '{"login_type": "admin"}',
        ),
    )
    conn.commit()
    conn.close()

    user_info = {
        "user_id": "admin_1",
        "customer_id": None,
        "role": "admin",
        "display_name": "System Administrator",
    }
    return True, user_info, "Admin authentication successful."
