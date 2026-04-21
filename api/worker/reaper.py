import time
from datetime import datetime, timedelta, timezone

from api.app.db import SessionLocal
from api.app.models import Job
from api.app.queues import enqueue_job


STALE_AFTER_SECONDS = 15
REAPER_INTERVAL_SECONDS = 5


def reap_stale_jobs():
    db = SessionLocal()

    try:
        threshold = datetime.now(timezone.utc) - timedelta(seconds=STALE_AFTER_SECONDS)

        stale_jobs = (
            db.query(Job)
            .filter(
                Job.status == "processing",
                Job.claimed_at < threshold
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

            recovered_ids.append(job.id)

        db.commit()

        for job_id in recovered_ids:
            enqueue_job(job_id)
            print(f"[reaper] re-enqueued stale job {job_id}")

    finally:
        db.close()


while True:
    reap_stale_jobs()
    time.sleep(REAPER_INTERVAL_SECONDS)