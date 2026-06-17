"""
report_generator.py
--------------------
Generates a professionally formatted, downloadable PDF analysis report
using ReportLab. The report mirrors all sections visible in the UI.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


# ─── Colour palette ────────────────────────────────────────────────────────────
C_DARK    = colors.HexColor("#0A0F1E")
C_CARD    = colors.HexColor("#111827")
C_ACCENT  = colors.HexColor("#6366F1")
C_PURPLE  = colors.HexColor("#A78BFA")
C_SUCCESS = colors.HexColor("#10B981")
C_DANGER  = colors.HexColor("#EF4444")
C_WARNING = colors.HexColor("#F59E0B")
C_TEXT    = colors.HexColor("#F9FAFB")
C_MUTED   = colors.HexColor("#9CA3AF")
C_WHITE   = colors.white


def _build_styles():
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "DocTitle",
            fontSize=26,
            fontName="Helvetica-Bold",
            textColor=C_WHITE,
            spaceAfter=4,
            alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "DocSubtitle",
            fontSize=11,
            fontName="Helvetica",
            textColor=C_MUTED,
            spaceAfter=16,
            alignment=TA_CENTER,
        ),
        "section_title": ParagraphStyle(
            "SectionTitle",
            fontSize=14,
            fontName="Helvetica-Bold",
            textColor=C_ACCENT,
            spaceBefore=14,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            fontSize=10,
            fontName="Helvetica",
            textColor=C_MUTED,
            spaceAfter=4,
            leading=15,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            fontSize=10,
            fontName="Helvetica",
            textColor=C_MUTED,
            spaceAfter=3,
            leftIndent=14,
            leading=14,
        ),
        "label": ParagraphStyle(
            "Label",
            fontSize=8,
            fontName="Helvetica-Bold",
            textColor=C_ACCENT,
            spaceAfter=2,
            letterSpacing=1,
        ),
        "score": ParagraphStyle(
            "Score",
            fontSize=52,
            fontName="Helvetica-Bold",
            textColor=C_ACCENT,
            alignment=TA_CENTER,
        ),
        "question": ParagraphStyle(
            "Question",
            fontSize=10,
            fontName="Helvetica",
            textColor=C_TEXT,
            spaceAfter=6,
            leading=15,
        ),
    }
    return styles


def _header_banner(styles) -> list:
    """Dark hero banner at the top of the report."""
    now = datetime.now().strftime("%B %d, %Y  ·  %H:%M")
    data = [[
        Paragraph("🎯 AI Resume Analyzer", styles["title"]),
    ]]
    tbl = Table(data, colWidths=[160*mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), C_DARK),
        ("TOPPADDING",   (0,0), (-1,-1), 20),
        ("BOTTOMPADDING",(0,0), (-1,-1), 10),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("ALIGN",        (0,0), (-1,-1), "CENTER"),
    ]))
    return [
        tbl,
        Paragraph(f"Generated on {now}", styles["subtitle"]),
        HRFlowable(color=C_ACCENT, thickness=1, width="100%"),
        Spacer(1, 8*mm),
    ]


def _score_section(score: int, styles) -> list:
    """Large score + verdict block."""
    if score >= 80:
        verdict, c = "Excellent Match ✅", C_SUCCESS
    elif score >= 60:
        verdict, c = "Good Match 👍", C_WARNING
    elif score >= 40:
        verdict, c = "Partial Match ⚠️", C_WARNING
    else:
        verdict, c = "Low Match ❌", C_DANGER

    score_para = Paragraph(f"{score}", styles["score"])
    label_para = Paragraph("OVERALL MATCH SCORE  /100", styles["label"])
    verdict_para = Paragraph(f"<b>{verdict}</b>", ParagraphStyle(
        "Verdict", fontSize=13, fontName="Helvetica-Bold", textColor=c,
        alignment=TA_CENTER,
    ))

    data = [[score_para], [label_para], [verdict_para]]
    tbl = Table(data, colWidths=[160*mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), C_CARD),
        ("TOPPADDING",    (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("ROUNDEDCORNERS", [8]),
    ]))
    return [tbl, Spacer(1, 8*mm)]


def _pill_table(items: list, colour, styles) -> list:
    """Render a list of short skill strings as coloured pills in a table."""
    if not items:
        return [Paragraph("None identified.", styles["body"])]

    cells = [Paragraph(f"  {item}  ", ParagraphStyle(
        "Pill", fontSize=9, fontName="Helvetica", textColor=C_WHITE,
    )) for item in items]

    # Arrange in rows of 3
    rows = [cells[i:i+3] for i in range(0, len(cells), 3)]
    # Pad last row
    while rows and len(rows[-1]) < 3:
        rows[-1].append(Paragraph("", styles["body"]))

    tbl = Table(rows, colWidths=[50*mm, 50*mm, 60*mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), colour),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS",(0,0), (-1,-1), [colour]),
        ("GRID",          (0,0), (-1,-1), 1, C_DARK),
    ]))
    return [tbl, Spacer(1, 4*mm)]


def _bulleted_list(items: list, styles) -> list:
    elements = []
    for item in items:
        elements.append(Paragraph(f"• &nbsp; {item}", styles["bullet"]))
    return elements


def generate_pdf_report(analysis: dict, resume_text: str, job_desc: str) -> bytes:
    """
    Build and return a complete PDF report as bytes.

    Args:
        analysis:    Parsed Gemini analysis dict.
        resume_text: Extracted resume plain text.
        job_desc:    Job description pasted by user.

    Returns:
        PDF file contents as a bytes object.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=15*mm,
        bottomMargin=15*mm,
    )

    styles   = _build_styles()
    elements = []

    # ── Header ────────────────────────────────────────────────────────────
    elements.extend(_header_banner(styles))

    # ── Score ─────────────────────────────────────────────────────────────
    elements.extend(_score_section(analysis.get("match_score", 0), styles))

    # ── Strengths ─────────────────────────────────────────────────────────
    elements.append(Paragraph("✅ Matched Strengths", styles["section_title"]))
    elements.extend(_pill_table(analysis.get("strengths", []), C_SUCCESS, styles))

    # ── Missing skills ────────────────────────────────────────────────────
    elements.append(Paragraph("⚠️ Skill Gaps", styles["section_title"]))
    elements.extend(_pill_table(analysis.get("missing_skills", []), C_DANGER, styles))

    # ── Improvements ─────────────────────────────────────────────────────
    elements.append(Paragraph("💡 Suggested Improvements", styles["section_title"]))
    elements.extend(_bulleted_list(analysis.get("improvements", []), styles))
    elements.append(Spacer(1, 4*mm))

    # ── Recommended projects ──────────────────────────────────────────────
    elements.append(Paragraph("🚀 Recommended Projects", styles["section_title"]))
    elements.extend(_bulleted_list(analysis.get("recommended_projects", []), styles))
    elements.append(Spacer(1, 4*mm))

    # ── Certifications ────────────────────────────────────────────────────
    elements.append(Paragraph("🏅 Recommended Certifications", styles["section_title"]))
    elements.extend(_bulleted_list(analysis.get("recommended_certifications", []), styles))
    elements.append(Spacer(1, 4*mm))

    # ── ATS Report ────────────────────────────────────────────────────────
    elements.append(Paragraph("🤖 ATS Optimization Report", styles["section_title"]))
    ats = analysis.get("ats_report", {})
    if isinstance(ats, dict):
        for key, value in ats.items():
            elements.append(Paragraph(f"<b>{key}</b>", ParagraphStyle(
                "AtsKey", fontSize=10, fontName="Helvetica-Bold",
                textColor=C_TEXT, spaceBefore=6, spaceAfter=2,
            )))
            if isinstance(value, list):
                for v in value:
                    elements.append(Paragraph(f"• {v}", styles["bullet"]))
            else:
                elements.append(Paragraph(str(value), styles["body"]))
    elements.append(Spacer(1, 4*mm))

    # ── Section feedback ──────────────────────────────────────────────────
    elements.append(Paragraph("📋 Section-wise Feedback", styles["section_title"]))
    for section, feedback in analysis.get("section_feedback", {}).items():
        elements.append(Paragraph(f"<b>{section}</b>", ParagraphStyle(
            "SecLabel", fontSize=10, fontName="Helvetica-Bold",
            textColor=C_PURPLE, spaceBefore=5, spaceAfter=2,
        )))
        elements.append(Paragraph(str(feedback), styles["body"]))
    elements.append(Spacer(1, 4*mm))

    # ── Interview questions ───────────────────────────────────────────────
    elements.append(Paragraph("❓ Likely Interview Questions", styles["section_title"]))
    for i, q in enumerate(analysis.get("interview_questions", []), 1):
        elements.append(Paragraph(f"Q{i}.  {q}", styles["question"]))

    # ── Footer ────────────────────────────────────────────────────────────
    elements.append(Spacer(1, 10*mm))
    elements.append(HRFlowable(color=C_ACCENT, thickness=0.5, width="100%"))
    elements.append(Paragraph(
        "Generated by AI Resume Analyzer · Powered by Google Gemini",
        ParagraphStyle("Footer", fontSize=8, textColor=C_MUTED, alignment=TA_CENTER, spaceBefore=4),
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
