from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db
from .api.routes import candidates, jobs, resumes, outreach, alerts
from .services.monitoring.scheduler import start_scheduler, stop_scheduler

app = FastAPI(
    title="Job Agent API",
    description="AI-powered job discovery and resume tailoring",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(candidates.router)
app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(outreach.router)
app.include_router(alerts.router)


@app.on_event("startup")
def startup():
    init_db()
    start_scheduler()


@app.on_event("shutdown")
def shutdown():
    stop_scheduler()


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}
