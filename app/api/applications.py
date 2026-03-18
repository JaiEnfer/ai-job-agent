from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.models.candidate_profile import CandidateProfile
from app.models.application_package import ApplicationPackage
from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationResponse
from app.schemas.application_update import ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationResponse)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    profile = db.query(CandidateProfile).filter(CandidateProfile.id == payload.profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    if payload.application_package_id is not None:
        package = (
            db.query(ApplicationPackage)
            .filter(ApplicationPackage.id == payload.application_package_id)
            .first()
        )
        if not package:
            raise HTTPException(status_code=404, detail="Application package not found")

    db_application = Application(
        job_id=payload.job_id,
        profile_id=payload.profile_id,
        application_package_id=payload.application_package_id,
        status=payload.status or "draft",
        application_channel=payload.application_channel,
        external_application_id=payload.external_application_id,
        recruiter_name=payload.recruiter_name,
        recruiter_email=payload.recruiter_email,
        notes=payload.notes,
        response_notes=payload.response_notes,
    )

    if (payload.status or "draft").lower() == "applied":
        db_application.applied_at = datetime.now(timezone.utc)

    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    return db_application


@router.get("", response_model=list[ApplicationResponse])
def list_applications(db: Session = Depends(get_db)):
    applications = db.query(Application).order_by(Application.created_at.desc()).all()
    return applications

@router.get("/status/{status}", response_model=list[ApplicationResponse])
def list_applications_by_status(status: str, db: Session = Depends(get_db)):
    applications = (
        db.query(Application)
        .filter(Application.status.ilike(status))
        .order_by(Application.created_at.desc())
        .all()
    )
    return applications

@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == application_id).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    return application


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
):
    application = db.query(Application).filter(Application.id == application_id).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "application_package_id" in update_data and update_data["application_package_id"] is not None:
        package = (
            db.query(ApplicationPackage)
            .filter(ApplicationPackage.id == update_data["application_package_id"])
            .first()
        )
        if not package:
            raise HTTPException(status_code=404, detail="Application package not found")

    previous_status = (application.status or "").lower()

    for field, value in update_data.items():
        setattr(application, field, value)

    new_status = (application.status or "").lower()
    if previous_status != "applied" and new_status == "applied" and application.applied_at is None:
        application.applied_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(application)

    return application


@router.delete("/{application_id}")
def delete_application(application_id: int, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == application_id).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    db.delete(application)
    db.commit()

    return {"message": f"Application {application_id} deleted successfully"}