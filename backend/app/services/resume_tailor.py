import json
import anthropic
from ..config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

KEYWORD_EXTRACTION_PROMPT = """Extract ATS keywords from this job description.

Return ONLY valid JSON (no markdown):
{
  "required_keywords": [],
  "preferred_keywords": [],
  "role_keywords": [],
  "industry_keywords": []
}

required_keywords: skills/tools explicitly required
preferred_keywords: skills mentioned as "nice to have" or "preferred"
role_keywords: action verbs and role-specific terms
industry_keywords: industry/domain specific terms"""

TAILORING_PROMPT = """You are an expert ATS resume writer with 15 years of experience helping candidates get past applicant tracking systems and impress human recruiters.

Your task: Rewrite the candidate's resume to be perfectly tailored for the specific job below.

HARD RULES:
1. Every bullet must follow: Action Verb + What You Did + Measurable Result
2. No weak phrases: "responsible for", "helped with", "worked on", "assisted with", "involved in"
3. Mirror EXACT keywords from the JD naturally - do not force them awkwardly
4. All ATS keywords must appear at least once in the resume body
5. Keep the candidate's authentic voice - do not make it sound generic
6. Summary: 3 sentences max. Start with the target job title. Front-load keywords.
7. Only include skills the candidate actually has - never fabricate
8. Quantify everything possible. If no number exists, add context ("across 5 teams", "for 200+ users")

Return ONLY valid JSON (no markdown):
{
  "summary": "",
  "experience": [
    {
      "title": "",
      "company": "",
      "location": "",
      "start_date": "",
      "end_date": "",
      "bullets": []
    }
  ],
  "skills": {
    "technical": [],
    "tools": [],
    "soft": []
  },
  "education": [
    {
      "degree": "",
      "field": "",
      "institution": "",
      "year": ""
    }
  ],
  "certifications": [],
  "ats_score_estimate": 0,
  "keywords_used": []
}"""


def extract_jd_keywords(job_description: str) -> dict:
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"{KEYWORD_EXTRACTION_PROMPT}\n\nJOB DESCRIPTION:\n{job_description[:4000]}"
            }
        ]
    )
    response_text = message.content[0].text.strip()
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])
    return json.loads(response_text)


def tailor_resume(candidate_profile: dict, job: dict, keywords: dict) -> dict:
    profile_str = json.dumps(candidate_profile, indent=2)
    keywords_str = json.dumps(keywords, indent=2)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=6000,
        messages=[
            {
                "role": "user",
                "content": (
                    f"{TAILORING_PROMPT}\n\n"
                    f"TARGET JOB: {job.get('title', '')} at {job.get('company', '')}\n\n"
                    f"JOB DESCRIPTION:\n{job.get('description', '')[:4000]}\n\n"
                    f"ATS KEYWORDS TO INCLUDE:\n{keywords_str}\n\n"
                    f"CANDIDATE'S ORIGINAL PROFILE:\n{profile_str}"
                )
            }
        ]
    )

    response_text = message.content[0].text.strip()
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    result = json.loads(response_text)
    result["name"] = candidate_profile.get("name", "")
    result["email"] = candidate_profile.get("email", "")
    result["phone"] = candidate_profile.get("phone", "")
    result["target_job"] = f"{job.get('title', '')} at {job.get('company', '')}"
    result["github_url"] = candidate_profile.get("github_url", "")
    result["linkedin_url"] = candidate_profile.get("linkedin_url", "")
    result["portfolio_url"] = candidate_profile.get("portfolio_url", "")
    return result
