from api.app.db import SessionLocal
from api.app.models import Job
from api.app.queues import enqueue_job


def recover_queued_jobs():
    db = SessionLocal()
    try:
        queued_jobs = db.query(Job).filter(Job.status == "queued").all()

        for job in queued_jobs:
            enqueue_job(job.id)

        print(f"[startup] recovered {len(queued_jobs)} queued jobs")
    finally:
        db.close()