"""
visualizations.py
-----------------
All chart and visual components for the AI Resume Analyzer.
Built with Plotly for interactive, attractive charts.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
import re


# ─── Colour palette aligned with the app's CSS variables ──────────────────────
COLORS = {
    "accent":    "#6366F1",
    "success":   "#10B981",
    "warning":   "#F59E0B",
    "danger":    "#EF4444",
    "purple":    "#A78BFA",
    "blue":      "#60A5FA",
    "bg_card":   "#111827",
    "bg_dark":   "#0A0F1E",
    "text":      "#F9FAFB",
    "text_muted":"#9CA3AF",
}

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=COLORS["text"]),
    margin=dict(l=10, r=10, t=40, b=10),
)


# ─── 1. Score gauge (unused in main but available for embeds) ─────────────────
def render_score_card(score: int):
    """Render a Plotly gauge chart for the match score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": COLORS["text_muted"]},
            "bar": {"color": COLORS["accent"]},
            "bgcolor": COLORS["bg_card"],
            "borderwidth": 0,
            "steps": [
                {"range": [0,  40], "color": "rgba(239,68,68,0.15)"},
                {"range": [40, 70], "color": "rgba(245,158,11,0.15)"},
                {"range": [70,100], "color": "rgba(16,185,129,0.15)"},
            ],
            "threshold": {
                "line": {"color": COLORS["purple"], "width": 3},
                "thickness": 0.8,
                "value": score,
            },
        },
        number={"font": {"size": 52, "color": COLORS["accent"]}, "suffix": "/100"},
    ))
    fig.update_layout(**CHART_LAYOUT, height=280, title=dict(text="Match Score", x=0.5))
    st.plotly_chart(fig, use_container_width=True)


# ─── 2. Skill gap horizontal bar chart ────────────────────────────────────────
def render_skill_gap_chart(strengths: list, missing_skills: list):
    """
    Side-by-side horizontal bar chart visualising matched vs missing skills.
    Gives an at-a-glance view of the candidate's skill alignment.
    """
    if not strengths and not missing_skills:
        st.info("No skill data to visualise.")
        return

    # Combine and sort for display (cap at 10 each)
    matched  = strengths[:10]
    missing  = missing_skills[:10]

    # ── Matched skills ────────────────────────────────────────────────────
    fig_matched = go.Figure(go.Bar(
        y=matched,
        x=[1] * len(matched),
        orientation="h",
        marker=dict(
            color=COLORS["success"],
            opacity=0.85,
            line=dict(color="rgba(0,0,0,0)", width=0),
        ),
        text=matched,
        textposition="inside",
        insidetextanchor="middle",
        hovertemplate="%{y}<extra></extra>",
        name="Matched",
        showlegend=False,
    ))
    fig_matched.update_layout(
        **CHART_LAYOUT,
        height=max(220, len(matched) * 36),
        title=dict(text="✅ Matched Strengths", x=0, font=dict(size=14, color=COLORS["text"])),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False, autorange="reversed"),
        bargap=0.3,
    )

    # ── Missing skills ────────────────────────────────────────────────────
    fig_missing = go.Figure(go.Bar(
        y=missing,
        x=[1] * len(missing),
        orientation="h",
        marker=dict(
            color=COLORS["danger"],
            opacity=0.85,
            line=dict(color="rgba(0,0,0,0)", width=0),
        ),
        text=missing,
        textposition="inside",
        insidetextanchor="middle",
        hovertemplate="%{y}<extra></extra>",
        name="Missing",
        showlegend=False,
    ))
    fig_missing.update_layout(
        **CHART_LAYOUT,
        height=max(220, len(missing) * 36),
        title=dict(text="⚠️ Skill Gaps", x=0, font=dict(size=14, color=COLORS["text"])),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False, autorange="reversed"),
        bargap=0.3,
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(fig_matched, use_container_width=True)
    with col_b:
        st.plotly_chart(fig_missing, use_container_width=True)

    # ── Overlap donut ──────────────────────────────────────────────────────
    total     = len(matched) + len(missing)
    pct_match = round(len(matched) / total * 100) if total else 0

    fig_pie = go.Figure(go.Pie(
        labels=["Matched Skills", "Skill Gaps"],
        values=[len(matched), len(missing)],
        hole=0.65,
        marker=dict(colors=[COLORS["success"], COLORS["danger"]],
                    line=dict(color=COLORS["bg_dark"], width=3)),
        textinfo="percent+label",
        textfont=dict(size=12),
        hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig_pie.add_annotation(
        text=f"{pct_match}%<br><span style='font-size:10px'>aligned</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=20, color=COLORS["accent"]),
    )
    fig_pie.update_layout(
        **CHART_LAYOUT,
        height=300,
        title=dict(text="🎯 Skill Coverage", x=0.5, font=dict(size=14, color=COLORS["text"])),
        legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.05),
        showlegend=True,
    )
    st.plotly_chart(fig_pie, use_container_width=True)


# ─── 3. ATS keyword heatmap ───────────────────────────────────────────────────
def render_keyword_heatmap(keywords: dict, job_description: str):
    """
    Treemap (acts as a keyword heatmap) showing keyword frequency in the JD,
    colour-coded by whether each keyword was found in the resume.
    """
    if not keywords:
        return

    found_in_resume = set(kw.lower() for kw in keywords.get("found_in_resume", []))
    found_in_jd     = keywords.get("found_in_jd", [])
    overlap         = set(kw.lower() for kw in keywords.get("overlap", []))

    if not found_in_jd:
        return

    # Build frequency map from JD text
    jd_lower = job_description.lower()
    freq = {kw: max(1, jd_lower.count(kw.lower())) for kw in found_in_jd}

    labels  = list(freq.keys())
    values  = list(freq.values())
    colours = [
        COLORS["success"] if kw.lower() in overlap else COLORS["danger"]
        for kw in labels
    ]

    fig = go.Figure(go.Treemap(
        labels=labels,
        values=values,
        parents=[""] * len(labels),
        marker=dict(colors=colours, line=dict(width=2, color=COLORS["bg_dark"])),
        textinfo="label",
        hovertemplate="%{label}<br>JD frequency: %{value}<extra></extra>",
        textfont=dict(size=13, color="white"),
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        height=380,
        title=dict(
            text="🔥 ATS Keyword Heatmap  (green = found in resume · red = missing)",
            x=0, font=dict(size=13, color=COLORS["text"]),
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─── 4. Section-wise feedback cards ──────────────────────────────────────────
def render_section_feedback(section_feedback: dict):
    """
    Render each resume section's feedback as an expandable styled card.
    """
    if not section_feedback:
        st.info("No section feedback available.")
        return

    SECTION_ICONS = {
        "Summary / Objective": "📝",
        "Experience":          "💼",
        "Skills":              "🛠",
        "Education":           "🎓",
        "Projects":            "🚀",
    }

    for section, feedback in section_feedback.items():
        icon = SECTION_ICONS.get(section, "📌")
        with st.expander(f"{icon}  {section}", expanded=True):
            st.markdown(
                f"<p style='color:#9CA3AF;font-size:0.9rem;line-height:1.6;'>{feedback}</p>",
                unsafe_allow_html=True,
            )
