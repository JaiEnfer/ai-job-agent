from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.application import Application

router = APIRouter(prefix="/application-summary", tags=["application-summary"])


@router.get("")
def get_application_summary(db: Session = Depends(get_db)):
    applications = db.query(Application).all()

    total = len(applications)
    status_counts = Counter((app.status or "unknown").lower() for app in applications)

    return {
        "total_applications": total,
        "status_breakdown": dict(status_counts),
    }