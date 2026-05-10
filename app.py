import streamlit as st
import sys
import io
import threading
import queue
import time
from contextlib import redirect_stdout

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f;
    color: #e8e6f0;
    font-family: 'IBM Plex Sans', sans-serif;
}

[data-testid="stAppViewContainer"] > .main {
    background: #0a0a0f;
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1100px; }

/* ── Hero Header ── */
.hero {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
    position: relative;
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 300px;
    background: radial-gradient(ellipse at center, rgba(139,92,246,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.hero-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #8b5cf6;
    margin-bottom: 1rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.8rem, 6vw, 4.5rem);
    font-weight: 800;
    line-height: 1.05;
    background: linear-gradient(135deg, #e8e6f0 30%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.8rem;
}
.hero-sub {
    font-size: 1.05rem;
    color: #6b6880;
    font-weight: 300;
    letter-spacing: 0.02em;
}

/* ── Input Card ── */
.input-card {
    background: #13121a;
    border: 1px solid #1e1c2a;
    border-radius: 16px;
    padding: 2rem;
    margin: 2rem 0;
    position: relative;
    overflow: hidden;
}
.input-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #8b5cf6, transparent);
}

/* ── Streamlit input overrides ── */
[data-testid="stTextInput"] input,
.stTextInput input {
    background: #0d0c14 !important;
    border: 1px solid #2a2838 !important;
    border-radius: 10px !important;
    color: #e8e6f0 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.85rem 1.1rem !important;
    transition: border-color 0.2s;
}
[data-testid="stTextInput"] input:focus {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.12) !important;
}
[data-testid="stTextInput"] label {
    color: #9896a8 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #8b5cf6) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    padding: 0.8rem 2.2rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 20px rgba(139,92,246,0.3) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6d28d9, #7c3aed) !important;
    box-shadow: 0 6px 28px rgba(139,92,246,0.45) !important;
    transform: translateY(-1px) !important;
}

/* ── Pipeline Steps ── */
.pipeline-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 2rem 0;
}
@media (max-width: 768px) {
    .pipeline-grid { grid-template-columns: repeat(2, 1fr); }
}
.step-card {
    background: #13121a;
    border: 1px solid #1e1c2a;
    border-radius: 12px;
    padding: 1.1rem 1rem;
    text-align: center;
    position: relative;
    transition: all 0.3s;
}
.step-card.active {
    border-color: #8b5cf6;
    background: #16142a;
    box-shadow: 0 0 20px rgba(139,92,246,0.2);
}
.step-card.done {
    border-color: #10b981;
    background: #0d1a14;
}
.step-card.error {
    border-color: #ef4444;
    background: #1a0d0d;
}
.step-icon {
    font-size: 1.6rem;
    margin-bottom: 0.4rem;
}
.step-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #4a4858;
    margin-bottom: 0.25rem;
}
.step-name {
    font-family: 'Syne', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    color: #c4c2d4;
}
.step-status {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    margin-top: 0.35rem;
}
.step-card.active .step-status { color: #a78bfa; }
.step-card.done .step-status { color: #10b981; }
.step-card.error .step-status { color: #ef4444; }
.step-card.idle .step-status { color: #4a4858; }

/* ── Result Sections ── */
.result-section {
    background: #13121a;
    border: 1px solid #1e1c2a;
    border-radius: 14px;
    margin: 1.2rem 0;
    overflow: hidden;
}
.result-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.4rem;
    border-bottom: 1px solid #1e1c2a;
    background: #0f0e18;
}
.result-header-icon { font-size: 1.1rem; }
.result-header-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    color: #c4c2d4;
}
.result-header-badge {
    margin-left: auto;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    padding: 0.25rem 0.65rem;
    border-radius: 20px;
    background: rgba(139,92,246,0.12);
    color: #8b5cf6;
    text-transform: uppercase;
}
.result-body {
    padding: 1.4rem;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.9rem;
    line-height: 1.75;
    color: #b0adc0;
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Final Report ── */
.report-wrapper {
    background: #0f0e18;
    border: 1px solid #2a2838;
    border-radius: 16px;
    overflow: hidden;
    margin-top: 1.5rem;
}
.report-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
    background: #13121a;
    border-bottom: 1px solid #1e1c2a;
}
.report-topbar-left {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #e8e6f0;
}
.report-topbar-badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    background: rgba(16,185,129,0.15);
    color: #10b981;
    text-transform: uppercase;
}

/* ── Feedback Card ── */
.feedback-card {
    background: #13121a;
    border-left: 3px solid #f59e0b;
    border-radius: 0 12px 12px 0;
    padding: 1.2rem 1.4rem;
    margin-top: 1.2rem;
}
.feedback-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #f59e0b;
    margin-bottom: 0.6rem;
}
.feedback-text {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.88rem;
    line-height: 1.7;
    color: #b0adc0;
    white-space: pre-wrap;
}

