import time
from datetime import datetime, timedelta, timezone

from api.app.db import SessionLocal
from api.app.models import Job
from api.app.queues import enqueue_job
from api.app.metrics import jobs_recovered_total

STALE_AFTER_SECONDS = 15
REAPER_INTERVAL_SECONDS = 5
QUEUE_RECOVERY_DELAY_SECONDS = 5

def reap_stale_jobs():
    db = SessionLocal()

    try:
        threshold = datetime.now(timezone.utc) - timedelta(seconds=STALE_AFTER_SECONDS)

        stale_jobs = (
            db.query(Job)
            .filter(
                Job.status == "processing",
                Job.last_heartbeat_at.isnot(None), 
                Job.last_heartbeat_at < threshold
            )
            .with_for_update()
            .all()
        )
        
        recovered_ids = []

        for job in stale_jobs:
            job.status = "queued"
            job.lease_version += 1
            job.owned_by = None
            job.claimed_at = None
            job.updated_at = datetime.now(timezone.utc)
            job.execution_started_at = None
            job.last_heartbeat_at = None
            recovered_ids.append(job.id)

        db.commit()

        for job_id in recovered_ids:
            enqueue_job(job_id)
            jobs_recovered_total.inc()
            print(f"[reaper] re-enqueued stale job {job_id}")

    finally:
        db.close()

def reconcile_queued_jobs():
    db = SessionLocal()

    try:
        threshold = datetime.now(timezone.utc) - timedelta(seconds=QUEUE_RECOVERY_DELAY_SECONDS)

        queued_jobs = (
            db.query(Job)
            .filter(
                Job.status == "queued",
                Job.updated_at < threshold
            )
            .all()
        )

        for job in queued_jobs:
            enqueue_job(job.id)
            print(f"[reaper] re-injected queued job {job.id}")

    finally:
        db.close()
while True:
    print("Reaper started...")
    reap_stale_jobs()
    reconcile_queued_jobs()
    time.sleep(REAPER_INTERVAL_SECONDS)