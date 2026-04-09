from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from uuid import uuid4

from .db import SessionLocal, engine, get_db
from .models import Base, Job
from .schemas import JobRequest
from .queues import enqueue_job

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/jobs")
def create_job(payload: JobRequest, db: Session = Depends(get_db)):
    job_id = str(uuid4)
    
    job = Job(
        id=job_id,
        status="queued"
    )
    
    db.add(job)
    db.commit()
    
    enqueue_job(job_id)
    
    return {"job_id": job_id}

@app.get("/health")
def health():
    return {"status": "ok"}

