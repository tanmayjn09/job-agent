import os
from pathlib import Path


def _safe(text: str) -> str:
    """Replace common Unicode chars that latin-1 Helvetica can't encode."""
    return (str(text)
        .replace("–", "-").replace("—", "-")
        .replace("‘", "'").replace("’", "'")
        .replace("“", '"').replace("”", '"')
        .replace("•", "-").replace("…", "...")
        .replace("â", "-").replace("⏤", "-")
        .encode("latin-1", errors="replace").decode("latin-1"))


def generate_pdf(resume_json: dict, output_path: str) -> str:
    from fpdf import FPDF

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(18, 16, 18)
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    W = pdf.w - pdf.l_margin - pdf.r_margin

    def section_header(title: str):
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(W, 5, _safe(title.upper()), ln=True)
        pdf.set_draw_color(180, 180, 180)
        pdf.set_line_width(0.3)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + W, pdf.get_y())
        pdf.ln(2)
        pdf.set_text_color(0, 0, 0)

    # ── Header ────────────────────────────────────────────────────────────────
    name = _safe(resume_json.get("name", ""))
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(W, 9, name, ln=True, align="C")

    contact_parts = []
    if resume_json.get("email"):
        contact_parts.append(_safe(resume_json["email"]))
    if resume_json.get("phone"):
        contact_parts.append(_safe(resume_json["phone"]))
    if resume_json.get("linkedin_url"):
        url = resume_json["linkedin_url"].replace("https://", "").replace("http://", "").rstrip("/")
        contact_parts.append(_safe(url))
    if resume_json.get("github_url"):
        url = resume_json["github_url"].replace("https://", "").replace("http://", "").rstrip("/")
        contact_parts.append(_safe(url))

    if contact_parts:
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(W, 5, "  |  ".join(contact_parts), ln=True, align="C")
        pdf.set_text_color(0, 0, 0)
    pdf.ln(1)

    # ── Summary ───────────────────────────────────────────────────────────────
    if resume_json.get("summary"):
        section_header("Summary")
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(W, 4.5, _safe(resume_json["summary"]))

    # ── Experience ────────────────────────────────────────────────────────────
    if resume_json.get("experience"):
        section_header("Experience")
        for exp in resume_json["experience"]:
            title_text = _safe(exp.get("title", ""))
            company_text = _safe(exp.get("company", ""))
            start = _safe(exp.get("start_date", ""))
            end = _safe(exp.get("end_date") or "Present")
            date_text = f"{start} - {end}" if start else ""

            pdf.set_font("Helvetica", "B", 9.5)
            pdf.cell(W * 0.72, 5, title_text, ln=False)
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(W * 0.28, 5, date_text, ln=True, align="R")
            pdf.set_text_color(0, 0, 0)

            location_text = _safe(exp.get("location", ""))
            co_line = company_text + (f"  |  {location_text}" if location_text else "")
            pdf.set_font("Helvetica", "I", 8.5)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(W, 4.5, co_line, ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 9)

            for bullet in exp.get("bullets", []):
                pdf.set_x(pdf.l_margin + 3)
                pdf.cell(3, 4.5, "-", ln=False)
                pdf.multi_cell(W - 6, 4.5, _safe(bullet))
            pdf.ln(1.5)

    # ── Skills ────────────────────────────────────────────────────────────────
    skills = resume_json.get("skills", {})
    if skills:
        section_header("Skills")
        rows = [
            ("Technical", ", ".join(skills.get("technical", []))),
            ("Tools", ", ".join(skills.get("tools", []))),
            ("Soft Skills", ", ".join(skills.get("soft", []))),
        ]
        for label, value in rows:
            if value:
                pdf.set_font("Helvetica", "B", 9)
                pdf.cell(22, 4.5, f"{label}:", ln=False)
                pdf.set_font("Helvetica", "", 9)
                pdf.multi_cell(W - 22, 4.5, _safe(value))

    # ── Education ─────────────────────────────────────────────────────────────
    if resume_json.get("education"):
        section_header("Education")
        for edu in resume_json["education"]:
            degree = _safe(edu.get("degree", ""))
            field = _safe(edu.get("field", ""))
            institution = _safe(edu.get("institution", ""))
            year = _safe(edu.get("year", ""))
            degree_line = f"{degree}{' - ' + field if field else ''}"
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(W * 0.72, 5, degree_line, ln=False)
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(W * 0.28, 5, year, ln=True, align="R")
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "I", 8.5)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(W, 4.5, institution, ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(1)

    # ── Certifications ────────────────────────────────────────────────────────
    certs = resume_json.get("certifications", [])
    if certs:
        section_header("Certifications")
        pdf.set_font("Helvetica", "", 9)
        for cert in certs:
            pdf.cell(4, 4.5, "-", ln=False)
            label = cert if isinstance(cert, str) else cert.get("name", str(cert))
            pdf.cell(W - 4, 4.5, _safe(label), ln=True)

    pdf_path = output_path if output_path.endswith(".pdf") else output_path.replace(".html", ".pdf")
    pdf.output(pdf_path)
    return pdf_path


def get_resume_filename(resume_json: dict, job_title: str = "") -> str:
    name = resume_json.get("name", "Candidate").replace(" ", "_")
    role = job_title.replace(" ", "_").replace("/", "_")[:30] if job_title else "Resume"
    return f"{name}_{role}.pdf"
