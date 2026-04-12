from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

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
        
def complete_job(job_id: str, lease_version: int):
    db = SessionLocal()
    
    try:
        job = db.query(Job).filter(
            Job.id == job_id,
            Job.lease_version == lease_version
        ).first()
        
        if not job:
            print("stale worker rejected")
            return False
        
        job.status = "done"
        job.result = "finished"
        db.commit()
        return True
    
    finally:
        db.close()
        
def fail_job(job_id: str, lease_version: int, error: str):
    db = SessionLocal()
    
    try:
        job = db.query(Job).filter(
            Job.id == job_id,
            Job.lease_version == lease_version
        ).first()
        
        if not job:
            return False
        
        job.status = "failed"
        job.error = error
        
        db.commit()
        return True
    
    finally:
        db.close()