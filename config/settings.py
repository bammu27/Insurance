"""Application configuration and settings."""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "documents"
DATABASE_PATH = BASE_DIR / "insurance_demo.db"

# Runtime mode
APP_MODE = os.getenv("APP_MODE", "demo")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")

# Mock Fault Injection for Testing
# Supported values: "none", "bad_citation", "timeout", "unsupported_price", "purchase_claim"
MOCK_FAULT = os.getenv("MOCK_FAULT", "none")

# Admin Authentication from Environment
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "secret_admin_key_2026")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "AdminSecurePass@2026")

# Limits
MAX_CSV_ROWS = int(os.getenv("MAX_CSV_ROWS", "5000"))
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "5"))
