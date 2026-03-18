from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    existing_job = None

    if job.job_url:
        existing_job = db.query(Job).filter(Job.job_url == job.job_url).first()

    if existing_job:
        raise HTTPException(status_code=400, detail="Job with this URL already exists")

    db_job = Job(
        title=job.title,
        company=job.company,
        location=job.location,
        source=job.source,
        job_url=job.job_url,
        description=job.description,
    )

    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.get("", response_model=list[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, updated_job: JobCreate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if updated_job.job_url and updated_job.job_url != job.job_url:
        existing_job = db.query(Job).filter(Job.job_url == updated_job.job_url).first()
        if existing_job:
            raise HTTPException(status_code=400, detail="Another job with this URL already exists")

    job.title = updated_job.title
    job.company = updated_job.company
    job.location = updated_job.location
    job.source = updated_job.source
    job.job_url = updated_job.job_url
    job.description = updated_job.description

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)
    db.commit()

    return {"message": f"Job {job_id} deleted successfully"}