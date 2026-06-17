"""
AI Resume Analyzer — Main Application
======================================
A production-quality Streamlit web app that leverages Google Gemini AI
to provide comprehensive resume analysis against job descriptions.

Author: AI Engineer Portfolio Project
Version: 1.0.0
"""

import streamlit as st
import time
import json
from pathlib import Path

from utils.pdf_extractor import extract_text_from_pdf
from utils.gemini_analyzer import analyze_resume
from utils.report_generator import generate_pdf_report
from utils.visualizations import (
    render_score_card,
    render_skill_gap_chart,
    render_keyword_heatmap,
    render_section_feedback,
)

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
def load_css():
    st.markdown("""
    <style>
    /* ── Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;700&display=swap');

    /* ── Root variables ── */
    :root {
        --bg-primary: #0A0F1E;
        --bg-card: #111827;
        --bg-card-hover: #1a2235;
        --accent: #6366F1;
        --accent-light: #818CF8;
        --accent-glow: rgba(99, 102, 241, 0.15);
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --text-primary: #F9FAFB;
        --text-secondary: #9CA3AF;
        --text-muted: #6B7280;
        --border: rgba(99, 102, 241, 0.2);
    }

    /* ── Base ── */
    .stApp {
        background: var(--bg-primary) !important;
        font-family: 'Inter', sans-serif;
    }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 2rem 3rem !important; max-width: 1400px; }

    /* ── Hero header ── */
    .hero-header {
        text-align: center;
        padding: 3.5rem 2rem 2rem;
        background: radial-gradient(ellipse at 50% 0%, rgba(99,102,241,0.12) 0%, transparent 70%);
        border-bottom: 1px solid var(--border);
        margin-bottom: 2.5rem;
    }
    .hero-badge {
        display: inline-block;
        background: var(--accent-glow);
        border: 1px solid var(--border);
        color: var(--accent-light);
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 0.35rem 1rem;
        border-radius: 999px;
        margin-bottom: 1.2rem;
    }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(2.2rem, 4vw, 3.4rem);
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.1;
        margin: 0 0 1rem;
    }
    .hero-title span {
        background: linear-gradient(135deg, #6366F1 0%, #A78BFA 50%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: var(--text-secondary);
        max-width: 520px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ── Cards ── */
    .card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.6rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s;
    }
    .card:hover { border-color: var(--accent); }

    .card-label {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 0.6rem;
    }

    /* ── Score display ── */
    .score-ring-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 2rem 1rem;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 20px;
    }
    .score-number {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 5rem;
        font-weight: 700;
        line-height: 1;
        background: linear-gradient(135deg, #6366F1, #A78BFA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .score-label { color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.4rem; }
    .score-verdict {
        margin-top: 0.8rem;
        padding: 0.4rem 1rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* ── Metric pills ── */
    .pill-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }
    .pill {
        padding: 0.3rem 0.75rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 500;
        border: 1px solid;
    }
    .pill-green  { background: rgba(16,185,129,0.1); color: #34D399; border-color: rgba(16,185,129,0.3); }
    .pill-red    { background: rgba(239,68,68,0.1);  color: #F87171; border-color: rgba(239,68,68,0.3); }
    .pill-blue   { background: rgba(99,102,241,0.1); color: #818CF8; border-color: rgba(99,102,241,0.3); }
    .pill-yellow { background: rgba(245,158,11,0.1); color: #FCD34D; border-color: rgba(245,158,11,0.3); }

    /* ── Section header ── */
    .section-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 2rem 0 1rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    /* ── Question cards ── */
    .question-card {
        background: var(--bg-card);
        border-left: 3px solid var(--accent);
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
        color: var(--text-primary);
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .question-num {
        font-size: 0.7rem;
        color: var(--accent-light);
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
    }

    /* ── Feedback items ── */
    .feedback-item {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.6rem;
        display: flex;
        gap: 0.75rem;
        align-items: flex-start;
    }
    .feedback-icon { font-size: 1.1rem; flex-shrink: 0; margin-top: 0.05rem; }
    .feedback-text { color: var(--text-secondary); font-size: 0.9rem; line-height: 1.55; }

    /* ── Upload zone ── */
    .stFileUploader > div > div {
        background: var(--bg-card) !important;
        border: 2px dashed var(--border) !important;
        border-radius: 14px !important;
        padding: 1.5rem !important;
        transition: border-color 0.2s !important;
    }
    .stFileUploader > div > div:hover { border-color: var(--accent) !important; }

    /* ── Text areas & inputs ── */
    .stTextArea textarea {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-size: 0.9rem !important;
        line-height: 1.6 !important;
    }
    .stTextArea textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px var(--accent-glow) !important; }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #6366F1 0%, #7C3AED 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.7rem 2rem !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.02em !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
    }
    .stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(99,102,241,0.4) !important; }

    /* ── Progress bar ── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366F1, #A78BFA) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-card) !important;
        border-radius: 12px !important;
        padding: 0.3rem !important;
        border: 1px solid var(--border) !important;
        gap: 0.2rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--accent) !important;
        color: white !important;
    }

    /* ── Divider ── */
    hr { border-color: var(--border) !important; margin: 2rem 0 !important; }

    /* ── Spinner ── */
    .stSpinner > div { border-top-color: var(--accent) !important; }

    /* ── Download button ── */
    .stDownloadButton > button {
        background: transparent !important;
        border: 1px solid var(--border) !important;
        color: var(--accent-light) !important;
        border-radius: 10px !important;
    }
    .stDownloadButton > button:hover { background: var(--accent-glow) !important; border-color: var(--accent) !important; }

    /* ── Label colors ── */
    .stTextArea label, .stFileUploader label { color: var(--text-secondary) !important; font-size: 0.85rem !important; }

    /* ── Info / warning callouts ── */
    .step-guide {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.5rem;
    }
    .step-guide h4 { color: var(--accent-light); font-size: 0.85rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; margin: 0 0 0.8rem; }
    .step-row { display: flex; align-items: center; gap: 0.8rem; color: var(--text-secondary); font-size: 0.88rem; margin-bottom: 0.5rem; }
    .step-num { background: var(--accent-glow); color: var(--accent-light); border-radius: 50%; width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 700; flex-shrink: 0; }
    </style>
    """, unsafe_allow_html=True)


