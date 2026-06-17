"""
gemini_analyzer.py
-------------------
Core AI analysis module powered by Groq (llama3-70b).
Fast, free, and reliable alternative to Gemini.
"""

import os
import json
import re
from groq import Groq


def _get_client():
    try:
        import streamlit as st
        api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
    except Exception:
        api_key = os.environ.get("GROQ_API_KEY", "")

    if not api_key:
        raise EnvironmentError("GROQ_API_KEY is not set.")

    return Groq(api_key=api_key)


SYSTEM_PROMPT = """
You are a senior technical recruiter and career coach with 15+ years of experience.

Analyse resumes against job descriptions. Return ONLY a valid JSON object, no markdown, no extra text.

Required JSON schema:
{
  "match_score": <integer 0-100>,
  "strengths": [<list of up to 8 strength strings>],
  "missing_skills": [<list of up to 10 missing skill strings>],
  "improvements": [<list of 6-8 actionable improvement strings>],
  "recommended_projects": [<list of 4-5 project idea strings>],
  "recommended_certifications": [<list of 4-5 certification strings>],
  "ats_report": {
    "Overall ATS Compatibility": "<paragraph>",
    "Keyword Density Issues": "<paragraph>",
    "Formatting Concerns": "<paragraph>",
    "Action Verbs Usage": "<paragraph>",
    "Quantification of Achievements": "<paragraph>",
    "Recommended ATS Keywords": ["<keyword>"]
  },
  "interview_questions": [<list of exactly 5 interview question strings>],
  "section_feedback": {
    "Summary / Objective": "<feedback>",
    "Experience": "<feedback>",
    "Skills": "<feedback>",
    "Education": "<feedback>",
    "Projects": "<feedback>"
  },
  "keywords": {
    "found_in_resume": ["<keyword>"],
    "found_in_jd": ["<keyword>"],
    "overlap": ["<keyword>"]
  }
}
"""


def analyze_resume(resume_text: str, job_description: str) -> dict:
    try:
        client = _get_client()
    except EnvironmentError as e:
        return {"error": str(e)}

    prompt = f"""
Analyse this resume against the job description.

=== RESUME ===
{resume_text[:6000]}

=== JOB DESCRIPTION ===
{job_description[:3000]}

Return the JSON analysis object now.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=4096,
        )
        raw_text = response.choices[0].message.content
    except Exception as e:
        return {"error": f"Groq API call failed: {e}"}

    return _parse_response(raw_text)


def _parse_response(raw_text: str) -> dict:
    cleaned = re.sub(r"```(?:json)?", "", raw_text).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return {"error": "No JSON found in response.", "raw": raw_text[:500]}
    try:
        data = json.loads(match.group())
        return _validate_and_fill_defaults(data)
    except json.JSONDecodeError as e:
        return {"error": f"JSON parsing error: {e}"}


def _validate_and_fill_defaults(data: dict) -> dict:
    defaults = {
        "match_score": 0,
        "strengths": [],
        "missing_skills": [],
        "improvements": [],
        "recommended_projects": [],
        "recommended_certifications": [],
        "ats_report": {},
        "interview_questions": [],
        "section_feedback": {},
        "keywords": {"found_in_resume": [], "found_in_jd": [], "overlap": []},
    }
    for key, default in defaults.items():
        if key not in data:
            data[key] = default
    data["match_score"] = max(0, min(100, int(data.get("match_score", 0))))
    return data