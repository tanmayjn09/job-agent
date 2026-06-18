import json
import os
import shutil
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.candidate import Candidate, CandidateFile
from ...models.job import JobMatch
from ...models.resume import TailoredResume
from ...schemas.candidate import CandidateOnboardResponse, CandidateProfileUpdate, CandidateResponse, DashboardResponse
from ...services.profile_builder import build_profile, extract_text_from_file
from ...config import settings

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


@router.post("/onboard", response_model=CandidateOnboardResponse)
async def onboard_candidate(
    resume: UploadFile = File(...),
    expectations: str = Form("{}"),
    github_url: Optional[str] = Form(None),
    linkedin_url: Optional[str] = Form(None),
    portfolio_url: Optional[str] = Form(None),
    about_text: Optional[str] = Form(None),
    extra_files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
):
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    candidate = Candidate(
        github_url=github_url,
        linkedin_url=linkedin_url,
        portfolio_url=portfolio_url,
        about_text=about_text,
    )
    db.add(candidate)
    db.flush()

    resume_ext = Path(resume.filename).suffix
    resume_path = upload_dir / f"resume_{candidate.id}{resume_ext}"
    with open(resume_path, "wb") as f:
        shutil.copyfileobj(resume.file, f)
    candidate.resume_file_path = str(resume_path)

    resume_text = extract_text_from_file(str(resume_path))
    candidate.raw_resume_text = resume_text

    extra_context_parts = []
    if about_text:
        extra_context_parts.append(f"Candidate's own description: {about_text}")
    if github_url:
        extra_context_parts.append(f"GitHub: {github_url}")
    if linkedin_url:
        extra_context_parts.append(f"LinkedIn: {linkedin_url}")
    if portfolio_url:
        extra_context_parts.append(f"Portfolio: {portfolio_url}")

    if extra_files:
        for ef in extra_files:
            if not ef.filename:
                continue
            ef_ext = Path(ef.filename).suffix
            ef_path = upload_dir / f"file_{candidate.id}_{ef.filename}"
            with open(ef_path, "wb") as f:
                shutil.copyfileobj(ef.file, f)
            ef_text = extract_text_from_file(str(ef_path))

            candidate_file = CandidateFile(
                candidate_id=candidate.id,
                file_path=str(ef_path),
                file_type=ef_ext,
                original_filename=ef.filename,
                extracted_text=ef_text,
            )
            db.add(candidate_file)
            if ef_text:
                extra_context_parts.append(f"Additional file ({ef.filename}):\n{ef_text[:2000]}")

    profile = build_profile(resume_text, "\n".join(extra_context_parts))

    candidate.name = profile.get("name", "")
    candidate.email = profile.get("email", "")
    candidate.phone = profile.get("phone", "")
    candidate.profile_json = json.dumps(profile)

    try:
        exp_data = json.loads(expectations)
    except Exception:
        exp_data = {}
    candidate.expectations_json = json.dumps(exp_data)

    db.commit()
    db.refresh(candidate)

    return CandidateOnboardResponse(
        id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        profile_json=candidate.profile_json,
        message="Profile built successfully",
    )


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.patch("/{candidate_id}", response_model=CandidateResponse)
def update_candidate(candidate_id: int, update: CandidateProfileUpdate, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    for field, value in update.model_dump(exclude_none=True).items():
        setattr(candidate, field, value)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("/{candidate_id}/dashboard")
def get_dashboard(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    matches = db.query(JobMatch).filter(JobMatch.candidate_id == candidate_id).all()
    resumes = db.query(TailoredResume).filter(TailoredResume.candidate_id == candidate_id).all()

    avg_score = sum(m.match_score for m in matches) / len(matches) if matches else 0

    recent_matches = []
    for m in sorted(matches, key=lambda x: x.created_at or 0, reverse=True)[:5]:
        recent_matches.append({
            "id": m.id,
            "job_id": m.job_id,
            "job_title": m.job.title if m.job else "",
            "company": m.job.company if m.job else "",
            "match_score": m.match_score,
        })

    recent_resumes = []
    for r in sorted(resumes, key=lambda x: x.created_at or 0, reverse=True)[:5]:
        recent_resumes.append({
            "id": r.id,
            "job_id": r.job_id,
            "job_title": r.job.title if r.job else "",
            "company": r.job.company if r.job else "",
            "status": r.status,
            "pdf_ready": bool(r.pdf_path),
        })

    return {
        "candidate": {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "profile_json": candidate.profile_json,
            "expectations_json": candidate.expectations_json,
            "github_url": candidate.github_url,
            "linkedin_url": candidate.linkedin_url,
            "portfolio_url": candidate.portfolio_url,
            "about_text": candidate.about_text,
            "created_at": candidate.created_at,
        },
        "total_job_matches": len(matches),
        "total_resumes_generated": len(resumes),
        "avg_match_score": round(avg_score, 1),
        "recent_matches": recent_matches,
        "recent_resumes": recent_resumes,
    }
