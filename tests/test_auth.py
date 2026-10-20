"""Tests for Authentication Service."""

from config.settings import ADMIN_API_KEY, ADMIN_PASSWORD
from src.auth.auth_service import authenticate_admin, authenticate_customer, hash_password


def test_customer_auth_valid():
    """Customer A signs in with valid password."""
    success, user, msg = authenticate_customer("cust_a", "password123")
    assert success is True
    assert user is not None
    assert user["customer_id"] == "cust_a"
    assert user["role"] == "customer"
    assert "successful" in msg.lower()


def test_customer_auth_invalid_password():
    """Customer A rejects incorrect password."""
    success, user, msg = authenticate_customer("cust_a", "wrong_password")
    assert success is False
    assert user is None
    assert "invalid" in msg.lower()


def test_customer_auth_unknown_user():
    """Unknown customer ID is rejected."""
    success, user, msg = authenticate_customer("unknown_cust", "password123")
    assert success is False
    assert user is None


def test_admin_auth_valid():
    """Admin signs in with valid key and password from environment."""
    success, user, msg = authenticate_admin(ADMIN_API_KEY, ADMIN_PASSWORD)
    assert success is True
    assert user is not None
    assert user["role"] == "admin"


def test_admin_auth_invalid():
    """Admin authentication fails with wrong key."""
    success, user, msg = authenticate_admin("wrong_key", ADMIN_PASSWORD)
    assert success is False
    assert user is None


def test_hash_password_consistency():
    """Password hashing is deterministic and non-trivial."""
    h1 = hash_password("mypassword")
    h2 = hash_password("mypassword")
    assert h1 == h2
    assert len(h1) == 64
