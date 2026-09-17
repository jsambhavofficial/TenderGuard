import streamlit as st
import pandas as pd
from pathlib import Path
import json

from app.config import UPLOADS_DIR, SAMPLE_TENDERS_DIR, SAMPLE_COMPANY_DIR
from app.database.db import (
    init_db,
    get_all_documents,
    get_company_profile,
    save_or_update_company_profile
)
from app.pdf.sample_generator import generate_demo_tender_pdf
from app.pipeline import process_tender_pdf, query_tender_evidence
from app.rules.compliance import run_compliance_evaluation
from app.nlp.normalizer import format_currency_inr

def render_dashboard():
    st.set_page_config(
        page_title="TenderGuard — Tender Intelligence",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_db()

    # Custom Styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        padding: 1.1rem;
        border-radius: 8px;
        border: 1px solid rgba(128,128,128,0.2);
        text-align: center;
        margin-bottom: 0.8rem;
    }
    .kpi-num {
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
    }
    .kpi-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.05em;
        color: #64748b;
    }
    .evidence-box {
        background-color: rgba(2, 132, 199, 0.08);
        border-left: 4px solid #0284c7;
        padding: 14px 18px;
        border-radius: 4px;
        font-size: 0.95rem;
        line-height: 1.5;
        margin: 10px 0;
    }
    .status-pass {
        color: #16a34a;
        font-weight: bold;
    }
    .status-fail {
        color: #dc2626;
        font-weight: bold;
    }
    .status-action {
        color: #2563eb;
        font-weight: bold;
    }
    .status-ambiguous {
        color: #d97706;
        font-weight: bold;
    }
    .status-missing {
        color: #dc2626;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize Session State
    if "current_doc_id" not in st.session_state:
        st.session_state.current_doc_id = None
    if "compliance_data" not in st.session_state:
        st.session_state.compliance_data = None
    if "selected_req_id" not in st.session_state:
        st.session_state.selected_req_id = None

    # Load Company Profile
    profile = get_company_profile("default_profile")
    if not profile:
        profile = {
            "id": "default_profile",
            "company_name": "ABC Construction Pvt Ltd",
            "annual_turnover": 70000000.0,
            "experience_years": 5.0,
            "gst_available": True,
            "pan_available": True,
            "experience_cert_available": True,
            "completed_projects_count": 12
        }
        save_or_update_company_profile(profile)

    # ----------------- SIDEBAR -----------------
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
        st.markdown("### **TenderGuard**")
        st.caption("AI-Powered Tender Intelligence")

        st.markdown("---")
        st.subheader("1. Document Ingestion")
        
        uploaded_file = st.file_uploader("Upload Tender PDF", type=["pdf"])
        if uploaded_file is not None:
            if st.button("🚀 Process Uploaded Tender", use_container_width=True):
                with st.spinner("Processing PDF, building FAISS index & extracting evidence..."):
                    save_path = UPLOADS_DIR / uploaded_file.name
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    res = process_tender_pdf(str(save_path), uploaded_file.name)
                    st.session_state.current_doc_id = res["document_id"]
                    st.session_state.compliance_data = res["compliance_summary"]
                    st.success(f"Processed {res['total_pages']} pages & found {res['total_requirements']} requirements!")
                    st.rerun()

        st.markdown("**OR**")
        if st.button("⚡ Load 43-Page Demo Tender", use_container_width=True, type="primary"):
            with st.spinner("Generating & indexing PRD-standard 43-page tender..."):
                sample_pdf = generate_demo_tender_pdf()
                res = process_tender_pdf(sample_pdf, "national_highway_tender_43pages.pdf")
                st.session_state.current_doc_id = res["document_id"]
                st.session_state.compliance_data = res["compliance_summary"]
                st.success("Loaded 43-Page Highway Tender Document!")
                st.rerun()

        st.markdown("---")
        st.subheader("2. Company Profile")
        with st.form("company_profile_form"):
            comp_name = st.text_input("Company Name", value=profile["company_name"])
            
            # Turnover in Cr
            turnover_cr = profile["annual_turnover"] / 10_000_000.0
            turnover_input_cr = st.number_input("Annual Turnover (₹ Crore)", min_value=0.0, max_value=500.0, value=float(turnover_cr), step=0.5)
            
            exp_years = st.number_input("Experience (Years)", min_value=0.0, max_value=50.0, value=float(profile["experience_years"]), step=1.0)
            
            gst_cb = st.checkbox("GST Registration Available", value=profile["gst_available"])
            pan_cb = st.checkbox("PAN Card Available", value=profile["pan_available"])
            exp_cert_cb = st.checkbox("Experience Certificates Available", value=profile["experience_cert_available"])
            
            update_btn = st.form_submit_button("🔄 Save & Re-Calculate Compliance", use_container_width=True)
            if update_btn:
                updated_profile = {
                    "id": "default_profile",
                    "company_name": comp_name,
                    "annual_turnover": float(turnover_input_cr * 10_000_000.0),
                    "experience_years": float(exp_years),
                    "gst_available": gst_cb,
                    "pan_available": pan_cb,
                    "experience_cert_available": exp_cert_cb,
                    "completed_projects_count": profile.get("completed_projects_count", 12)
                }
                save_or_update_company_profile(updated_profile)
                if st.session_state.current_doc_id:
                    st.session_state.compliance_data = run_compliance_evaluation(st.session_state.current_doc_id, updated_profile)
                st.success("Company profile saved & compliance re-evaluated!")
                st.rerun()

    # ----------------- MAIN CONTENT -----------------
    st.markdown('<div class="main-header">🛡️ TenderGuard Compliance Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automated requirement extraction, deterministic rule validation, and verifiable page-level evidence citations.</div>', unsafe_allow_html=True)

    if not st.session_state.current_doc_id or not st.session_state.compliance_data:
        st.info("👈 Please upload a Tender PDF or click **'Load 43-Page Demo Tender'** in the sidebar to start compliance analysis.")
        return

    data = st.session_state.compliance_data
    items = data["items"]

    # 1. SUMMARY METRIC CARDS (PRD Section 16)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num">{data["total_requirements"]}</div><div class="kpi-label">Requirements</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color: #16a34a;">{data["passed_count"]}</div><div class="kpi-label">Passed</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color: #dc2626;">{data["missing_count"] + data["failed_count"]}</div><div class="kpi-label">Missing / Fail</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color: #d97706;">{data["ambiguous_count"]}</div><div class="kpi-label">Ambiguous</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color: #2563eb;">{data["action_required_count"]}</div><div class="kpi-label">Action Req.</div></div>', unsafe_allow_html=True)
    with c6:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color: #9333ea;">{data["deadlines_count"]}</div><div class="kpi-label">Deadlines</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # 2. MAIN DUAL-PANE LAYOUT: REQUIREMENTS TABLE + EVIDENCE VIEWER
    left_col, right_col = st.columns([1.1, 0.9])

    with left_col:
        st.subheader("📋 Requirements & Compliance Matrix")
        
        # Filters
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            categories = ["All"] + sorted(list(set(it["category"] for it in items)))
            selected_cat = st.selectbox("Category Filter", categories)
        with f_col2:
            statuses = ["All", "PASS", "FAIL", "ACTION_REQUIRED", "MISSING", "AMBIGUOUS"]
            selected_status = st.selectbox("Status Filter", statuses)

        # Filter items
        filtered_items = items
        if selected_cat != "All":
            filtered_items = [it for it in filtered_items if it["category"] == selected_cat]
        if selected_status != "All":
            filtered_items = [it for it in filtered_items if it["result_status"] == selected_status]

        # Table Display
        table_rows = []
        for it in filtered_items:
            table_rows.append({
                "ID": it["requirement_id"],
                "Category": it["category"],
                "Requirement": it["title"],
                "Status": it["result_status"],
                "Page": f"P. {it['page_number']}"
            })
            
        df = pd.DataFrame(table_rows)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn(
                    "Compliance Status",
                    help="Deterministic result from company profile check"
                )
            }
        )

        # Item Selector for Evidence View
        req_options = {it["requirement_id"]: f"{it['requirement_id']} — {it['title']} ({it['result_status']})" for it in items}
        selected_id = st.selectbox(
            "🔍 Select Requirement to Inspect Verifiable Evidence:",
            options=list(req_options.keys()),
            format_func=lambda x: req_options[x]
        )

    # Selected Requirement Object
    selected_req = next((it for it in items if it["requirement_id"] == selected_id), items[0] if items else None)

    with right_col:
        st.subheader("🔎 Verifiable Evidence Viewer")
        if selected_req:
            # Status Badge Color
            stat = selected_req["result_status"]
            status_color_map = {
                "PASS": "#16a34a",
                "FAIL": "#dc2626",
                "ACTION_REQUIRED": "#2563eb",
                "MISSING": "#dc2626",
                "AMBIGUOUS": "#d97706"
            }
            color = status_color_map.get(stat, "#4b5563")

            st.markdown(f"""
            <div style="border: 1px solid rgba(128,128,128,0.25); border-radius: 8px; padding: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; font-size: 1.25rem;">{selected_req['title']}</h3>
                    <span style="background-color: {color}; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 0.85rem;">{stat}</span>
                </div>
                <p style="color: #64748b; margin: 4px 0 12px 0;"><strong>Category:</strong> {selected_req['category']} | <strong>Source:</strong> Page {selected_req['page_number']} ({selected_req['section_name']})</p>
                <hr style="margin: 8px 0; border: none; border-top: 1px solid rgba(128,128,128,0.15);" />
                
                <p style="margin: 8px 0;"><strong>Requirement Rule:</strong><br/>{selected_req['requirement_text']}</p>
                
                <div class="evidence-box">
                    <strong>📄 Exact Tender Text Evidence (Page {selected_req['page_number']}):</strong><br/>
                    <em>"{selected_req['evidence_text']}"</em>
                </div>
                
                <p style="margin: 8px 0;"><strong>🏢 Company Profile Value:</strong> {selected_req['company_value']}</p>
                <p style="margin: 8px 0;"><strong>⚖️ Deterministic Python Validation:</strong><br/>{selected_req['reason']}</p>
                
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 10px;">
                    Confidence Score: {selected_req['confidence'] * 100:.0f}% | Traceable Source: Page {selected_req['page_number']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. DEADLINES AND AD-HOC VERIFICATION SECTION
    d_col1, d_col2 = st.columns([1, 1])

    with d_col1:
        st.subheader("📅 Extracted Important Deadlines")
        if data["deadlines"]:
            for dl in data["deadlines"]:
                st.markdown(f"""
                <div style="padding: 10px 14px; border: 1px solid rgba(128,128,128,0.2); border-radius: 6px; margin-bottom: 8px;">
                    <strong style="font-size: 1rem;">{dl['title']}</strong> (Page {dl['page_number']})<br/>
                    <span style="color: #2563eb;">{dl['requirement_text']}</span><br/>
                    <small style="color: #64748b;">Evidence: {dl['evidence_text']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No critical dates detected.")

    with d_col2:
        st.subheader("🔍 Ad-Hoc Tender Fact Lookup")
        st.caption("Ask specific questions against the tender index. Unmentioned facts return strict fallback.")
        
        user_query = st.text_input("Enter query (e.g. 'Turnover', 'EMD', 'Drone survey requirement'):")
        if user_query:
            ans = query_tender_evidence(st.session_state.current_doc_id, user_query)
            if ans["found"]:
                st.success(f"{ans['answer']}")
                st.markdown(f"""
                <div class="evidence-box">
                    <strong>Page {ans['page']} — {ans['section']}:</strong><br/>
                    {ans['evidence']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning(f"⚠️ {ans['answer']}")

if __name__ == "__main__":
    render_dashboard()
