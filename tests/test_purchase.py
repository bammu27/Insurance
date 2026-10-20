"""Tests for Insurance Purchase Service."""

from src.db.database import get_db_connection
from src.services.purchase_service import purchase_insurance_policy


def test_purchase_active_policy():
    """Customer purchases an active motor product; policy is created and activated."""
    success, pol, msg = purchase_insurance_policy(
        customer_id="cust_a",
        product_id="PROD-MOTOR-01",
        sum_insured=500000.0,
        tenure_years=1,
        nominee_name="Pooja Sharma",
    )
    assert success is True
    assert pol is not None
    assert pol["status"] == "active"
    assert pol["category"] == "motor"
    assert pol["nominee_name"] == "Pooja Sharma"

    # Verify directly in SQLite
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT policy_id, status FROM customer_policies WHERE policy_id = ?;", (pol["policy_id"],))
    row = cur.fetchone()
    conn.close()

    assert row is not None
    assert row["status"] == "active"


def test_purchase_inactive_policy_rejected():
    """Customer cannot purchase an inactive product."""
    success, pol, msg = purchase_insurance_policy(
        customer_id="cust_a",
        product_id="PROD-HOME-OLD",  # inactive product
        sum_insured=1000000.0,
    )
    assert success is False
    assert pol is None
    assert "inactive" in msg.lower()
