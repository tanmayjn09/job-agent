from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.alert import Alert
from ...services.monitoring.alert_manager import get_unread_alerts, mark_read, mark_all_read

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/{candidate_id}")
def get_alerts(candidate_id: int, db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(
        Alert.candidate_id == candidate_id
    ).order_by(Alert.created_at.desc()).limit(50).all()

    return [
        {
            "id": a.id,
            "alert_type": a.alert_type,
            "match_score": a.match_score,
            "is_read": a.is_read,
            "created_at": a.created_at,
            "job": {
                "id": a.job.id,
                "title": a.job.title,
                "company": a.job.company,
                "location": a.job.location,
                "url": a.job.url,
            } if a.job else None,
        }
        for a in alerts
    ]


@router.get("/{candidate_id}/unread-count")
def unread_count(candidate_id: int, db: Session = Depends(get_db)):
    count = db.query(Alert).filter(
        Alert.candidate_id == candidate_id,
        Alert.is_read == False,
    ).count()
    return {"count": count}


@router.patch("/{alert_id}/read")
def read_alert(alert_id: int, db: Session = Depends(get_db)):
    mark_read(db, alert_id)
    return {"ok": True}


@router.patch("/{candidate_id}/read-all")
def read_all(candidate_id: int, db: Session = Depends(get_db)):
    mark_all_read(db, candidate_id)
    return {"ok": True}
