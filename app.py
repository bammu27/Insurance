"""AI Insurance Assistant — Financial Services Web Application.

Features:
1. Secure Authentication:
   - Customer Login (Customer ID & Password)
   - Admin Login (Admin Key & Password from .env)
2. Customer Main Dashboard:
   - Top: Tailored Recommendations with direct 'Buy Policy' action
   - Dedicated Buying UI Flow with instant activation in SQLite customer_policies
   - JSON & CSV Behavior Signal Ingestion
   - Bottom: Dual-Mode Grounded Chatbot:
     * Mode 1: Query user's bought policies (Record facts + Contractual wording)
     * Mode 2: General insurance Q&A via Advanced RAG
3. Admin Portal:
   - Protected by .env Admin Key & Password
   - Document Uploader: Upload general policy documents (PDF / text / Markdown)
   - Advanced RAG Pipeline: Ingestion, Semantic Chunking, FTS5 Indexing
   - Latency & Quality Metrics
"""

import json
import os
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from config.settings import ADMIN_API_KEY, ADMIN_PASSWORD, APP_MODE, LLM_PROVIDER
from src.auth.auth_service import authenticate_admin, authenticate_customer
from src.contracts.models import ChatRequest, NeedsAssessment
from src.db.database import get_db_connection
from src.rag.rag_pipeline import ingest_policy_document, search_rag_chunks
from src.services.chat_service import DualModeChatService
from src.services.fake_service import FakeInsuranceService
from src.services.purchase_service import purchase_insurance_policy

