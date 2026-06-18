import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.candidate import Candidate
from ...models.job import Job, JobMatch
from ...schemas.job import JobSearchFilters, JobSearchResponse, JobMatchResponse, JobResponse
from ...services.job_discovery import discover_jobs
from ...services.match_scorer import batch_score_jobs

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(filters: JobSearchFilters, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == filters.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    profile = json.loads(candidate.profile_json) if candidate.profile_json else {}
    expectations = json.loads(candidate.expectations_json) if candidate.expectations_json else {}

    query = filters.query or expectations.get("target_role") or profile.get("current_title", "Software Engineer")
    locations = filters.locations or expectations.get("locations") or []
    remote = filters.remote if filters.remote is not None else (expectations.get("remote_preference") == "remote")
    date_posted = filters.date_posted or "month"
    employment_type = filters.employment_type or (
        expectations.get("employment_types", ["full-time"])[0] if expectations.get("employment_types") else None
    )

    raw_jobs = discover_jobs(
        query=query,
        locations=locations,
        remote=remote if remote else None,
        date_posted=date_posted,
        employment_type=employment_type,
        num_per_source=filters.per_page,
    )

    scored_jobs = await batch_score_jobs(profile, raw_jobs)

    saved_matches = []
    for sj in scored_jobs:
        job = Job(
            title=sj.get("title", ""),
            company=sj.get("company", ""),
            location=sj.get("location", ""),
            description=sj.get("description", ""),
            url=sj.get("url", ""),
            source=sj.get("source", ""),
            posted_at=sj.get("posted_at", ""),
            remote=sj.get("remote", False),
            employment_type=sj.get("employment_type", ""),
        )
        db.add(job)
        db.flush()

        match = JobMatch(
            candidate_id=candidate.id,
            job_id=job.id,
            match_score=sj.get("match_score", 0),
            match_reasoning=sj.get("reasoning", ""),
            skill_matches=json.dumps(sj.get("skill_matches", [])),
            skill_gaps=json.dumps(sj.get("skill_gaps", [])),
        )
        db.add(match)
        saved_matches.append((job, match))

    db.commit()

    page = filters.page or 1
    per_page = filters.per_page or 20
    start = (page - 1) * per_page
    end = start + per_page
    page_matches = saved_matches[start:end]

    response_matches = []
    for job, match in page_matches:
        db.refresh(job)
        db.refresh(match)
        response_matches.append(JobMatchResponse(
            id=match.id,
            job=JobResponse(
                id=job.id,
                title=job.title,
                company=job.company,
                location=job.location,
                description=job.description,
                url=job.url,
                source=job.source,
                posted_at=job.posted_at,
                remote=job.remote or False,
                seniority=job.seniority,
                industry=job.industry,
                employment_type=job.employment_type,
            ),
            match_score=match.match_score,
            match_reasoning=match.match_reasoning,
            skill_matches=match.skill_matches,
            skill_gaps=match.skill_gaps,
            created_at=match.created_at,
        ))

    return JobSearchResponse(
        matches=response_matches,
        total=len(saved_matches),
        page=page,
        per_page=per_page,
    )


@router.get("/{job_id}")
def get_job(job_id: int, candidate_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    match = db.query(JobMatch).filter(
        JobMatch.job_id == job_id,
        JobMatch.candidate_id == candidate_id
    ).first()

    return {
        "job": {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "url": job.url,
            "source": job.source,
            "posted_at": job.posted_at,
            "remote": job.remote,
            "employment_type": job.employment_type,
        },
        "match": {
            "match_score": match.match_score if match else None,
            "match_reasoning": match.match_reasoning if match else None,
            "skill_matches": json.loads(match.skill_matches) if match and match.skill_matches else [],
            "skill_gaps": json.loads(match.skill_gaps) if match and match.skill_gaps else [],
        } if match else None
    }
