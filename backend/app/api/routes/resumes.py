import json
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.candidate import Candidate
from ...models.job import Job
from ...models.resume import TailoredResume
from ...schemas.resume import TailorResumeRequest, TailoredResumeResponse
from ...services.resume_tailor import extract_jd_keywords, tailor_resume
from ...services.pdf_generator import generate_pdf, get_resume_filename
from ...config import settings

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


@router.post("/tailor", response_model=TailoredResumeResponse)
def tailor_resume_endpoint(request: TailorResumeRequest, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    profile = json.loads(candidate.profile_json) if candidate.profile_json else {}
    if candidate.github_url:
        profile["github_url"] = candidate.github_url
    if candidate.linkedin_url:
        profile["linkedin_url"] = candidate.linkedin_url
    if candidate.portfolio_url:
        profile["portfolio_url"] = candidate.portfolio_url

    resume_record = TailoredResume(
        candidate_id=candidate.id,
        job_id=job.id,
        status="processing",
    )
    db.add(resume_record)
    db.flush()

    try:
        description = request.extra_description or job.description or ""
        job_dict = {
            "title": job.title,
            "company": job.company,
            "description": description,
            "location": job.location,
        }

        keywords = extract_jd_keywords(description)
        tailored = tailor_resume(profile, job_dict, keywords)

        resume_record.content_json = json.dumps(tailored)
        resume_record.ats_keywords = json.dumps(keywords)

        upload_dir = Path(settings.upload_dir) / "resumes"
        upload_dir.mkdir(parents=True, exist_ok=True)
        filename = get_resume_filename(tailored, job.title)
        output_path = str(upload_dir / f"{resume_record.id}_{filename}")

        pdf_path = generate_pdf(tailored, output_path)
        resume_record.pdf_path = pdf_path
        resume_record.status = "complete"

    except Exception as e:
        resume_record.status = "error"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

    db.commit()
    db.refresh(resume_record)

    return TailoredResumeResponse(
        id=resume_record.id,
        candidate_id=resume_record.candidate_id,
        job_id=resume_record.job_id,
        content_json=resume_record.content_json,
        ats_keywords=resume_record.ats_keywords,
        status=resume_record.status,
        created_at=resume_record.created_at,
        pdf_ready=bool(resume_record.pdf_path),
    )


@router.get("/{resume_id}/download")
def download_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(TailoredResume).filter(TailoredResume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not resume.pdf_path or not os.path.exists(resume.pdf_path):
        raise HTTPException(status_code=404, detail="PDF not generated yet")

    filename = Path(resume.pdf_path).name
    media_type = "application/pdf" if resume.pdf_path.endswith(".pdf") else "text/html"
    return FileResponse(path=resume.pdf_path, filename=filename, media_type=media_type)


@router.get("/{resume_id}", response_model=TailoredResumeResponse)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(TailoredResume).filter(TailoredResume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return TailoredResumeResponse(
        id=resume.id,
        candidate_id=resume.candidate_id,
        job_id=resume.job_id,
        content_json=resume.content_json,
        ats_keywords=resume.ats_keywords,
        status=resume.status,
        created_at=resume.created_at,
        pdf_ready=bool(resume.pdf_path),
    )
