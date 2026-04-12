from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

from api.app.db import SessionLocal
from api.app.models import Job

def claim_job(job_id: str, worker_id: str):
    db = SessionLocal()

    try:
        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .with_for_update()
            .first()
        )

        if not job:
            return None

        if job.status != "queued":
            return None

        job.status = "processing"
        job.owned_by = worker_id
        job.claimed_at = datetime.utcnow()
        job.lease_version += 1

        db.commit()

        return job.lease_version

    finally:
        db.close()
        
def complete_job(job_id: str, lease_version: int, worker_id: str):
    db = SessionLocal()
    
    try:
        job = db.query(Job).filter(
            Job.id == job_id,
            Job.lease_version == lease_version,
            Job.status == "processing",
            Job.owned_by == worker_id
        ).first()
        
        if not job:
            print("stale worker rejected")
            return False
        
        job.status = "done"
        job.result = "finished"
        job.updated_at = datetime.now(timezone.utc)
        job.error = None
        db.commit()
        return True
    
    finally:
        db.close()
        
def fail_job(job_id: str, lease_version: int, worker_id: str, error: str):
    db = SessionLocal()
    
    try:
        job = db.query(Job).filter(
            Job.id == job_id,
            Job.lease_version == lease_version,
            Job.owned_by == worker_id,
            Job.status == "processing"
        ).first()
        
        if not job:
            return False
        
        job.status = "failed"
        job.error = error
        job.result = None
        job.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        return True
    
    finally:
        db.close()