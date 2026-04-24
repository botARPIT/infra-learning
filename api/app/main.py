from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from uuid import uuid4

from .db import SessionLocal, engine, get_db, ping_db
from .models import Base, Job
from .schemas import JobRequest
from .queues import enqueue_job, ping_redis
from .metrics import get_metrics, get_prometheus_metrics
from fastapi.responses import Response
from .config import settings
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    Base.metadata.create_all(bind=engine)
    yield
    # shutdown
    engine.dispose()

app = FastAPI(lifespan=lifespan)


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

@app.get("/ready")
def ready():
    
    try:
        ping_db()
        ping_redis()
        
        return {"status": "ready"}
    
    except Exception as e:
        return {
            "status": "not ready",
            "reason": str(e)
        }
              
        
@app.get("/debug-metrics")
def debug_metrics():
    return get_metrics()

@app.get("/metrics")
def prometheus_metrics():
    return Response(
        get_prometheus_metrics(),
        media_type="text/plain"
    )

@app.get("/jobs/{job_id}")
def status(job_id: str):
    db = SessionLocal()
    
    try:
        job = db.query(Job).filter(
            Job.id == job_id
        ).first()
        
        if not job:
            return {"status": "Job not found"}
        
        return {"status": job.status}
    
    finally:
        db.close()
        
        

