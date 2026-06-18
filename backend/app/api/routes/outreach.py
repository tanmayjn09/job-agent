import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.candidate import Candidate
from ...models.job import Job
from ...models.outreach import OutreachDraft
from ...services.outreach.recruiter_finder import find_hiring_manager
from ...services.outreach.email_finder import find_email, extract_domain_from_url
from ...services.outreach.message_generator import generate_outreach
from ...services.signals.crunchbase import get_funding_signal
from ...services.signals.company_health import get_company_health

router = APIRouter(prefix="/api/outreach", tags=["outreach"])


@router.post("/generate")
async def generate_outreach_endpoint(
    candidate_id: int,
    job_id: int,
    db: Session = Depends(get_db),
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    profile = json.loads(candidate.profile_json) if candidate.profile_json else {}

    hiring_manager = await find_hiring_manager(job.company or "", job.title or "")

    email_data = {}
    if hiring_manager.get("name"):
        parts = hiring_manager["name"].split()
        first = parts[0] if parts else ""
        last = parts[-1] if len(parts) > 1 else ""
        domain = extract_domain_from_url(job.url or "")
        email_data = await find_email(domain, first, last)

    funding = await get_funding_signal(job.company or "")
    health = await get_company_health(job.company or "")

    company_context = []
    if funding.get("latest_news"):
        company_context.append(f"Recent news: {funding['latest_news']}")
    if funding.get("last_funding_type"):
        company_context.append(f"Last funding: {funding['last_funding_type']}")
    if health.get("glassdoor_rating"):
        company_context.append(f"Glassdoor: {health['glassdoor_rating']}/5")
    if health.get("recent_layoffs"):
        company_context.append("Note: company had recent layoffs")

    job_dict = {"title": job.title, "company": job.company, "url": job.url, "description": job.description}
    messages = generate_outreach(profile, job_dict, hiring_manager, "\n".join(company_context))

    draft = OutreachDraft(
        candidate_id=candidate_id,
        job_id=job_id,
        hiring_manager_name=hiring_manager.get("name", ""),
        hiring_manager_linkedin=hiring_manager.get("linkedin_url", ""),
        hiring_manager_email=email_data.get("email", ""),
        email_confidence=email_data.get("confidence", 0),
        linkedin_note=messages.get("linkedin_connection_note", ""),
        email_subject=messages.get("email_subject", ""),
        cold_email=messages.get("cold_email", ""),
        follow_up_day3=messages.get("follow_up_day3", ""),
        follow_up_day7=messages.get("follow_up_day7", ""),
        talking_points=json.dumps(messages.get("talking_points", [])),
        company_signals=json.dumps({"funding": funding, "health": health}),
        status="draft",
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)

    return {
        "id": draft.id,
        "hiring_manager": {
            "name": draft.hiring_manager_name,
            "linkedin_url": draft.hiring_manager_linkedin,
            "email": draft.hiring_manager_email,
            "email_confidence": draft.email_confidence,
        },
        "messages": {
            "linkedin_note": draft.linkedin_note,
            "email_subject": draft.email_subject,
            "cold_email": draft.cold_email,
            "follow_up_day3": draft.follow_up_day3,
            "follow_up_day7": draft.follow_up_day7,
        },
        "talking_points": json.loads(draft.talking_points or "[]"),
        "company_signals": json.loads(draft.company_signals or "{}"),
    }


@router.get("/{draft_id}")
def get_outreach(draft_id: int, db: Session = Depends(get_db)):
    draft = db.query(OutreachDraft).filter(OutreachDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Outreach draft not found")
    return {
        "id": draft.id,
        "hiring_manager": {
            "name": draft.hiring_manager_name,
            "linkedin_url": draft.hiring_manager_linkedin,
            "email": draft.hiring_manager_email,
            "email_confidence": draft.email_confidence,
        },
        "messages": {
            "linkedin_note": draft.linkedin_note,
            "email_subject": draft.email_subject,
            "cold_email": draft.cold_email,
            "follow_up_day3": draft.follow_up_day3,
            "follow_up_day7": draft.follow_up_day7,
        },
        "talking_points": json.loads(draft.talking_points or "[]"),
        "company_signals": json.loads(draft.company_signals or "{}"),
        "status": draft.status,
    }


@router.get("/candidate/{candidate_id}")
def list_outreach(candidate_id: int, db: Session = Depends(get_db)):
    drafts = db.query(OutreachDraft).filter(OutreachDraft.candidate_id == candidate_id).all()
    return [{"id": d.id, "job_id": d.job_id, "hiring_manager_name": d.hiring_manager_name,
             "status": d.status, "created_at": d.created_at} for d in drafts]