/* ── Divider ── */
.fancy-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #2a2838, transparent);
    margin: 2rem 0;
}

/* ── Spinner Override ── */
[data-testid="stSpinner"] { color: #8b5cf6 !important; }

/* ── Error Box ── */
[data-testid="stAlert"] {
    background: #1a0d0d !important;
    border: 1px solid #ef4444 !important;
    border-radius: 10px !important;
    color: #fca5a5 !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #13121a !important;
    border: 1px solid #1e1c2a !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
    color: #9896a8 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* ── Footer ── */
.footer {
    text-align: center;
    margin-top: 4rem;
    padding-top: 2rem;
    border-top: 1px solid #1e1c2a;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #3a3848;
    letter-spacing: 0.1em;
}
</style>
""", unsafe_allow_html=True)


# ── Session State Init ────────────────────────────────────────────────────────
for key in ["result", "running", "error"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "running" else False


# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-label">⬡ Multi-Agent Research System</div>
    <div class="hero-title">ResearchMind</div>
    <div class="hero-sub">Four specialized agents. One definitive report.</div>
</div>
""", unsafe_allow_html=True)


# ── Input Area ───────────────────────────────────────────────────────────────
st.markdown('<div class="input-card">', unsafe_allow_html=True)

col1, col2 = st.columns([5, 1.2])
with col1:
    topic = st.text_input(
        "RESEARCH TOPIC",
        placeholder="e.g. The impact of AI on drug discovery in 2025",
        disabled=st.session_state.running,
        label_visibility="visible",
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button(
        "▶ Run Pipeline",
        disabled=st.session_state.running or not topic,
        use_container_width=True,
    )

st.markdown('</div>', unsafe_allow_html=True)


# ── Pipeline Step Tracker ─────────────────────────────────────────────────────
def render_steps(active: int = -1, done_up_to: int = -1, error_at: int = -1):
    steps = [
        ("🔍", "Search Agent",  "Finds sources"),
        ("📄", "Reader Agent",  "Scrapes content"),
        ("✍️", "Writer Agent",  "Drafts report"),
        ("🧠", "Critic Agent",  "Reviews quality"),
    ]
    cards = ""
    for i, (icon, name, tagline) in enumerate(steps):
        if error_at == i:
            cls, status = "error", "✕ failed"
        elif i < done_up_to:
            cls, status = "done", "✓ complete"
        elif i == active:
            cls, status = "active", "● working…"
        else:
            cls, status = "idle", "○ waiting"
        cards += f"""
        <div class="step-card {cls}">
            <div class="step-icon">{icon}</div>
            <div class="step-num">Step {i+1}</div>
            <div class="step-name">{name}</div>
            <div class="step-status">{status}</div>
        </div>"""

    st.markdown(f'<div class="pipeline-grid">{cards}</div>', unsafe_allow_html=True)


step_placeholder = st.empty()

# initial idle state
with step_placeholder:
    render_steps()


# ── Run Pipeline ──────────────────────────────────────────────────────────────
if run_btn and topic:
    st.session_state.running = True
    st.session_state.result = None
    st.session_state.error = None

    try:
        from pipeline import run_research_pipeline

        # Step 1 — Search
        with step_placeholder:
            render_steps(active=0, done_up_to=0)

        search_placeholder = st.empty()
        with search_placeholder:
            with st.spinner("Search agent is scouting the web…"):
                # We'll capture state step by step by calling components individually
                pass

        # Import individual building blocks
        from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

        state = {}

        # ── Step 1: Search ────────────────────────────────────────────
        with step_placeholder:
            render_steps(active=0, done_up_to=0)

        search_status = st.empty()
        with search_status:
            with st.spinner("🔍 Search agent scouting…"):
                search_agent = build_search_agent()
                search_result = search_agent.invoke({
                    "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
                })
                state["search_result"] = search_result["messages"][-1].content

        search_status.empty()
        with step_placeholder:
            render_steps(active=1, done_up_to=1)

        st.markdown("""
        <div class="result-section">
            <div class="result-header">
                <span class="result-header-icon">🔍</span>
                <span class="result-header-title">Search Results</span>
                <span class="result-header-badge">Step 1 · Complete</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("View raw search output", expanded=False):
            st.markdown(f'<div class="result-body">{state["search_result"]}</div>', unsafe_allow_html=True)

        # ── Step 2: Reader ────────────────────────────────────────────
        reader_status = st.empty()
        with reader_status:
            with st.spinner("📄 Reader agent scraping top sources…"):
                reader_agent = build_reader_agent()
                reader_result = reader_agent.invoke({
                    "messages": [(
                        "user",
                        f"Based on the following search results about '{topic}', "
                        f"pick the most relevant URL and scrape it for deeper content.\n\n"
                        f"Search Results:\n{state['search_result'][:800]}"
                    )]
                })
                state["scraped_content"] = reader_result["messages"][-1].content

        reader_status.empty()
        with step_placeholder:
            render_steps(active=2, done_up_to=2)

        st.markdown("""
        <div class="result-section">
            <div class="result-header">
                <span class="result-header-icon">📄</span>
                <span class="result-header-title">Scraped Content</span>
                <span class="result-header-badge">Step 2 · Complete</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("View raw scraped output", expanded=False):
            st.markdown(f'<div class="result-body">{state["scraped_content"]}</div>', unsafe_allow_html=True)

        # ── Step 3: Writer ────────────────────────────────────────────
        writer_status = st.empty()
        with writer_status:
            with st.spinner("✍️ Writer agent composing the report…"):
                research_combined = (
                    f"SEARCH RESULTS:\n{state['search_result']}\n\n"
                    f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
                )
                state["report"] = writer_chain.invoke({
                    "topic": topic,
                    "research": research_combined
                })

        writer_status.empty()
        with step_placeholder:
            render_steps(active=3, done_up_to=3)

        # ── Step 4: Critic ────────────────────────────────────────────
        critic_status = st.empty()
        with critic_status:
            with st.spinner("🧠 Critic agent reviewing quality…"):
                state["feedback"] = critic_chain.invoke({
                    "report": state["report"]
                })

        critic_status.empty()
        with step_placeholder:
            render_steps(active=-1, done_up_to=4)

        # ── Final Results ─────────────────────────────────────────────
        st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="report-wrapper">
            <div class="report-topbar">
                <span class="report-topbar-left">📋 Final Research Report</span>
                <span class="report-topbar-badge">✓ Pipeline Complete</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f'<div class="result-body" style="background:#0f0e18;border:1px solid #1e1c2a;border-radius:0 0 14px 14px;padding:1.6rem;">{state["report"]}</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="feedback-card">
            <div class="feedback-label">🧠 Critic's Feedback</div>
            <div class="feedback-text">{state["feedback"]}</div>
        </div>
        """, unsafe_allow_html=True)

        st.session_state.result = state

    except ImportError as e:
        with step_placeholder:
            render_steps(error_at=0)
        st.error(f"**Import Error:** Could not load pipeline modules.\n\n`{e}`\n\nMake sure `pipeline.py` and `agents.py` are in the same directory as `app.py`.")
    except Exception as e:
        with step_placeholder:
            render_steps(error_at=0)
        st.error(f"**Pipeline Error:** {e}")
    finally:
        st.session_state.running = False


# ── Previous Result (if re-render without re-run) ────────────────────────────
elif st.session_state.result and not st.session_state.running:
    state = st.session_state.result
    with step_placeholder:
        render_steps(done_up_to=4)

    with st.expander("🔍 Search Results", expanded=False):
        st.markdown(f'<div class="result-body">{state["search_result"]}</div>', unsafe_allow_html=True)
    with st.expander("📄 Scraped Content", expanded=False):
        st.markdown(f'<div class="result-body">{state["scraped_content"]}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="report-wrapper">
        <div class="report-topbar">
            <span class="report-topbar-left">📋 Final Research Report</span>
            <span class="report-topbar-badge">✓ Complete</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f'<div class="result-body" style="background:#0f0e18;border:1px solid #1e1c2a;border-radius:0 0 14px 14px;padding:1.6rem;">{state["report"]}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="feedback-card">
        <div class="feedback-label">🧠 Critic's Feedback</div>
        <div class="feedback-text">{state["feedback"]}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    ResearchMind · Multi-Agent Pipeline · Search → Read → Write → Critique
</div>
""", unsafe_allow_html=True)