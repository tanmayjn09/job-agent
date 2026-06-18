import json
import anthropic
from ...config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

OUTREACH_PROMPT = """You are an expert at writing B2B cold outreach that gets responses.

Write a personalized outreach package for this candidate applying to this job.

Rules:
- LinkedIn message: max 300 characters (connection request limit)
- Cold email: 5-7 sentences max, no fluff, lead with value
- Subject line: specific, not generic ("Quick question about [role]" not "Job inquiry")
- Reference something specific about the company/role, not just the job title
- No "I hope this email finds you well" or "I am writing to express my interest"
- Sound like a person, not a cover letter
- Follow-up: 3-day follow-up, 7-day final nudge

Return ONLY valid JSON (no markdown):
{
  "linkedin_connection_note": "",
  "email_subject": "",
  "cold_email": "",
  "follow_up_day3": "",
  "follow_up_day7": "",
  "talking_points": []
}

talking_points: 3-4 specific things from the candidate's background to mention in conversation"""


def generate_outreach(
    candidate_profile: dict,
    job: dict,
    hiring_manager: dict,
    company_context: str = "",
) -> dict:
    profile_str = json.dumps({
        "name": candidate_profile.get("name", ""),
        "current_title": candidate_profile.get("current_title", ""),
        "years_experience": candidate_profile.get("years_experience", 0),
        "strong_areas": candidate_profile.get("strong_areas", []),
        "achievements": candidate_profile.get("achievements", [])[:3],
        "skills": candidate_profile.get("skills", {}),
    }, indent=2)

    context = f"""
CANDIDATE:
{profile_str}

TARGET JOB: {job.get('title', '')} at {job.get('company', '')}
JOB URL: {job.get('url', '')}

HIRING MANAGER: {hiring_manager.get('name', 'Unknown')}
LINKEDIN: {hiring_manager.get('linkedin_url', 'Not found')}

COMPANY CONTEXT:
{company_context or 'No additional context available'}
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": f"{OUTREACH_PROMPT}\n\n{context}"}]
    )

    response_text = message.content[0].text.strip()
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    return json.loads(response_text)
