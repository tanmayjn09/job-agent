from sqlalchemy.orm import Session
from ...models.alert import Alert


def create_alert(
    db: Session,
    candidate_id: int,
    job_id: int,
    match_score: float,
    alert_type: str = "new_match",
) -> Alert:
    alert = Alert(
        candidate_id=candidate_id,
        job_id=job_id,
        match_score=match_score,
        alert_type=alert_type,
    )
    db.add(alert)
    db.flush()
    return alert


def get_unread_alerts(db: Session, candidate_id: int) -> list[Alert]:
    return db.query(Alert).filter(
        Alert.candidate_id == candidate_id,
        Alert.is_read == False,
    ).order_by(Alert.created_at.desc()).all()


def mark_read(db: Session, alert_id: int) -> None:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.is_read = True
        db.commit()


def mark_all_read(db: Session, candidate_id: int) -> None:
    db.query(Alert).filter(
        Alert.candidate_id == candidate_id,
        Alert.is_read == False,
    ).update({"is_read": True})
    db.commit()
