# 🎯 AI Resume Analyzer

> **Internship-ready AI web application** — upload a resume, paste a job description, and receive a
> comprehensive AI-powered analysis in seconds: match score, skill gaps, ATS optimization, interview prep, and more.

---

## ✨ Live Features

| Feature | Description |
|---|---|
| 📄 **PDF Extraction** | Automatic text extraction from any text-based PDF resume |
| 🤖 **Gemini AI Analysis** | Google Gemini 1.5 Flash powers all intelligence |
| 📊 **Match Score (0–100)** | Calibrated score with detailed verdict |
| ⚠️ **Skill Gap Detection** | Side-by-side view of matched and missing skills |
| 💡 **Improvement Suggestions** | 6–8 specific, actionable resume improvements |
| 🚀 **Project Recommendations** | Tailored project ideas to bridge skill gaps |
| 🏅 **Certification Guidance** | Relevant certifications with justification |
| 🤖 **ATS Report** | Full ATS compatibility analysis with keyword list |
| ❓ **Interview Questions** | 5 likely questions based on your resume + JD |
| 🔥 **Keyword Heatmap** | Treemap visualisation of JD keyword coverage |
| 📋 **Section Feedback** | Per-section resume critique |
| ⬇️ **PDF Download** | Professionally formatted downloadable report |

---

## 🗂 Project Structure

```
ai-resume-analyzer/
├── app.py                        # Main Streamlit application & UI
├── utils/
│   ├── __init__.py
│   ├── pdf_extractor.py          # PDF text extraction (PyMuPDF + pdfplumber)
│   ├── gemini_analyzer.py        # Gemini API integration & prompt engineering
│   ├── visualizations.py         # Plotly charts: skill gap, heatmap, donut
│   └── report_generator.py       # ReportLab PDF report builder
├── .streamlit/
│   ├── config.toml               # Streamlit theme & server config
│   └── secrets.toml.example      # API key template (never commit real file)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚡ Quick Start (5 minutes)

### Prerequisites
- Python 3.10 or higher
- A free Google Gemini API key → https://aistudio.google.com/app/apikey

### Step 1 — Clone / Download

```bash
git clone https://github.com/your-username/ai-resume-analyzer.git
cd ai-resume-analyzer
```

### Step 2 — Create a virtual environment

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Set your Gemini API key

**Option A — Streamlit secrets (recommended for deployment):**

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Open .streamlit/secrets.toml and replace the placeholder with your real key
```

**Option B — Environment variable (quick local dev):**

```bash
export GOOGLE_API_KEY="your-key-here"      # macOS / Linux
set GOOGLE_API_KEY=your-key-here           # Windows CMD
$env:GOOGLE_API_KEY="your-key-here"        # Windows PowerShell
```

### Step 5 — Run the app

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser. That's it!

---

## 🚀 Deploying to Streamlit Cloud (free)

1. Push the repo to GitHub (make sure `secrets.toml` is in `.gitignore`).
2. Go to https://share.streamlit.io → **New app**.
3. Select your repo and `app.py` as the entry point.
4. Under **Advanced settings → Secrets**, add:
   ```toml
   GOOGLE_API_KEY = "your-real-key"
   ```
5. Click **Deploy**. Done.

---

## 🏗 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                    │
│  app.py: hero UI, file upload, job description, tabs    │
└────────────────┬──────────────────────────┬─────────────┘
                 │                          │
         ┌───────▼───────┐        ┌─────────▼───────────┐
         │ pdf_extractor │        │   gemini_analyzer    │
         │               │        │                      │
         │  PyMuPDF      │        │  Prompt engineering  │
         │  pdfplumber   │        │  Gemini 1.5 Flash    │
         │  (fallback)   │        │  JSON parsing        │
         └───────────────┘        └─────────┬────────────┘
                                            │
               ┌────────────────────────────┼─────────────────┐
               │                            │                  │
      ┌────────▼───────┐         ┌──────────▼──────┐  ┌───────▼────────┐
      │ visualizations │         │report_generator │  │  Streamlit UI  │
      │                │         │                 │  │  (tabs, cards) │
      │  Plotly charts │         │  ReportLab PDF  │  │                │
      │  Skill gap bar │         │  Multi-section  │  │  Download btn  │
      │  Treemap       │         │  Professional   │  │                │
      │  Donut         │         │  layout         │  │                │
      └────────────────┘         └─────────────────┘  └────────────────┘
