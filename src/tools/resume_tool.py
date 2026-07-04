"""
ResumeTool — read a resume (PDF / DOCX / TXT / MD), get APEX-Genius
to rewrite it for impact, emit a clean PDF.

Pipeline:
  load → parse to plain text → call Gemini for structured rewrite
       → render the structured object as a PDF (reportlab)
       → return path + tier-by-tier feedback (what's good / weak / missing)

Output PDF style: minimal one-column, ATS-friendly. No images, no columns,
black-on-white, single accent color.
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

try:
    from google import genai  # type: ignore
except Exception:  # pragma: no cover
    genai = None

from src.core.time_context import TimeContext


# ─────────────────────────────────────────────────────────────────────────────
# Parsing — accept .pdf / .docx / .txt / .md
# ─────────────────────────────────────────────────────────────────────────────

def load_resume(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        from pypdf import PdfReader  # lazy
        reader = PdfReader(path)
        chunks = [(page.extract_text() or "") for page in reader.pages]
        return "\n".join(chunks).strip()
    if ext == ".docx":
        try:
            import docx  # python-docx
        except Exception as e:
            raise RuntimeError("python-docx not installed — `pip install python-docx`") from e
        d = docx.Document(path)
        return "\n".join(p.text for p in d.paragraphs).strip()
    if ext in (".txt", ".md"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    raise ValueError(f"unsupported extension: {ext}")


# ─────────────────────────────────────────────────────────────────────────────
# Rewrite — Gemini structured JSON
# ─────────────────────────────────────────────────────────────────────────────

REWRITE_SYSTEM = """\
You are APEX-Resume, a brutally honest senior recruiter + ex-FAANG hiring
manager. Rewrite the user's resume for MAXIMUM IMPACT while keeping every
factual claim intact.

DO:
  - Rewrite each bullet as <action verb> + <quantified outcome> when data exists.
  - Lead with results, not responsibilities. "Cut p95 latency 40%" beats
    "Worked on improving latency."
  - Tighten language. Remove filler ("responsible for", "helped to").
  - Group skills by domain, sorted by relevance.
  - Preserve all factual content: dates, employers, school, GPA, links.

DON'T:
  - Invent achievements, numbers, employers, or skills.
  - Add buzzwords without substance ("synergize", "leverage paradigms").

OUTPUT FORMAT: pure JSON, no markdown fence:
{
  "name": "...",
  "headline": "Senior X | Y | Z (one line, max 80 chars)",
  "contact": {"email": "...", "phone": "...", "location": "...", "links": ["..."]},
  "summary": "2-3 sentence punchy summary",
  "experience": [
    {
      "role": "...",
      "company": "...",
      "location": "...",
      "dates": "MMM YYYY – MMM YYYY",
      "bullets": ["impact bullet 1", "impact bullet 2"]
    }
  ],
  "projects": [
    {"name": "...", "tech": ["..."], "bullets": ["..."]}
  ],
  "education": [
    {"school": "...", "degree": "...", "dates": "...", "details": "..."}
  ],
  "skills": {
    "Languages": ["..."],
    "Frameworks": ["..."],
    "Tools": ["..."]
  },
  "feedback": {
    "strong": ["specific thing user did well"],
    "weak":   ["specific thing user did poorly"],
    "missing": ["section/proof/metric they should add"],
    "one_liner": "single dry-witty sentence"
  }
}

