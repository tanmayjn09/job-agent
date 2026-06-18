import os
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates"


def generate_pdf(resume_json: dict, output_path: str) -> str:
    try:
        from weasyprint import HTML, CSS
        use_weasyprint = True
    except ImportError:
        use_weasyprint = False

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("resume.html")
    html_content = template.render(resume=resume_json)

    html_path = output_path.replace(".pdf", ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    if use_weasyprint:
        HTML(filename=html_path).write_pdf(output_path)
        os.remove(html_path)
        return output_path
    else:
        return html_path


def get_resume_filename(resume_json: dict, job_title: str = "") -> str:
    name = resume_json.get("name", "Candidate").replace(" ", "_")
    role = job_title.replace(" ", "_").replace("/", "_")[:30] if job_title else "Resume"
    return f"{name}_{role}.pdf"
