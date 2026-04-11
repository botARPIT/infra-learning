from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from uuid import uuid4

from .db import SessionLocal, engine, get_db
from .models import Base, Job
from .schemas import JobRequest
from .queues import enqueue_job

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/jobs", status_code=202)
def create_job(payload: JobRequest, db: Session = Depends(get_db)):
    job_id = str(uuid4())

    job = Job(
        id=job_id,
        status="queued",
        retry_count=0,
        lease_version=0
    )

    db.add(job)
    db.commit()

    try:
        enqueue_job(job_id)
        return {
            "job_id": job_id,
            "status": "queued"
        }

    except Exception as e:
        job.status = "enqueue_failed"
        job.error = str(e)

        db.commit()

        return {
            "job_id": job_id,
            "status": "delayed"
        }

@app.get("/health")
def health():
    return {"status": "ok"}

