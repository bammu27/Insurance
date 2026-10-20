"""Database schema and deterministic seed tests.

Verifies acceptance criteria M0.2:
- Running seed twice gives identical data (hash is stable).
- All 11 tables exist with required test fixtures.
"""

import hashlib
import sqlite3
from pathlib import Path

from config.settings import DATABASE_PATH
from data.seed_demo_data import seed_data
from src.db.database import get_db_connection


def test_seed_hash_stability(tmp_path: Path):
    """Criterion M0.2: Running the seed twice gives an identical database dump."""
    test_db = tmp_path / "test_insurance.db"

    # First run
    seed_data(test_db, reset=True)
    conn1 = sqlite3.connect(str(test_db))
    dump1 = "".join(conn1.iterdump()).encode("utf-8")
    conn1.close()
    hash1 = hashlib.sha256(dump1).hexdigest()

    # Second run
    seed_data(test_db, reset=True)
    conn2 = sqlite3.connect(str(test_db))
    dump2 = "".join(conn2.iterdump()).encode("utf-8")
    conn2.close()
    hash2 = hashlib.sha256(dump2).hexdigest()

    assert hash1 == hash2, "Seed data must produce identical dumps across runs"


def test_seed_fixtures_completeness():
    """Verify all 11 tables and expected fixtures are seeded."""
    conn = get_db_connection(DATABASE_PATH)
    cur = conn.cursor()

    # Verify 11 tables
    expected_tables = [
        "users",
        "customers",
        "transactions",
        "insurance_products",
        "customer_policies",
        "documents",
        "document_chunks",
        "recommendations",
        "feedback",
        "assistance_sessions",
        "audit_events",
    ]
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    existing_tables = [row["name"] for row in cur.fetchall()]
    for tbl in expected_tables:
        assert tbl in existing_tables, f"Table {tbl} must exist in SQLite schema"

    # Verify users
    cur.execute("SELECT user_id, role FROM users ORDER BY user_id;")
    users = {row["user_id"]: row["role"] for row in cur.fetchall()}
    assert users["cust_a"] == "customer"
    assert users["cust_b"] == "customer"
    assert users["emp_1"] == "employee"
    assert users["admin_1"] == "admin"

    # Verify Customer A policies (Active health, Expired travel)
    cur.execute("SELECT policy_id, status FROM customer_policies WHERE customer_id = 'cust_a';")
    cust_a_pols = {row["policy_id"]: row["status"] for row in cur.fetchall()}
    assert cust_a_pols["POL-A-HEALTH"] == "active"
    assert cust_a_pols["POL-A-TRAVEL"] == "expired"

    # Verify Customer B policies (Active term)
    cur.execute("SELECT policy_id, status FROM customer_policies WHERE customer_id = 'cust_b';")
    cust_b_pols = {row["policy_id"]: row["status"] for row in cur.fetchall()}
    assert cust_b_pols["POL-B-TERM"] == "active"

    # Verify Products (6 total: 1 inactive, 1 unknown eligibility)
    cur.execute("SELECT product_id, active, source_status FROM insurance_products;")
    prods = {row["product_id"]: row for row in cur.fetchall()}
    assert len(prods) == 6
    assert prods["PROD-HOME-OLD"]["active"] == 0  # Inactive product
    assert prods["PROD-HEALTH-SPECIAL"]["source_status"] == "unknown_eligibility"

    # Verify Documents & Injection chunk
    cur.execute("SELECT chunk_id, chunk_text FROM document_chunks WHERE chunk_id = 'CHUNK-HEALTH-INJECTION';")
    inj = cur.fetchone()
    assert inj is not None
    assert "ignore previous instructions" in inj["chunk_text"].lower()

    conn.close()
