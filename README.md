# Job Agent

AI-powered job discovery and ATS-optimized resume tailoring. Upload your resume, get ranked job matches, generate tailored resumes per application.

## How it works

1. **Upload resume** - Claude extracts your full profile: skills, experience, achievements, strong areas
2. **Set expectations** - target role, location, seniority, salary, remote preference
3. **Search jobs** - pulls from Google Jobs (via SerpAPI) + LinkedIn, scores each against your profile
4. **Tailor resume** - Claude rewrites your resume with ATS keywords from the specific JD, keeps your authentic voice

## Stack

- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: React + Tailwind + Vite
- **AI**: Claude API (Anthropic) for resume parsing, job scoring, resume tailoring
- **Job Search**: SerpAPI (Google Jobs aggregation) + LinkedIn scraping fallback

## Setup

### 1. Clone and configure

```bash
git clone https://github.com/tanmayjn09/job-agent.git
cd job-agent
```

### 2. Backend

```bash
cd backend
# Requires Python 3.12 (3.14 not yet supported by all dependencies)
# macOS: brew install python@3.12
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your API keys:
#   ANTHROPIC_API_KEY=sk-ant-...
#   SERPAPI_KEY=your_serpapi_key (get free key at serpapi.com)
```

Start the backend:
```bash
uvicorn app.main:app --reload
```

API docs available at: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

## API Keys Required

| Key | Where to get | Free tier |
|-----|-------------|-----------|
| `ANTHROPIC_API_KEY` | console.anthropic.com | Pay-as-you-go |
| `SERPAPI_KEY` | serpapi.com | 100 searches/month free |

## API Endpoints

```
POST /api/candidates/onboard     - Upload resume + build profile
GET  /api/candidates/{id}        - Get candidate
PATCH /api/candidates/{id}       - Update profile/expectations
GET  /api/candidates/{id}/dashboard - Dashboard data

POST /api/jobs/search            - Search + score jobs
GET  /api/jobs/{id}              - Job detail + match breakdown

POST /api/resumes/tailor         - Generate ATS-optimized resume
GET  /api/resumes/{id}           - Resume detail
GET  /api/resumes/{id}/download  - Download PDF
```

## Notes

- Job search uses SerpAPI (Google Jobs) as primary source. If no SerpAPI key, falls back to LinkedIn scraping.
- Candidate files stored in `/uploads` directory - never committed to git.
- SQLite database stored at `backend/job_agent.db` - not committed.
- Resume PDFs require WeasyPrint. Falls back to HTML if WeasyPrint not installed.

## WeasyPrint (PDF generation)

WeasyPrint requires system dependencies:

```bash
# macOS
brew install pango

# Ubuntu/Debian  
sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0
```
