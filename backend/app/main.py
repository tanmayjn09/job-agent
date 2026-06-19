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
    _migrate_db()
    start_scheduler()


def _migrate_db():
    from .database import engine
    from sqlalchemy import inspect, text
    try:
        inspector = inspect(engine)
        cols = [c["name"] for c in inspector.get_columns("job_matches")]
        with engine.connect() as conn:
            if "is_applied" not in cols:
                conn.execute(text("ALTER TABLE job_matches ADD COLUMN is_applied BOOLEAN DEFAULT FALSE"))
            if "applied_at" not in cols:
                conn.execute(text("ALTER TABLE job_matches ADD COLUMN applied_at TIMESTAMP"))
            conn.commit()
    except Exception:
        pass


@app.on_event("shutdown")
def shutdown():
    stop_scheduler()


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}