If a section doesn't exist in the source, omit it from the JSON (don't
fabricate). Lists may be empty but feedback fields must be populated.
"""


async def rewrite_resume(text: str, target_role: Optional[str] = None,
                         model: str = "gemini-3.5-flash") -> Dict[str, Any]:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not genai or not api_key:
        return _fallback_parse(text)
    client = genai.Client(api_key=api_key)
    role_block = f"\nTARGET ROLE: {target_role}\n" if target_role else ""
    user_msg = (
        f"{REWRITE_SYSTEM}\n\n"
        f"{TimeContext.system_prefix()}\n"
        f"{role_block}"
        f"\nRESUME SOURCE TEXT:\n---\n{text}\n---\n\n"
        "Return JSON only."
    )
    try:
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model=model,
                contents=user_msg,
                config={"response_mime_type": "application/json"},
            ),
        )
        parsed = json.loads(res.text or "{}")
        if not isinstance(parsed, dict):
            return _fallback_parse(text)
        parsed.setdefault("feedback", {})
        parsed["feedback"].setdefault("strong", [])
        parsed["feedback"].setdefault("weak", [])
        parsed["feedback"].setdefault("missing", [])
        parsed["feedback"].setdefault("one_liner", "")
        return parsed
    except Exception:
        return _fallback_parse(text)


def _fallback_parse(text: str) -> Dict[str, Any]:
    """When no brain is available, hand back the raw text as a single block."""
    return {
        "name": "(name unknown)",
        "headline": "(headline unavailable — Gemini offline)",
        "contact": {},
        "summary": text[:600],
        "experience": [],
        "projects": [],
        "education": [],
        "skills": {},
        "feedback": {
            "strong": [],
            "weak": [],
            "missing": ["GEMINI_API_KEY not set — set it to unlock rewrite."],
            "one_liner": "I can read your resume but my critic is in the breakroom.",
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# PDF render — reportlab
# ─────────────────────────────────────────────────────────────────────────────

def render_pdf(data: Dict[str, Any], out_path: str,
               accent: str = "#1f4e79") -> str:
    """
    Render the structured resume dict to a clean one-column PDF.
    Returns the absolute output path.
    """
    from reportlab.lib.pagesizes import letter  # lazy heavy import
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether,
    )
    from reportlab.lib.enums import TA_LEFT

    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    accent_color = colors.HexColor(accent)

    base = getSampleStyleSheet()
    styles = {
        "name": ParagraphStyle("name", parent=base["Heading1"], fontSize=20,
                               leading=22, spaceAfter=2, textColor=accent_color,
                               alignment=TA_LEFT),
        "headline": ParagraphStyle("headline", parent=base["BodyText"], fontSize=10,
                                   textColor=colors.grey, spaceAfter=2),
        "contact": ParagraphStyle("contact", parent=base["BodyText"], fontSize=9,
                                  textColor=colors.HexColor("#555555"), spaceAfter=8),
        "section": ParagraphStyle("section", parent=base["Heading2"], fontSize=12,
                                  leading=14, spaceBefore=10, spaceAfter=4,
                                  textColor=accent_color),
        "role": ParagraphStyle("role", parent=base["BodyText"], fontSize=10.5,
                               leading=13, spaceAfter=0, fontName="Helvetica-Bold"),
        "meta": ParagraphStyle("meta", parent=base["BodyText"], fontSize=9.5,
                               leading=12, textColor=colors.HexColor("#666666"),
                               spaceAfter=4),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontSize=10,
                               leading=13, spaceAfter=2),
        "bullet": ParagraphStyle("bullet", parent=base["BodyText"], fontSize=10,
                                 leading=13, leftIndent=12, bulletIndent=2,
                                 spaceAfter=1),
    }

    flow: List = []

    def H(text):
        return Paragraph(_e(text), styles["section"])

    def B(text):
        return Paragraph("• " + _e(text), styles["bullet"])

    # Header
    flow.append(Paragraph(_e(data.get("name", "")), styles["name"]))
    if data.get("headline"):
        flow.append(Paragraph(_e(data["headline"]), styles["headline"]))
    contact = data.get("contact") or {}
    bits: List[str] = []
    for k in ("email", "phone", "location"):
        if contact.get(k):
            bits.append(_e(contact[k]))
    for link in contact.get("links", []) or []:
        bits.append(_e(link))
    if bits:
        flow.append(Paragraph("  •  ".join(bits), styles["contact"]))
    flow.append(HRFlowable(width="100%", thickness=0.8, color=accent_color,
                           spaceBefore=0, spaceAfter=6))

    # Summary
    if data.get("summary"):
        flow.append(H("Summary"))
        flow.append(Paragraph(_e(data["summary"]), styles["body"]))

    # Experience
    if data.get("experience"):
        flow.append(H("Experience"))
        for exp in data["experience"]:
            block = []
            head = exp.get("role", "")
            company = exp.get("company", "")
            line = f"{head}" + (f" — {company}" if company else "")
            block.append(Paragraph(_e(line), styles["role"]))
            meta_bits = [b for b in (exp.get("location", ""), exp.get("dates", "")) if b]
            if meta_bits:
                block.append(Paragraph(_e("  •  ".join(meta_bits)), styles["meta"]))
            for b in exp.get("bullets", []) or []:
                block.append(B(b))
            block.append(Spacer(1, 4))
            flow.append(KeepTogether(block))

    # Projects
    if data.get("projects"):
        flow.append(H("Projects"))
        for pr in data["projects"]:
            block = []
            name = pr.get("name", "")
            tech = ", ".join(pr.get("tech", []) or [])
            head = name + (f" — {tech}" if tech else "")
            block.append(Paragraph(_e(head), styles["role"]))
            for b in pr.get("bullets", []) or []:
                block.append(B(b))
            block.append(Spacer(1, 4))
            flow.append(KeepTogether(block))

    # Education
    if data.get("education"):
        flow.append(H("Education"))
        for ed in data["education"]:
            head = ed.get("school", "")
            degree = ed.get("degree", "")
            head_line = head + (f" — {degree}" if degree else "")
            block = [Paragraph(_e(head_line), styles["role"])]
            meta_bits = [b for b in (ed.get("dates", ""), ed.get("details", "")) if b]
            if meta_bits:
                block.append(Paragraph(_e("  •  ".join(meta_bits)), styles["meta"]))
            block.append(Spacer(1, 4))
            flow.append(KeepTogether(block))

    # Skills
    if data.get("skills"):
        flow.append(H("Skills"))
        for group, items in (data["skills"] or {}).items():
            if not items:
                continue
            line = f"<b>{_e(group)}:</b> " + _e(", ".join(items))
            flow.append(Paragraph(line, styles["body"]))

    doc = SimpleDocTemplate(
        out_path, pagesize=letter,
        leftMargin=0.6 * inch, rightMargin=0.6 * inch,
        topMargin=0.55 * inch, bottomMargin=0.55 * inch,
        title=data.get("name", "Resume"),
    )
    doc.build(flow)
    return os.path.abspath(out_path)


def _e(s: Any) -> str:
    """Escape reportlab inline markup."""
    if s is None:
        return ""
    t = str(s)
    return (
        t.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
    )


# ─────────────────────────────────────────────────────────────────────────────
# Top-level orchestrator
# ─────────────────────────────────────────────────────────────────────────────

class ResumeTool:
    def __init__(self, out_dir: str = "data/resumes"):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

    async def improve(
        self,
        path: str,
        target_role: Optional[str] = None,
        out_name: Optional[str] = None,
        accent: str = "#1f4e79",
    ) -> Dict[str, Any]:
        text = load_resume(path)
        data = await rewrite_resume(text, target_role=target_role)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_name = out_name or f"resume_{stamp}.pdf"
        out_path = os.path.join(self.out_dir, out_name)
        try:
            pdf_path = render_pdf(data, out_path, accent=accent)
        except Exception as e:
            return {
                "success": False,
                "error": f"PDF render failed: {e}",
                "data": data,
            }
        return {
            "success": True,
            "pdf": pdf_path,
            "data": data,
            "feedback": data.get("feedback", {}),
        }
