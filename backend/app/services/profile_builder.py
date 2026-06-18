import json
import os
from pathlib import Path

import anthropic

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

from ..config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

PROFILE_EXTRACTION_PROMPT = """You are an expert resume parser. Extract a complete structured profile from the resume text below.

Return ONLY valid JSON with this exact structure (no markdown, no explanation):
{
  "name": "",
  "email": "",
  "phone": "",
  "current_title": "",
  "years_experience": 0,
  "summary": "",
  "skills": {
    "technical": [],
    "tools": [],
    "soft": []
  },
  "experience": [
    {
      "title": "",
      "company": "",
      "location": "",
      "start_date": "",
      "end_date": "",
      "duration": "",
      "bullets": []
    }
  ],
  "education": [
    {
      "degree": "",
      "field": "",
      "institution": "",
      "year": ""
    }
  ],
  "certifications": [],
  "achievements": [],
  "industries": [],
  "strong_areas": [],
  "languages": []
}

Rules:
- Extract ALL skills mentioned, even if implicit in job descriptions
- strong_areas: 3-5 key differentiators that make this candidate stand out
- achievements: quantified wins extracted from bullets (e.g. "Grew revenue 40% YoY")
- industries: industries the candidate has worked in
- If a field is not found, use empty string or empty array
- years_experience: calculate from work history dates"""


def extract_text_from_pdf(file_path: str) -> str:
    if not HAS_PYPDF2:
        return ""
    text = []
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text.append(page.extract_text() or "")
    return "\n".join(text)


def extract_text_from_docx(file_path: str) -> str:
    if not HAS_DOCX:
        return ""
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text_from_file(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""


def build_profile(resume_text: str, extra_context: str = "") -> dict:
    full_text = resume_text
    if extra_context:
        full_text += f"\n\n--- Additional Context ---\n{extra_context}"

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": f"{PROFILE_EXTRACTION_PROMPT}\n\nRESUME:\n{full_text}"
            }
        ]
    )

    response_text = message.content[0].text.strip()
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    return json.loads(response_text)