```

### How AI is used

1. **Prompt Engineering** — A structured system prompt defines Gemini's role as a senior technical recruiter. A strict JSON schema is enforced in the prompt so output is always machine-parseable.

2. **Single-pass analysis** — Resume text (up to 6,000 chars) and job description (up to 3,000 chars) are sent in one Gemini call at `temperature=0.4` (reproducible yet slightly creative).

3. **Structured output** — Gemini returns a single JSON object containing 10 distinct analysis fields. Regex-based post-processing handles edge cases where the model accidentally adds markdown fences.

4. **Keyword intelligence** — The `keywords` field from Gemini drives the treemap heatmap, letting users see at a glance which JD terms appear in their resume.

---

## 📚 Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | Streamlit 1.35 | Rapid Python-native web UI |
| AI / LLM | Google Gemini 1.5 Flash | Fast, affordable, 1M context window |
| PDF parsing | PyMuPDF + pdfplumber | Robust extraction for varied PDF types |
| Visualisations | Plotly 5 | Interactive, dark-theme-friendly charts |
| PDF reports | ReportLab | Production-quality PDF generation in Python |

---

## 💼 Portfolio Description (for internship applications)

> **AI Resume Analyzer** — *Python · Streamlit · Google Gemini · Plotly · ReportLab*
>
> Designed and built a full-stack AI web application that analyses resumes against job descriptions
> using Google Gemini 1.5 Flash. The app extracts text from uploaded PDFs, sends a structured
> prompt to the LLM, and renders a rich analysis including a calibrated match score, skill gap
> visualisations, ATS optimisation report, section-wise feedback, tailored project/certification
> recommendations, and five likely interview questions. Users can download a professionally
> formatted PDF report. Features interactive Plotly charts including a keyword treemap heatmap
> and skill-coverage donut. Built with production-quality modular Python, Streamlit dark-theme
> UI, and deployed on Streamlit Cloud.

---

## 📄 Resume Bullet Points

Add these to the **Projects** section of your resume:

```
• Built AI Resume Analyzer (Streamlit + Google Gemini 1.5 Flash) that parses PDF resumes,
  evaluates them against job descriptions, and returns match scores, skill gap charts, ATS
  reports, and interview prep questions via a structured LLM pipeline.

• Engineered a multi-field prompt system with JSON schema enforcement, achieving consistent
  structured output from Gemini across 10 analysis dimensions including ATS compatibility,
  section-wise feedback, and keyword heatmaps.

• Implemented interactive Plotly visualisations (treemap, donut, horizontal bar charts) in a
  custom dark-theme Streamlit UI, with a ReportLab-generated downloadable PDF report.

• Deployed application to Streamlit Cloud with environment-based secret management; project
  demonstrates full-stack AI engineering skills across LLM integration, document processing,
  data visualisation, and PDF generation.
```

---

## 🔮 Potential Enhancements

- [ ] Multi-language resume support (translate to English before analysis)
- [ ] Resume rewrite mode (LLM rewrites bullet points to match JD)
- [ ] Comparison mode (analyse same resume against multiple JDs)
- [ ] LinkedIn scraper integration (auto-fetch JD from URL)
- [ ] User accounts + history (Supabase backend)
- [ ] Resume template generator based on gaps

---

## 📝 License

MIT — free to use for personal and commercial projects.

---

## 🙏 Acknowledgements

- Google Gemini AI — https://deepmind.google/gemini
- Streamlit — https://streamlit.io
- PyMuPDF — https://pymupdf.readthedocs.io
- ReportLab — https://reportlab.com
