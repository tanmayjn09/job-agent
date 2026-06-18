import json
import asyncio
import anthropic
from ..config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

SCORING_PROMPT = """You are an expert recruiter scoring candidate-job fit.

Given the candidate profile and job description below, return ONLY valid JSON (no markdown):
{
  "match_score": 0,
  "reasoning": "",
  "skill_matches": [],
  "skill_gaps": [],
  "seniority_fit": "",
  "domain_fit": ""
}

Scoring criteria (0-100):
- 40 points: Required skills present (technical skills, tools, domain knowledge)
- 25 points: Seniority alignment (years of experience vs role expectations)
- 20 points: Industry/domain overlap
- 15 points: Title and role relevance

skill_matches: list of candidate skills that match the JD
skill_gaps: list of required skills from JD that the candidate lacks
seniority_fit: "strong", "acceptable", "overqualified", "underqualified"
domain_fit: "strong", "related", "adjacent", "unrelated"
reasoning: 2-3 sentence explanation of the score"""


def score_job(candidate_profile: dict, job_description: str, job_title: str = "") -> dict:
    profile_str = json.dumps(candidate_profile, indent=2)

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"{SCORING_PROMPT}\n\nCANDIDATE PROFILE:\n{profile_str}\n\nJOB TITLE: {job_title}\n\nJOB DESCRIPTION:\n{job_description[:3000]}"
            }
        ]
    )

    response_text = message.content[0].text.strip()
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    result = json.loads(response_text)
    result["match_score"] = max(0, min(100, float(result.get("match_score", 0))))
    return result


async def score_job_async(candidate_profile: dict, job: dict) -> dict:
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        score_job,
        candidate_profile,
        job.get("description", ""),
        job.get("title", ""),
    )
    return {**job, **result}


async def batch_score_jobs(candidate_profile: dict, jobs: list[dict]) -> list[dict]:
    tasks = [score_job_async(candidate_profile, job) for job in jobs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    scored = []
    for r in results:
        if isinstance(r, Exception):
            continue
        scored.append(r)
    scored.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return scored
