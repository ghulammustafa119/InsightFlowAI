"""
Autonomous Insight-to-Action AI Agent — Streamlit UI

Mobile-first, hackathon-ready dashboard demonstrating the full agentic pipeline:
INPUT → INSIGHT → CONFLICT → DECISION → ACTION → SIMULATION → OUTCOME
"""
import json
import os
import streamlit as st
import pandas as pd
from engine.analyzer import Analyzer
from engine.planner import Planner
from engine.simulator import Simulator
from engine.logger import AgentLogger

# ── page config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agentic AI — Insight to Action",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── custom CSS — mobile-first, dark premium ──────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 40%, #16213e 100%);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: #0d0d1a; }
h1, h2, h3, h4 { color: #e0e0ff !important; }
.block-container { padding: 1rem 1.2rem !important; max-width: 1100px; }

/* metric cards */
.metric-card {
    background: linear-gradient(145deg, rgba(30,30,60,0.9), rgba(20,20,45,0.95));
    border: 1px solid rgba(120,120,255,0.15);
    border-radius: 16px; padding: 1.2rem; margin: 0.4rem 0;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(80,80,200,0.25); }
.metric-label { font-size: 0.75rem; color: #8888cc; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }
.metric-value { font-size: 1.6rem; font-weight: 800; margin-top: 4px; }
.metric-value.critical { color: #ff4d6a; }
.metric-value.warn { color: #ffb347; }
.metric-value.good { color: #47ffb3; }
.metric-value.info { color: #47b3ff; }

/* insight cards */
.insight-card {
    background: rgba(25,25,55,0.85); border-left: 4px solid #6c63ff;
    border-radius: 0 12px 12px 0; padding: 1rem 1.2rem; margin: 0.6rem 0;
}
.insight-card.critical { border-left-color: #ff4d6a; }
.insight-card.high { border-left-color: #ffb347; }
.insight-card.medium { border-left-color: #47b3ff; }
.insight-title { font-weight: 700; font-size: 1rem; color: #e0e0ff; }
.insight-detail { font-size: 0.85rem; color: #a0a0cc; margin-top: 4px; }
.severity-badge {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
}
.severity-badge.critical { background: rgba(255,77,106,0.2); color: #ff4d6a; }
.severity-badge.high { background: rgba(255,179,71,0.2); color: #ffb347; }
.severity-badge.medium { background: rgba(71,179,255,0.2); color: #47b3ff; }
.severity-badge.low { background: rgba(71,255,179,0.2); color: #47ffb3; }

/* action plan cards */
.action-card {
    background: rgba(25,25,55,0.85); border: 1px solid rgba(120,120,255,0.15);
    border-radius: 12px; padding: 1rem; margin: 0.5rem 0;
}
.action-step { font-size: 0.7rem; font-weight: 800; color: #6c63ff; text-transform: uppercase; letter-spacing: 2px; }
.action-title { font-size: 1rem; font-weight: 700; color: #e0e0ff; margin-top: 2px; }
.action-desc { font-size: 0.82rem; color: #9090bb; margin-top: 4px; }
.action-meta { font-size: 0.72rem; color: #7070aa; margin-top: 6px; }

/* status dots */
.status-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }
.status-dot.success { background: #47ffb3; box-shadow: 0 0 8px #47ffb3; }
.status-dot.recovered { background: #ffb347; box-shadow: 0 0 8px #ffb347; }
.status-dot.deferred { background: #666; }
.status-dot.failed { background: #ff4d6a; box-shadow: 0 0 8px #ff4d6a; }

/* log entries */
.log-entry {
    background: rgba(15,15,35,0.9); border: 1px solid rgba(80,80,160,0.2);
    border-radius: 10px; padding: 0.8rem 1rem; margin: 0.5rem 0;
    font-size: 0.8rem;
}
.log-phase { font-weight: 700; color: #6c63ff; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 1.5px; }
.log-field-label { color: #7070aa; font-weight: 600; }
.log-field-value { color: #c0c0ee; }
.log-failure { color: #ff4d6a; }
.log-recovery { color: #47ffb3; }

/* section headers */
.section-header {
    font-size: 1.3rem; font-weight: 800; color: #e0e0ff;
    border-bottom: 2px solid rgba(108,99,255,0.4);
    padding-bottom: 0.5rem; margin: 1.5rem 0 0.8rem 0;
}
.section-icon { margin-right: 8px; }

/* hero */
.hero-container {
    text-align: center; padding: 1.5rem 0.5rem 1rem;
}
.hero-title {
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(135deg, #6c63ff 0%, #47b3ff 50%, #47ffb3 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1.2;
}
.hero-sub { font-size: 0.9rem; color: #8888bb; margin-top: 0.5rem; }
.pipeline-flow {
    display: flex; flex-wrap: wrap; justify-content: center; gap: 4px;
    margin-top: 0.8rem; font-size: 0.72rem; font-weight: 600; color: #6c63ff;
}
.pipeline-flow span { background: rgba(108,99,255,0.12); padding: 4px 10px; border-radius: 20px; }

/* comparison table */
.cmp-better { color: #47ffb3; font-weight: 700; }
.cmp-worse { color: #ff4d6a; font-weight: 700; }
.cmp-neutral { color: #8888bb; }
</style>
""", unsafe_allow_html=True)

# ── hero ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-title">Autonomous Insight-to-Action<br/>AI Agent</div>
    <div class="hero-sub">Agentic Decision System — Hackathon Demo</div>
    <div class="pipeline-flow">
        <span>📥 INPUT</span><span>→</span>
        <span>🔍 INSIGHT</span><span>→</span>
        <span>⚡ CONFLICT</span><span>→</span>
        <span>🧠 DECISION</span><span>→</span>
        <span>🎯 ACTION</span><span>→</span>
        <span>🔄 SIMULATION</span><span>→</span>
        <span>📊 OUTCOME</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── state init ───────────────────────────────────────────────────────
for key in ("data", "analysis", "plan_result", "sim_result", "logs", "run_complete"):
    if key not in st.session_state:
        st.session_state[key] = None

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "inputs.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")


# ── helpers ──────────────────────────────────────────────────────────
def _metric_card(label: str, value: str, css_class: str = "info"):
    return f"""<div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {css_class}">{value}</div>
    </div>"""


def _insight_html(ins: dict) -> str:
    sev = ins.get("severity", "low")
    return f"""<div class="insight-card {sev}">
        <span class="severity-badge {sev}">{sev}</span>
        <div class="insight-title">{ins['title']}</div>
        <div class="insight-detail">{ins['detail']}</div>
        <div style="margin-top:6px;font-size:0.72rem;color:#6060aa;">Confidence: {ins.get('confidence',0):.0%} · Source: {ins.get('source','')}</div>
    </div>"""


def _action_html(act: dict) -> str:
    status = act.get("status", "approved")
    status_color = "#47ffb3" if status == "approved" else "#666"
    return f"""<div class="action-card">
        <div class="action-step">Step {act['step']} · {act.get('type','')}</div>
        <div class="action-title">{act['title']}</div>
        <div class="action-desc">{act['description']}</div>
        <div class="action-meta">
            ⏱ {act.get('estimated_time_hours',0)}h · 💰 ${act.get('estimated_cost_usd',0):,.0f} ·
            🎯 {act.get('success_probability',0):.0%} ·
            <span style="color:{status_color};font-weight:700;">{status.upper()}</span>
        </div>
    </div>"""


def _sim_result_html(r: dict) -> str:
    s = r.get("status", "")
    dot_class = s if s in ("success", "recovered", "deferred") else "failed"
    html = f"""<div class="action-card">
        <div><span class="status-dot {dot_class}"></span><strong style="color:#e0e0ff;">Step {r['step']}: {r['title']}</strong></div>
        <div style="font-size:0.82rem;color:#9090bb;margin-top:4px;">Status: <span style="font-weight:700;">{s.upper()}</span></div>"""
    if r.get("failure"):
        html += f'<div style="font-size:0.8rem;color:#ff4d6a;margin-top:4px;">⚠ {r["failure"]}</div>'
    if r.get("recovery"):
        html += f'<div style="font-size:0.8rem;color:#47ffb3;margin-top:2px;">↩ {r["recovery"]}</div>'
    html += "</div>"
    return html


def _log_html(entry: dict) -> str:
    parts = [f'<div class="log-entry"><div class="log-phase">⬡ {entry["phase"]} · Step {entry["step"]}</div>']
    for field in ("observation", "reasoning", "decision", "action", "result"):
        val = entry.get(field, "")
        if val:
            parts.append(f'<div><span class="log-field-label">{field.title()}:</span> <span class="log-field-value">{val}</span></div>')
    if entry.get("failure"):
        parts.append(f'<div class="log-failure">⚠ Failure: {entry["failure"]}</div>')
    if entry.get("recovery"):
        parts.append(f'<div class="log-recovery">↩ Recovery: {entry["recovery"]}</div>')
    parts.append("</div>")
    return "".join(parts)


# =====================================================================
# SECTION 1 — Load / Upload Data
# =====================================================================
st.markdown('<div class="section-header"><span class="section-icon">📥</span>Data Ingestion</div>', unsafe_allow_html=True)

upload = st.file_uploader("Upload custom inputs.json (or use built-in sample)", type=["json"])
col_load, col_info = st.columns([1, 2])
with col_load:
    if st.button("🚀 Load Sample Data", use_container_width=True):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            st.session_state.data = json.load(f)
        st.session_state.analysis = None
        st.session_state.plan_result = None
        st.session_state.sim_result = None
        st.session_state.logs = None
        st.session_state.run_complete = None

if upload is not None:
    st.session_state.data = json.load(upload)
    st.session_state.analysis = None
    st.session_state.plan_result = None
    st.session_state.sim_result = None
    st.session_state.logs = None
    st.session_state.run_complete = None

data = st.session_state.data
if data:
    with col_info:
        sources = data.get("data_sources", {})
        st.markdown(
            f"**Scenario:** {data.get('scenario', 'N/A')}  \n"
            f"**Sources loaded:** {', '.join(sources.keys())}  \n"
            f"**Timestamp:** {data.get('timestamp', '')}",
        )
    with st.expander("📋 Raw Input Data"):
        st.json(data)

# =====================================================================
# SECTION 2–7 — Full Pipeline (runs on button click)
# =====================================================================
if data:
    st.markdown('<div class="section-header"><span class="section-icon">⚙️</span>Agent Pipeline</div>', unsafe_allow_html=True)
    if st.button("🧠 Run Full Agent Pipeline", type="primary", use_container_width=True):
        logger = AgentLogger(os.path.join(OUTPUT_DIR, "logs.json"))
        run_id = logger.start_run()

        logger.log(
            phase="ingestion",
            observation=f"Loaded scenario '{data.get('scenario','')}' with {len(data.get('data_sources',{}))} sources",
            reasoning="All sources available. Proceeding to analysis.",
            decision="Begin multi-source analysis",
            action="Pass data to Analyzer",
            result="Data ingested successfully",
        )

        # ── Analysis ─────────────────────────────────────────────
        with st.spinner("🔍 Analyzing data sources..."):
            analyzer = Analyzer(logger)
            analysis = analyzer.run(data)
            st.session_state.analysis = analysis

        # ── Planning ─────────────────────────────────────────────
        with st.spinner("🧠 Generating action plan..."):
            planner = Planner(logger)
            constraints = data.get("data_sources", {}).get("financial_constraints", {})
            plan_result = planner.run(analysis, constraints)
            st.session_state.plan_result = plan_result

        # ── Simulation ───────────────────────────────────────────
        with st.spinner("🔄 Simulating execution..."):
            simulator = Simulator(logger)
            sim_result = simulator.run(plan_result["plan"], data)
            st.session_state.sim_result = sim_result

        # ── Save outputs ─────────────────────────────────────────
        logger.log(
            phase="output",
            observation="All pipeline stages complete",
            reasoning="Results and logs ready for persistence.",
            decision="Save outputs to disk",
            action="Write logs.json and results.json",
            result="Files saved",
        )
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        logger.save()
        with open(os.path.join(OUTPUT_DIR, "results.json"), "w", encoding="utf-8") as f:
            json.dump({"analysis": analysis, "plan": plan_result, "simulation": sim_result}, f, indent=2, default=str)

        st.session_state.logs = logger.get_traces()
        st.session_state.run_complete = True
        st.rerun()

# ── Render results if available ──────────────────────────────────────
analysis = st.session_state.analysis
plan_result = st.session_state.plan_result
sim_result = st.session_state.sim_result
logs = st.session_state.logs

if analysis:
    # ── Insights ─────────────────────────────────────────────────
    st.markdown('<div class="section-header"><span class="section-icon">🔍</span>Extracted Insights</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown(_metric_card("Insights", str(len(analysis["insights"])), "info"), unsafe_allow_html=True)
    c2.markdown(_metric_card("Contradictions", str(len(analysis["contradictions"])), "critical"), unsafe_allow_html=True)
    c3.markdown(_metric_card("Confidence", f"{analysis['confidence']:.0%}", "good" if analysis["confidence"] > 0.8 else "warn"), unsafe_allow_html=True)

    for ins in analysis["insights"]:
        st.markdown(_insight_html(ins), unsafe_allow_html=True)

    # ── Trends ───────────────────────────────────────────────────
    if analysis.get("trends"):
        st.markdown('<div class="section-header"><span class="section-icon">📈</span>Detected Trends</div>', unsafe_allow_html=True)
        for t in analysis["trends"]:
            arrow = "🔻" if t["direction"] == "down" else "🔺"
            st.markdown(f"**{arrow} {t['title']}** — {t['magnitude']} {t['unit']}")

    # ── Contradictions / Conflicts ───────────────────────────────
    st.markdown('<div class="section-header"><span class="section-icon">⚡</span>Detected Conflicts</div>', unsafe_allow_html=True)
    if analysis["contradictions"]:
        for con in analysis["contradictions"]:
            sev = con.get("severity", "medium")
            st.markdown(
                f"""<div class="insight-card {sev}">
                    <span class="severity-badge {sev}">{sev}</span>
                    <div class="insight-title">{con['title']}</div>
                    <div class="insight-detail">{con['detail']}</div>
                    <div style="margin-top:4px;font-size:0.72rem;color:#6060aa;">Sources: {', '.join(con.get('sources',[]))}</div>
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.info("No contradictions detected.")

if plan_result:
    # ── Action Plan ──────────────────────────────────────────────
    st.markdown('<div class="section-header"><span class="section-icon">🎯</span>Action Plan</div>', unsafe_allow_html=True)
    ca = plan_result["constraints_applied"]
    c1, c2, c3 = st.columns(3)
    c1.markdown(_metric_card("Budget Allocated", f"${ca['allocated_usd']:,.0f}", "warn"), unsafe_allow_html=True)
    c2.markdown(_metric_card("Budget Remaining", f"${ca['remaining_usd']:,.0f}", "good"), unsafe_allow_html=True)
    c3.markdown(_metric_card("Max Acceptable Loss", f"${ca['max_acceptable_loss_usd']:,.0f}", "info"), unsafe_allow_html=True)
    st.markdown(f"*{plan_result['rationale']}*")
    for act in plan_result["plan"]:
        st.markdown(_action_html(act), unsafe_allow_html=True)

if sim_result:
    # ── Simulation Results ───────────────────────────────────────
    st.markdown('<div class="section-header"><span class="section-icon">🔄</span>Simulation Results</div>', unsafe_allow_html=True)
    for r in sim_result["action_results"]:
        st.markdown(_sim_result_html(r), unsafe_allow_html=True)

    # ── Before vs After ──────────────────────────────────────────
    st.markdown('<div class="section-header"><span class="section-icon">📊</span>Before vs After</div>', unsafe_allow_html=True)
    before = sim_result["before"]
    after = sim_result["after"]
    rows = []
    for key in before:
        b_val = before[key]
        a_val = after[key]
        if isinstance(b_val, bool):
            change = "✅ Activated" if a_val and not b_val else ("—" if a_val == b_val else "Changed")
            rows.append({"Metric": key.replace("_", " ").title(), "Before": str(b_val), "After": str(a_val), "Change": change})
        elif isinstance(b_val, (int, float)):
            diff = round(a_val - b_val, 2)
            a_display = round(a_val, 2)
            b_display = round(b_val, 2)
            if "usd" in key:
                change = f"${diff:+,.0f}"
                b_str = f"${b_display:,.0f}"
                a_str = f"${a_display:,.0f}"
            elif "pct" in key or "rate" in key:
                change = f"{diff:+.1f}pp"
                b_str = f"{b_display}"
                a_str = f"{a_display}"
            else:
                change = f"{diff:+.2f}" if isinstance(b_val, float) else f"{int(diff):+d}"
                b_str = f"{b_display}"
                a_str = f"{a_display}"
            rows.append({"Metric": key.replace("_", " ").title(), "Before": b_str, "After": a_str, "Change": change})
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

if logs:
    # ── Agent Reasoning Trace ────────────────────────────────────
    st.markdown('<div class="section-header"><span class="section-icon">🧾</span>Agent Reasoning Trace (Antigravity Logs)</div>', unsafe_allow_html=True)
    st.caption(f"{len(logs)} trace entries recorded")
    phase_filter = st.multiselect("Filter by phase", options=sorted({l["phase"] for l in logs}), default=sorted({l["phase"] for l in logs}))
    filtered = [l for l in logs if l["phase"] in phase_filter]
    for entry in filtered:
        st.markdown(_log_html(entry), unsafe_allow_html=True)

    with st.expander("📄 Raw Logs JSON"):
        st.json(logs)

# ── footer ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#5555aa;font-size:0.75rem;">'
    'Autonomous Insight-to-Action AI Agent · Built for Hackathon Demo · 2026'
    '</div>',
    unsafe_allow_html=True,
)
