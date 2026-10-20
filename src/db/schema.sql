CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    role TEXT NOT NULL,
    customer_id TEXT,
    password_hash TEXT NOT NULL DEFAULT '',
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    synthetic_attributes_json TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',
    source TEXT NOT NULL,
    imported_at TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS insurance_products (
    product_id TEXT PRIMARY KEY,
    insurer TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    eligibility_json TEXT,
    benefits_json TEXT,
    exclusions_json TEXT,
    pricing_basis TEXT,
    source_status TEXT
);

CREATE TABLE IF NOT EXISTS customer_policies (
    policy_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    status TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    coverage_json TEXT,
    premium_amount REAL NOT NULL,
    premium_status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES insurance_products(product_id)
);

CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    product_id TEXT,
    title TEXT NOT NULL,
    source_url TEXT,
    source_type TEXT NOT NULL,
    version TEXT NOT NULL,
    effective_date TEXT NOT NULL,
    retrieved_at TEXT NOT NULL,
    content_hash TEXT,
    FOREIGN KEY (product_id) REFERENCES insurance_products(product_id)
);

CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    section_title TEXT NOT NULL,
    page_number INTEGER,
    chunk_text TEXT NOT NULL,
    metadata_json TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);

CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    score_internal REAL,
    status TEXT NOT NULL,
    reasons_json TEXT,
    assumptions_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES insurance_products(product_id)
);

CREATE TABLE IF NOT EXISTS feedback (
    feedback_id TEXT PRIMARY KEY,
    recommendation_id TEXT,
    customer_id TEXT NOT NULL,
    rating INTEGER NOT NULL,
    comment_optional TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS assistance_sessions (
    session_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    purpose TEXT NOT NULL,
    authorization_status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    FOREIGN KEY (employee_id) REFERENCES users(user_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS audit_events (
    event_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    timestamp_utc TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    actor_role TEXT NOT NULL,
    action TEXT NOT NULL,
    intent TEXT,
    target_type TEXT,
    target_id TEXT,
    authorization_outcome TEXT NOT NULL,
    outcome TEXT NOT NULL,
    source_ids_json TEXT,
    model_metadata_json TEXT,
    latency_ms REAL NOT NULL DEFAULT 0.0,
    error_code TEXT,
    metadata_json TEXT
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_policies_customer ON customer_policies(customer_id);
CREATE INDEX IF NOT EXISTS idx_chunks_document ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp_utc);
CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_events(actor_id);

-- Full-Text Search (FTS5) for RAG Pipeline
CREATE VIRTUAL TABLE IF NOT EXISTS document_chunks_fts USING fts5(
    chunk_id UNINDEXED,
    document_id UNINDEXED,
    section_title,
    chunk_text,
    tokenize='porter unicode61'
);