# ─── Hero Header ──────────────────────────────────────────────────────────────
def render_hero():
    st.markdown("""
    <div class="hero-header">
        <div class="hero-badge">⚡ Powered by Google Gemini AI</div>
        <h1 class="hero-title">AI <span>Resume Analyzer</span></h1>
        <p class="hero-subtitle">
            Upload your resume and paste a job description.<br>
            Get an instant AI-powered match score, skill gaps, and a full ATS report.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ─── Guided steps panel ───────────────────────────────────────────────────────
def render_guide():
    st.markdown("""
    <div class="step-guide">
        <h4>How it works</h4>
        <div class="step-row"><span class="step-num">1</span>Upload your PDF resume (text-based)</div>
        <div class="step-row"><span class="step-num">2</span>Paste the target job description</div>
        <div class="step-row"><span class="step-num">3</span>Click <strong>Analyze Resume</strong></div>
        <div class="step-row"><span class="step-num">4</span>Download the full PDF report</div>
    </div>
    """, unsafe_allow_html=True)


# ─── Simulated progress animation ────────────────────────────────────────────
def show_analysis_progress():
    steps = [
        ("📄 Extracting resume text…",       0.15),
        ("🔍 Parsing job description…",       0.30),
        ("🧠 Running Gemini AI analysis…",    0.55),
        ("📊 Calculating match score…",       0.70),
        ("💡 Generating recommendations…",    0.85),
        ("📝 Building ATS report…",           0.95),
        ("✅ Finalizing results…",             1.00),
    ]
    bar = st.progress(0)
    status = st.empty()
    for msg, pct in steps:
        status.markdown(f"<p style='color:#9CA3AF;font-size:0.88rem;'>{msg}</p>", unsafe_allow_html=True)
        bar.progress(pct)
        time.sleep(0.4)
    status.empty()
    bar.empty()


# ─── Results rendering ────────────────────────────────────────────────────────
def render_results(analysis: dict, resume_text: str, job_desc: str):
    """Render all analysis results in a structured tabbed layout."""

    score = analysis.get("match_score", 0)

    # Determine verdict label + color
    if score >= 80:
        verdict, verdict_color = "Excellent Match", "#10B981"
    elif score >= 60:
        verdict, verdict_color = "Good Match", "#F59E0B"
    elif score >= 40:
        verdict, verdict_color = "Partial Match", "#F97316"
    else:
        verdict, verdict_color = "Low Match", "#EF4444"

    # ── Top summary row ────────────────────────────────────────────────────
    col_score, col_stats = st.columns([1, 2])

    with col_score:
        st.markdown(f"""
        <div class="score-ring-wrap">
            <div class="card-label">Overall Match Score</div>
            <div class="score-number">{score}</div>
            <div class="score-label">out of 100</div>
            <div class="score-verdict" style="background:rgba(99,102,241,0.1);color:{verdict_color};border:1px solid {verdict_color}40;">
                {verdict}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_stats:
        strengths    = analysis.get("strengths", [])
        missing      = analysis.get("missing_skills", [])
        improvements = analysis.get("improvements", [])

        # Mini metric row
        m1, m2, m3 = st.columns(3)
        m1.metric("✅ Strengths",       len(strengths))
        m2.metric("⚠️ Skill Gaps",      len(missing))
        m3.metric("💡 Improvements",    len(improvements))

        st.markdown("<br>", unsafe_allow_html=True)
        # Quick keyword pills
        st.markdown("<div class='card-label'>Matched Strengths</div>", unsafe_allow_html=True)
        pills_html = "<div class='pill-row'>"
        for s in strengths[:6]:
            pills_html += f"<span class='pill pill-green'>{s}</span>"
        pills_html += "</div>"
        st.markdown(pills_html, unsafe_allow_html=True)

        st.markdown("<br><div class='card-label'>Missing Skills</div>", unsafe_allow_html=True)
        pills_html = "<div class='pill-row'>"
        for m in missing[:6]:
            pills_html += f"<span class='pill pill-red'>{m}</span>"
        pills_html += "</div>"
        st.markdown(pills_html, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "📊 Skill Analysis",
        "💡 Improvements",
        "🚀 Projects & Certs",
        "🤖 ATS Report",
        "❓ Interview Prep",
    ])

    # Tab 1 — Skill Analysis
    with tabs[0]:
        render_skill_gap_chart(strengths, missing)
        render_keyword_heatmap(analysis.get("keywords", {}), job_desc)

    # Tab 2 — Improvements
    with tabs[1]:
        st.markdown("<div class='section-title'>💡 Suggested Improvements</div>", unsafe_allow_html=True)
        for item in improvements:
            st.markdown(f"""
            <div class="feedback-item">
                <span class="feedback-icon">🔧</span>
                <span class="feedback-text">{item}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>📋 Section-wise Feedback</div>", unsafe_allow_html=True)
        render_section_feedback(analysis.get("section_feedback", {}))

    # Tab 3 — Projects & Certifications
    with tabs[2]:
        col_proj, col_cert = st.columns(2)
        with col_proj:
            st.markdown("<div class='section-title'>🚀 Recommended Projects</div>", unsafe_allow_html=True)
            for proj in analysis.get("recommended_projects", []):
                st.markdown(f"""
                <div class="feedback-item">
                    <span class="feedback-icon">💻</span>
                    <span class="feedback-text">{proj}</span>
                </div>""", unsafe_allow_html=True)

        with col_cert:
            st.markdown("<div class='section-title'>🏅 Recommended Certifications</div>", unsafe_allow_html=True)
            for cert in analysis.get("recommended_certifications", []):
                st.markdown(f"""
                <div class="feedback-item">
                    <span class="feedback-icon">🎓</span>
                    <span class="feedback-text">{cert}</span>
                </div>""", unsafe_allow_html=True)

    # Tab 4 — ATS Report
    with tabs[3]:
        st.markdown("<div class='section-title'>🤖 ATS Optimization Report</div>", unsafe_allow_html=True)
        ats = analysis.get("ats_report", {})
        if isinstance(ats, dict):
            for key, value in ats.items():
                with st.expander(f"📌 {key}", expanded=True):
                    if isinstance(value, list):
                        for v in value:
                            st.markdown(f"• {v}")
                    else:
                        st.markdown(value)
        else:
            st.markdown(str(ats))

    # Tab 5 — Interview Questions
    with tabs[4]:
        st.markdown("<div class='section-title'>❓ Likely Interview Questions</div>", unsafe_allow_html=True)
        for i, q in enumerate(analysis.get("interview_questions", []), 1):
            st.markdown(f"""
            <div class="question-card">
                <div class="question-num">Question {i}</div>
                {q}
            </div>""", unsafe_allow_html=True)


# ─── Main App ─────────────────────────────────────────────────────────────────
def main():
    load_css()
    render_hero()

    # ── Input columns ──────────────────────────────────────────────────────
    left, right = st.columns([1, 1], gap="large")

    with left:
        render_guide()
        st.markdown("<div class='card-label'>Upload Your Resume (PDF)</div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            label="resume_upload",
            type=["pdf"],
            label_visibility="collapsed",
            help="Upload a text-based PDF resume (not scanned image).",
        )

    with right:
        st.markdown("<div class='card-label'>Paste Job Description</div>", unsafe_allow_html=True)
        job_description = st.text_area(
            label="job_description",
            placeholder="Paste the full job description here — include responsibilities, required skills, and qualifications…",
            height=260,
            label_visibility="collapsed",
        )

    # ── Analyze button ─────────────────────────────────────────────────────
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        analyze_clicked = st.button("🎯 Analyze Resume", use_container_width=True)

    # ── Run analysis ───────────────────────────────────────────────────────
    if analyze_clicked:
        # Validate inputs
        if not uploaded_file:
            st.error("Please upload a PDF resume before running the analysis.")
            return
        if not job_description.strip():
            st.error("Please paste a job description before running the analysis.")
            return
        if len(job_description.strip()) < 50:
            st.warning("The job description seems very short. For best results, paste the full JD.")

        st.markdown("<hr>", unsafe_allow_html=True)

        # Extract resume text
        with st.spinner("Reading your resume…"):
            resume_text = extract_text_from_pdf(uploaded_file)
            if not resume_text or len(resume_text.strip()) < 100:
                st.error(
                    "Could not extract readable text from the PDF. "
                    "Make sure it's a text-based PDF, not a scanned image."
                )
                return

        # Run AI analysis with progress animation
        progress_placeholder = st.empty()
        with progress_placeholder.container():
            show_analysis_progress()

        with st.spinner(""):
            analysis = analyze_resume(resume_text, job_description)

        progress_placeholder.empty()

        if "error" in analysis:
            st.error(f"Analysis failed: {analysis['error']}")
            st.info(
                "Check that your GOOGLE_API_KEY environment variable is set correctly, "
                "or verify your internet connection."
            )
            return

        # Show results
        st.success("✅ Analysis complete!")
        render_results(analysis, resume_text, job_description)

        # ── Download report ──────────────────────────────────────────────
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📥 Download Full Report</div>", unsafe_allow_html=True)

        with st.spinner("Building PDF report…"):
            pdf_bytes = generate_pdf_report(analysis, resume_text, job_description)

        col_dl, _ = st.columns([1, 3])
        with col_dl:
            st.download_button(
                label="⬇️  Download PDF Report",
                data=pdf_bytes,
                file_name="resume_analysis_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        # Optionally expose raw JSON for developers
        with st.expander("🛠 Raw Analysis JSON (for developers)"):
            st.json(analysis)


if __name__ == "__main__":
    main()
