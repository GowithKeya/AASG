import streamlit as st
import pandas as pd
import json
from dashboard.api import fetch_events, fetch_approvals, submit_approval, fetch_metrics, trigger_suite, run_task

st.set_page_config(
    page_title="CY-03 Agent Firewall | Taint-Tracking Security",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #262626;
        background-color: #ffffff;
    }
    
    .stApp {
        background-color: #ffffff;
    }
    
    .header-banner {
        background: linear-gradient(135deg, #ff5e1f 0%, #fa4700 100%);
        padding: 28px 32px;
        border-radius: 8px;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(255, 94, 31, 0.2);
    }
    
    .header-title {
        font-size: 28px;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 15px;
        font-weight: 400;
        opacity: 0.92;
        margin-top: 6px;
    }
    
    .metric-card {
        background: #ffffff;
        border: 1px solid #f0f0f0;
        border-radius: 8px;
        padding: 20px 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }
    
    .metric-val {
        font-size: 32px;
        font-weight: 700;
        color: #ff5e1f;
    }
    
    .metric-label {
        font-size: 13px;
        font-weight: 500;
        color: #666666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-allow {
        background-color: #ecfdf5;
        color: #047857;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 12px;
    }
    
    .badge-block {
        background-color: #fef2f2;
        color: #b91c1c;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 12px;
    }
    
    .badge-approval {
        background-color: #fff4ec;
        color: #ff5e1f;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 12px;
    }
    
    .badge-tainted {
        background-color: #fef2f2;
        color: #d92d20;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
    }
    
    .badge-clean {
        background-color: #f0fdf4;
        color: #15803d;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
    }
    
    .stButton>button {
        background-color: #ff5e1f !important;
        color: #ffffff !important;
        border-radius: 9999px !important;
        padding: 8px 24px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton>button:hover {
        background-color: #e04b10 !important;
        box-shadow: 0 4px 12px rgba(255, 94, 31, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <div class="header-title">🛡️ CY-03 Taint-Tracking Agent Firewall</div>
    <div class="header-subtitle">Deterministic tool policy enforcement & data flow tracking for autonomous AI agents</div>
</div>
""", unsafe_allow_html=True)

metrics = fetch_metrics()

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Attack Prevention Rate</div>
        <div class="metric-val">{:.1f}%</div>
    </div>
    """.format(metrics.get("attack_prevention_rate", 0.0) * 100), unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Benign Task Completion</div>
        <div class="metric-val">{:.1f}%</div>
    </div>
    """.format(metrics.get("benign_completion_rate", 0.0) * 100), unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Total Threat Blocks</div>
        <div class="metric-val">{}</div>
    </div>
    """.format(metrics.get("any_block_count", 0)), unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Evaluation Runs</div>
        <div class="metric-val">{}</div>
    </div>
    """.format(metrics.get("total_runs", 0)), unsafe_allow_html=True)

with c5:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Average Latency</div>
        <div class="metric-val">{:.1f}ms</div>
    </div>
    """.format(metrics.get("avg_latency_ms", 0.0)), unsafe_allow_html=True)

tab_bench, tab_events, tab_approvals, tab_sandbox = st.tabs([
    "📊 Red Team Benchmarks",
    "📜 Security Events & Audit Trail",
    "⏳ Pending Human Approvals",
    "🧪 Interactive Sandbox"
])

with tab_bench:
    st.subheader("Red Team Attack & Benign Benchmark Evaluation")
    col_a, col_b = st.columns([1, 3])
    with col_a:
        st.markdown("**Run Automated Benchmark Suite**")
        guard_toggle = st.checkbox("Enable Firewall Guardrails", value=True)
        if st.button("Execute Full Benchmark Suite"):
            with st.spinner("Executing attack and benign test suites..."):
                batch_id = trigger_suite(guard_on=guard_toggle)
                st.success(f"Benchmark finished: {batch_id}")
                st.rerun()

    with col_b:
        by_mode = metrics.get("by_guard_mode", {})
        if by_mode:
            st.markdown("**Comparative Performance Breakdown**")
            summary_data = []
            for m_name, m_data in by_mode.items():
                summary_data.append({
                    "Guardrail Mode": "Firewall Enabled" if m_name == "guard_on" else "Firewall Disabled",
                    "Total Runs": m_data.get("total", 0),
                    "Attack Prevention": f"{m_data.get('attack_prevention_rate', 0.0)*100:.1f}%",
                    "Benign Completion": f"{m_data.get('benign_completion_rate', 0.0)*100:.1f}%",
                    "Interceptions": m_data.get("any_block_count", 0),
                    "Avg Latency": f"{m_data.get('avg_latency_ms', 0.0):.2f} ms"
                })
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

    st.markdown("---")
    runs = metrics.get("runs", [])
    if runs:
        st.markdown(f"**Detailed Evaluation Run Records ({len(runs)} items)**")
        df_runs = pd.DataFrame(runs)
        cols_to_show = ["id", "batch_id", "item_id", "kind", "guard_mode", "attack_succeeded", "task_completed", "any_block", "latency_ms"]
        available_cols = [c for c in cols_to_show if c in df_runs.columns]
        st.dataframe(df_runs[available_cols], use_container_width=True)
    else:
        st.info("No benchmark runs recorded yet. Click 'Execute Full Benchmark Suite' above to populate.")

with tab_events:
    st.subheader("Real-Time Security Event Stream")
    events = fetch_events()
    if events:
        table_rows = []
        for e in events:
            dec = e.get("decision") or {}
            app = e.get("approval") or {}
            verdict_val = dec.get("verdict", "N/A")
            table_rows.append({
                "Event ID": e.get("id"),
                "Timestamp": e.get("ts"),
                "Type": e.get("type"),
                "Tool": e.get("tool") or "-",
                "Trust": e.get("trust") or "-",
                "Sensitivity": e.get("sensitivity") or "-",
                "Verdict": verdict_val,
                "Rule": dec.get("rule_id", "-"),
                "Explanation": dec.get("explanation", "-"),
                "Approval": app.get("status", "-")
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True)
    else:
        st.info("No security events logged yet.")

with tab_approvals:
    st.subheader("Human-In-The-Loop Pending Approvals")
    approvals = fetch_approvals()
    if approvals:
        for app in approvals:
            with st.container():
                st.markdown(f"""
                <div style="border: 1px solid #ff5e1f; border-radius: 8px; padding: 16px; margin-bottom: 12px; background: #fffcfb;">
                    <div style="font-weight: 700; font-size: 16px; color: #ff5e1f;">⚠️ Approval Request #{app['id']} — Tool: <code>{app['tool']}</code></div>
                    <div style="margin-top: 8px; color: #262626;"><b>Reason:</b> {app['explanation']}</div>
                    <div style="margin-top: 4px; color: #555555; font-size: 13px;"><b>Arguments:</b> <code>{json.dumps(app.get('args', {}))}</code></div>
                    <div style="margin-top: 4px; color: #777777; font-size: 12px;">Session: {app['session_id']} | Created: {app['created_at']}</div>
                </div>
                """, unsafe_allow_html=True)
                col_y, col_n = st.columns([1, 6])
                with col_y:
                    if st.button(f"Approve #{app['id']}", key=f"app_{app['id']}"):
                        submit_approval(app['id'], True)
                        st.success(f"Approved #{app['id']}")
                        st.rerun()
                with col_n:
                    if st.button(f"Deny #{app['id']}", key=f"deny_{app['id']}"):
                        submit_approval(app['id'], False)
                        st.error(f"Denied #{app['id']}")
                        st.rerun()
    else:
        st.success("All pending actions resolved. Zero approvals waiting.")

with tab_sandbox:
    st.subheader("Interactive Agent Firewall Sandbox")
    st.write("Run an agent instruction with custom documents and inspect firewall behavior.")

    sand_col1, sand_col2 = st.columns([2, 1])
    with sand_col1:
        task_input = st.text_area(
            "Agent Task Prompt:",
            value="Read doc_injection_email.txt and proceed."
        )
        doc_input = st.selectbox(
            "Attach Document (optional):",
            options=["None", "doc_benign_summary.txt", "doc_injection_email.txt", "doc_injection_leak.txt", "doc_injection_unauth.txt", "doc_confidential_memo.txt"]
        )

    with sand_col2:
        st.markdown("**Firewall Configuration**")
        sandbox_guard = st.toggle("Enable Taint-Tracking Firewall", value=True)
        st.markdown("""
        - 🛡️ Ingestion Inspection: Active
        - 🏷️ Dynamic Taint Tracking: Active
        - 🔒 Outbound Exfiltration Shield: Active
        """)

    if st.button("Run Agent in Sandbox"):
        doc_arg = None if doc_input == "None" else doc_input
        with st.spinner("Agent running with security layer..."):
            result = run_task(task=task_input, guard_on=sandbox_guard, doc=doc_arg)
            st.markdown(f"**Session ID:** `{result.session_id}` | **Latency:** `{result.latency_ms:.2f}ms` | **Tainted:** `{result.tainted}`")
            
            st.markdown("### Executed Tool Calls & Verdicts")
            if result.executed_calls:
                for idx, call in enumerate(result.executed_calls, 1):
                    v = call.verdict
                    action = v.action if v else "ALLOW"
                    border_color = "#10b981" if action == "ALLOW" else ("#ef4444" if action == "BLOCK" else "#f59e0b")
                    st.markdown(f"""
                    <div style="border-left: 4px solid {border_color}; padding: 12px 16px; margin-bottom: 10px; background: #f9fafb; border-radius: 4px;">
                        <div style="font-weight: 600;">#{idx} Tool: <code>{call.tool}</code> | Verdict: <b>{action}</b> ({v.rule_id if v else 'none'}) | Executed: <b>{call.executed}</b></div>
                        <div style="margin-top: 4px; font-size: 13px;"><b>Args:</b> <code>{json.dumps(call.args)}</code></div>
                        <div style="margin-top: 4px; font-size: 13px;"><b>Explanation:</b> {v.explanation if v else 'Executed directly.'}</div>
                        <div style="margin-top: 4px; font-size: 12px; color: #4b5563;"><b>Output:</b> {call.output}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No tool calls were generated for this task.")

            st.markdown("### Final Agent Output")
            st.info(result.final_output)