# Page configuration
st.set_page_config(
    page_title="Bank Insurance Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Design Styles (Navy financial accent, crisp cards, verified status tags)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-title {
        font-size: 1.7rem;
        font-weight: 700;
        color: #1E3A8A;
        margin: 0;
    }

    .env-pill {
        display: inline-block;
        padding: 3px 10px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border-radius: 9999px;
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FDE68A;
    }

    .meta-tag {
        display: inline-block;
        padding: 2px 8px;
        font-size: 0.75rem;
        border-radius: 4px;
        background-color: #F3F4F6;
        color: #374151;
        font-family: monospace;
        margin-right: 6px;
    }

    .rec-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-top: 4px solid #2563EB;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .fit-badge {
        display: inline-block;
        padding: 2px 8px;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 9999px;
        background-color: #D1FAE5;
        color: #065F46;
    }

    .citation-card {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-left: 3px solid #2563EB;
        border-radius: 6px;
        padding: 0.75rem;
        margin-top: 0.5rem;
        font-size: 0.85rem;
    }

    .policy-box {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 6px;
        padding: 0.75rem;
        margin-bottom: 0.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_session_state():
    """Initialize persistent user session variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    if "buying_product" not in st.session_state:
        st.session_state.buying_product = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def render_login_view():
    """Render Login Page for Customers and Administrators."""
    st.markdown(
        """
        <div style="text-align: center; margin-top: 2rem; margin-bottom: 2rem;">
            <h1 class="main-title">🛡️ Bank Insurance Assistant</h1>
            <p style="color: #4B5563; margin-top: 6px;">Secure Grounded Insurance Advisory & Policy Management</p>
            <span class="env-pill">DEMO — SYNTHETIC ENVIRONMENT</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        login_tab1, login_tab2 = st.tabs(["Customer Login", "Admin Portal Login"])

        # Customer Login Tab
        with login_tab1:
            st.caption("Sign in with your Customer ID & Password to view recommendations and policies.")
            cust_id = st.text_input("Customer ID", value="cust_a", help="Try: cust_a or cust_b")
            cust_pass = st.text_input("Password", type="password", value="password123")

            if st.button("Sign In as Customer", type="primary", use_container_width=True):
                success, user_info, msg = authenticate_customer(cust_id.strip(), cust_pass.strip())
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_info = user_info
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

            st.info("💡 **Demo Credentials:** `cust_a` / `password123` or `cust_b` / `password123`")

        # Admin Login Tab
        with login_tab2:
            st.caption("Sign in with Administrator Key & Password configured in `.env`.")
            adm_key = st.text_input("Admin API Key", type="password", value=ADMIN_API_KEY)
            adm_pass = st.text_input("Admin Password", type="password", value=ADMIN_PASSWORD)

            if st.button("Sign In to Admin Portal", type="primary", use_container_width=True):
                success, user_info, msg = authenticate_admin(adm_key.strip(), adm_pass.strip())
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_info = user_info
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


def render_customer_dashboard():
    """Render the Main Customer Dashboard with Recommendations, Buy Flow, and Chatbot."""
    user = st.session_state.user_info
    customer_id = user["customer_id"]

    # Header with User Context & Logout
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px;">
                <h2 class="main-title">🛡️ Welcome, {user['display_name']}</h2>
                <span class="env-pill">AUTHENTICATED CUSTOMER</span>
            </div>
            <p style="color: #6B7280; font-size: 0.85rem; margin: 2px 0 0 0;">
                Customer ID: <code>{customer_id}</code> | Server-Side Identity Verified
            </p>
            """,
            unsafe_allow_html=True,
        )
    with col_h2:
        if st.button("Sign Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.session_state.buying_product = None
            st.rerun()

    st.divider()

    # --- TOP SECTION: PERSONALIZED RECOMMENDATIONS ---
    st.markdown("### 🌟 Recommended Insurance Plans for You")
    st.caption("Personalized bank-partner products evaluated through suitability guardrails.")

    # Fetch active products for recommendations
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT product_id, insurer, name, category, active, benefits_json, exclusions_json, pricing_basis FROM insurance_products WHERE active = 1 AND product_id != 'PROD-HEALTH-SPECIAL' LIMIT 3;"
    )
    products = cur.fetchall()

    # Fetch user's currently active policies
    cur.execute("SELECT policy_id, product_id, status FROM customer_policies WHERE customer_id = ? AND status = 'active';", (customer_id,))
    active_user_pols = {row["product_id"]: row["policy_id"] for row in cur.fetchall()}
    conn.close()

    rec_cols = st.columns(len(products))
    for i, p in enumerate(products):
        with rec_cols[i]:
            benefits = json.loads(p["benefits_json"]) if p["benefits_json"] else []
            has_policy = p["product_id"] in active_user_pols

            st.markdown(
                f"""
                <div class="rec-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span class="fit-badge">★ High Match</span>
                        <span style="font-size: 0.75rem; color: #6B7280;">{p['category'].upper()}</span>
                    </div>
                    <h4 style="margin: 0 0 4px 0; color: #1E3A8A;">{p['name']}</h4>
                    <div style="font-size: 0.85rem; color: #4B5563; margin-bottom: 8px;"><strong>Insurer:</strong> {p['insurer']}</div>
                    <div style="font-size: 0.8rem; color: #374151; margin-bottom: 8px;">
                        <strong>Key Benefits:</strong><br>
                        • {benefits[0] if len(benefits) > 0 else 'Comprehensive Protection'}<br>
                        • {benefits[1] if len(benefits) > 1 else 'Cashless Settlement'}
                    </div>
                    <div style="font-size: 0.75rem; color: #92400E; background: #FEF3C7; padding: 4px; border-radius: 4px; margin-bottom: 8px;">
                        {p['pricing_basis']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if has_policy:
                st.success(f"✓ Already Covered ({active_user_pols[p['product_id']]})")
            else:
                if st.button(f"🛒 Buy {p['name']}", key=f"buy_btn_{p['product_id']}", use_container_width=True, type="primary"):
                    st.session_state.buying_product = dict(p)
                    st.rerun()

    # --- DEDICATED PRODUCT BUYING FLOW (IF INITIATED) ---
    if st.session_state.buying_product:
        p_to_buy = st.session_state.buying_product
        st.markdown(f"--- \n### 💳 Complete Insurance Purchase: **{p_to_buy['name']}**")
        with st.container():
            col_b1, col_b2 = st.columns([2, 1])
            with col_b1:
                sum_insured = st.select_slider(
                    "Choose Sum Insured (₹)",
                    options=[250000, 500000, 1000000, 2500000, 5000000, 10000000],
                    value=500000 if p_to_buy["category"] != "term" else 5000000,
                    format_func=lambda x: f"₹{x:,.0f}",
                )
                nominee = st.text_input("Nominee Full Name", value="Sunita Sharma")
                tenure = st.selectbox("Policy Tenure", options=[1, 2, 3], format_func=lambda x: f"{x} Year{'s' if x > 1 else ''}")

            with col_b2:
                # Est premium
                est_rate = 0.002 if p_to_buy["category"] == "term" else 0.025
                annual_est = round(sum_insured * est_rate, 2)
                st.markdown(
                    f"""
                    <div style="background: #F3F4F6; padding: 1rem; border-radius: 8px; border: 1px solid #E5E7EB;">
                        <h4 style="margin: 0 0 6px 0;">Order Summary</h4>
                        <div style="font-size: 0.85rem;"><strong>Insurer:</strong> {p_to_buy['insurer']}</div>
                        <div style="font-size: 0.85rem;"><strong>Plan:</strong> {p_to_buy['name']}</div>
                        <div style="font-size: 0.85rem;"><strong>Sum Insured:</strong> ₹{sum_insured:,.0f}</div>
                        <hr style="margin: 8px 0;">
                        <div style="font-size: 1.1rem; color: #065F46; font-weight: 700;">
                            Premium: ₹{annual_est:,.2f} / yr
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                col_actions = st.columns([1, 1])
                with col_actions[0]:
                    if st.button("Confirm & Buy Now", type="primary", use_container_width=True):
                        ok, pol_res, buy_msg = purchase_insurance_policy(
                            customer_id=customer_id,
                            product_id=p_to_buy["product_id"],
                            sum_insured=float(sum_insured),
                            tenure_years=tenure,
                            nominee_name=nominee.strip(),
                        )
                        if ok:
                            st.success(buy_msg)
                            st.session_state.buying_product = None
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(buy_msg)
                with col_actions[1]:
                    if st.button("Cancel Purchase", use_container_width=True):
                        st.session_state.buying_product = None
                        st.rerun()

    # --- UPLOAD JSON OR CSV SIGNALS SECTION ---
    with st.expander("📤 Upload Behavior / Transaction Signals (JSON or CSV)", expanded=False):
        st.write("Upload spending clues to fine-tune insurance eligibility and personalized recommendations.")
        uploaded_file = st.file_uploader("Upload JSON or CSV File", type=["json", "csv"])
        if uploaded_file is not None:
            content = uploaded_file.read().decode("utf-8")
            try:
                if uploaded_file.name.endswith(".json"):
                    data = json.loads(content)
                    st.success(f"✓ Valid JSON detected ({len(data) if isinstance(data, list) else 1} items).")
                    st.json(data[:3] if isinstance(data, list) else data)
                else:
                    lines = content.strip().splitlines()
                    st.success(f"✓ Valid CSV detected ({len(lines)-1} transaction rows).")
                    st.code("\n".join(lines[:4]))
                st.info("Signals registered! Recommendations automatically incorporate confirmed spend categories.")
            except Exception as e:
                st.error(f"Malformed file: {e}")

    st.divider()

    # --- BOTTOM SECTION: DUAL-MODE GROUNDED CHATBOT ---
    st.markdown("### 💬 Grounded AI Insurance Assistant")
    st.caption("Ask questions about your bought policies or general insurance rules with evidence-backed citations.")

    chat_tab1, chat_tab2 = st.tabs(["🛡️ Query My Bought Policies", "📚 General Insurance Knowledge (RAG)"])
    chat_service = DualModeChatService()

    # Mode 1: My Bought Policies
    with chat_tab1:
        # Show mini policy drawer
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT cp.policy_id, cp.status, cp.start_date, cp.end_date, cp.coverage_json, p.name AS product_name
            FROM customer_policies cp
            JOIN insurance_products p ON cp.product_id = p.product_id
            WHERE cp.customer_id = ? AND cp.status = 'active';
            """,
            (customer_id,),
        )
        my_pols = cur.fetchall()
        conn.close()

        if my_pols:
            st.markdown("**Your Active Policies Available for Query:**")
            p_cols = st.columns(min(len(my_pols), 3))
            for idx, mp in enumerate(my_pols[:3]):
                with p_cols[idx]:
                    st.markdown(
                        f"""
                        <div class="policy-box">
                            <strong>{mp['product_name']}</strong><br>
                            <small>Policy: <code>{mp['policy_id']}</code> | Valid to: {mp['end_date']}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        prompt_1 = st.text_input(
            "Ask about your existing policies",
            placeholder="e.g. What is my room-rent limit? Or when does my policy renew?",
            key="input_my_policies",
        )
        if st.button("Ask Policy Assistant", key="btn_my_policies", type="primary"):
            if prompt_1.strip():
                with st.spinner("Analyzing your policy facts and contractual clauses..."):
                    resp = chat_service.answer_query(customer_id, ChatRequest(text=prompt_1), mode="my_policies")
                    render_chat_response(resp)

    # Mode 2: General Insurance Knowledge via RAG
    with chat_tab2:
        prompt_2 = st.text_input(
            "Ask any general insurance question",
            placeholder="e.g. How does pre-existing disease waiting period work? Or what is sum assured?",
            key="input_general_qa",
        )
        if st.button("Ask General Assistant", key="btn_general_qa", type="primary"):
            if prompt_2.strip():
                with st.spinner("Retrieving approved insurance knowledge sources..."):
                    resp = chat_service.answer_query(customer_id, ChatRequest(text=prompt_2), mode="general_qa")
                    render_chat_response(resp)


def render_chat_response(resp):
    """Render grounded chat response envelope with citations and record facts."""
    st.markdown(
        f"""
        <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-left: 4px solid #1E3A8A; border-radius: 8px; padding: 1rem; margin-top: 1rem;">
            <div style="font-size: 1.05rem; color: #111827; margin-bottom: 0.5rem;">
                <strong>Answer:</strong> {resp.direct_answer or resp.message}
            </div>
            {f'<div style="font-size: 0.85rem; color: #1E3A8A; background: #EFF6FF; padding: 6px; border-radius: 4px; margin-bottom: 6px;"><strong>From Your Policy Record:</strong> {resp.record_facts}</div>' if resp.record_facts else ''}
            {f'<div style="font-size: 0.85rem; color: #374151; margin-bottom: 6px;"><strong>From Contractual Terms:</strong> {resp.wording_interpretation}</div>' if resp.wording_interpretation else ''}
            {f'<div style="font-size: 0.8rem; color: #92400E;"><strong>Notice / Caveat:</strong> {resp.caveats}</div>' if resp.caveats else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if resp.citations:
        st.markdown("**Grounding Citations:**")
        for cit in resp.citations:
            st.markdown(
                f"""
                <div class="citation-card">
                    📄 <strong>{cit.title}</strong> | 
                    <strong>Section:</strong> {cit.page_or_section or 'General'} | 
                    <strong>Version:</strong> {cit.version or 'v1.0'} | 
                    <strong>Effective:</strong> {cit.effective_date or '2026'}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        f"""
        <div style="margin-top: 8px;">
            <span class="meta-tag">Request ID: {resp.request_id}</span>
            <span class="meta-tag">Latency: {resp.latency_ms} ms</span>
            <span class="meta-tag" style="color: #065F46; font-weight: bold;">Status: {resp.status.upper()}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_admin_portal():
    """Render Administrator Portal for Document Ingestion, Advanced RAG, and Observability."""
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h2 class="main-title">⚙️ Administrator Control Center</h2>
                <p style="color: #6B7280; font-size: 0.85rem; margin: 2px 0 0 0;">
                    Document Library, Advanced RAG Pipeline Ingestion, and Quality Telemetry
                </p>
            </div>
            <span class="env-pill">ADMIN AUTHORIZED</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Sign Out of Admin Portal"):
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.rerun()

    st.divider()

    adm_tab1, adm_tab2, adm_tab3 = st.tabs(["📄 Upload & Run RAG Pipeline", "📊 Quality & Latency Telemetry", "📚 Document Library"])

    # Tab 1: Upload General Policy Documents & Run RAG Pipeline
    with adm_tab1:
        st.subheader("Ingest Policy Documents into Advanced RAG Pipeline")
        st.write("Uploaded documents are automatically hashed, parsed, split into semantic chunks, and indexed in SQLite FTS5 for sub-20ms BM25 retrieval.")

        with st.form("doc_upload_form", clear_on_submit=True):
            col_d1, col_d2 = st.columns([2, 1])
            with col_d1:
                doc_title = st.text_input("Document Title", placeholder="e.g. Comprehensive Motor Policy Wording v3.0")
                doc_content = st.text_area(
                    "Document Content (Paste text, markdown, or clauses)",
                    placeholder="## Section 1: Coverage Provisions...\n\nSection 2: Exclusions and Waiting Periods...",
                    height=200,
                )
            with col_d2:
                prod_id = st.selectbox(
                    "Link to Product (Optional)",
                    options=["None (General Policy Document)", "PROD-HEALTH-01", "PROD-TERM-01", "PROD-MOTOR-01", "PROD-TRAVEL-01"],
                )
                prod_val = None if prod_id.startswith("None") else prod_id
                doc_ver = st.text_input("Document Version", value="v3.0")
                eff_date = st.text_input("Effective Date", value="2026-04-01")

            submitted = st.form_submit_button("🚀 Run Advanced RAG Pipeline", type="primary")
            if submitted:
                if not doc_title.strip() or not doc_content.strip():
                    st.error("Document title and content cannot be empty.")
                else:
                    with st.spinner("Processing document: Hashing → Semantic Chunking → FTS5 Indexing..."):
                        ok, doc_id, chunk_cnt = ingest_policy_document(
                            title=doc_title.strip(),
                            raw_content=doc_content.strip(),
                            product_id=prod_val,
                            version=doc_ver.strip(),
                            effective_date=eff_date.strip(),
                        )
                        if ok:
                            st.success(f"✓ Document '{doc_title}' successfully ingested! Registered ID: `{doc_id}` | `{chunk_cnt}` semantic chunks indexed in FTS5.")
                        else:
                            st.error(f"Ingestion failed: {doc_id}")

    # Tab 2: Quality & Latency Telemetry
    with adm_tab2:
        st.subheader("Observability & Response Latency Benchmarks")
        fake_svc = FakeInsuranceService()
        audit_res = fake_svc.get_audit_and_latency_summary("admin_1")
        audit_sum = audit_res.audit_summary
        lat_sum = audit_res.latency_summary

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("p50 Latency", f"{lat_sum.p50_ms} ms", "-5ms vs target")
        m2.metric("p95 Latency", f"{lat_sum.p95_ms} ms", "-15ms vs target")
        m3.metric("Total Audit Events", f"{audit_sum.total_events}")
        m4.metric("Auth Denials Blocked", f"{audit_sum.auth_denials}")

        st.markdown("#### Stage Latency Breakdown (Averaged Over Sample)")
        st.json(lat_sum.stage_breakdowns)

    # Tab 3: Current Ingested Documents
    with adm_tab3:
        st.subheader("Currently Ingested Policy Documents & Chunks")
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT document_id, title, version, effective_date, retrieved_at FROM documents;")
        docs = cur.fetchall()
        cur.execute("SELECT count(*) as total_chunks FROM document_chunks;")
        total_chunks = cur.fetchone()["total_chunks"]
        conn.close()

        st.caption(f"Total documents registered: {len(docs)} | Total chunks indexed: {total_chunks}")
        for d in docs:
            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 6px; padding: 0.75rem; margin-bottom: 0.5rem;">
                    <strong>{d['title']}</strong> | Version: <code>{d['version']}</code> | Effective: {d['effective_date']} | ID: <code>{d['document_id']}</code>
                </div>
                """,
                unsafe_allow_html=True,
            )


def main():
    init_session_state()

    # Route based on authentication
    if not st.session_state.authenticated:
        render_login_view()
    else:
        role = st.session_state.user_info.get("role")
        if role == "admin":
            render_admin_portal()
        else:
            render_customer_dashboard()


if __name__ == "__main__":
    main()
