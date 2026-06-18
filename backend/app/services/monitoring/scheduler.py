"""
Background job monitoring agent.
Runs every 6 hours, discovers new jobs for active candidates,
creates alerts for matches above threshold.
"""
import json
import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from ...database import SessionLocal
from ...models.candidate import Candidate
from ...models.job import Job, JobMatch
from ..crawlers.aggregator import crawl_all_sources
from ..match_scorer import score_job
from .alert_manager import create_alert

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()
MATCH_THRESHOLD = 65


async def run_monitoring_cycle():
    logger.info(f"Monitoring cycle started at {datetime.utcnow()}")
    db: Session = SessionLocal()
    try:
        candidates = db.query(Candidate).filter(
            Candidate.profile_json.isnot(None)
        ).all()

        for candidate in candidates:
            try:
                await _process_candidate(db, candidate)
            except Exception as e:
                logger.error(f"Error processing candidate {candidate.id}: {e}")
    finally:
        db.close()
    logger.info("Monitoring cycle complete")


async def _process_candidate(db: Session, candidate: Candidate):
    profile = json.loads(candidate.profile_json)
    expectations = json.loads(candidate.expectations_json or "{}")

    query = expectations.get("target_role") or profile.get("current_title", "Software Engineer")
    locations = expectations.get("locations", [])
    remote = expectations.get("remote_preference") == "remote"

    raw_jobs = await crawl_all_sources(
        query=query,
        locations=locations,
        remote=remote if remote else None,
    )

    existing_urls = set(
        url for (url,) in db.query(Job.url).join(JobMatch).filter(
            JobMatch.candidate_id == candidate.id
        ).all()
    )

    new_jobs = [j for j in raw_jobs if j.get("url") not in existing_urls]

    for job_data in new_jobs[:20]:
        try:
            scored = score_job(profile, job_data.get("description", ""), job_data.get("title", ""))
            if scored.get("match_score", 0) < MATCH_THRESHOLD:
                continue

            job = Job(
                title=job_data.get("title", ""),
                company=job_data.get("company", ""),
                location=job_data.get("location", ""),
                description=job_data.get("description", ""),
                url=job_data.get("url", ""),
                source=job_data.get("source", ""),
                posted_at=job_data.get("posted_at", ""),
                remote=job_data.get("remote", False),
                employment_type=job_data.get("employment_type", ""),
            )
            db.add(job)
            db.flush()

            match = JobMatch(
                candidate_id=candidate.id,
                job_id=job.id,
                match_score=scored.get("match_score", 0),
                match_reasoning=scored.get("reasoning", ""),
                skill_matches=json.dumps(scored.get("skill_matches", [])),
                skill_gaps=json.dumps(scored.get("skill_gaps", [])),
            )
            db.add(match)
            db.flush()

            create_alert(
                db=db,
                candidate_id=candidate.id,
                job_id=job.id,
                match_score=scored.get("match_score", 0),
                alert_type="new_match",
            )
        except Exception as e:
            logger.error(f"Error processing job for candidate {candidate.id}: {e}")
            continue

    db.commit()


def start_scheduler():
    scheduler.add_job(run_monitoring_cycle, "interval", hours=6, id="monitoring_cycle", replace_existing=True)
    scheduler.start()
    logger.info("Monitoring scheduler started - runs every 6 hours")


def stop_scheduler():
    scheduler.shutdown(wait=False)
