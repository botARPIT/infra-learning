import time
from uuid import uuid4

from api.app.queues import dequeue_job
from .worker import claim_job, fail_job, complete_job


worker_id = f"worker-{uuid4().hex[:6]}"


while True:
    print(f"[{worker_id}] waiting for jobs..")

    job_id = dequeue_job()

    lease_version = claim_job(job_id, worker_id)

    if not lease_version:
        print(f"[{worker_id}] stale queue signal skipped {job_id}")
        continue

    try:
        print(f"[{worker_id}] claimed {job_id}")

        time.sleep(5)
        
        success = complete_job(job_id, lease_version, worker_id)

        if success:
            print(f"[{worker_id}] completed {job_id}")
        else:
            print(f"[{worker_id}] stale completion discarded {job_id}")


    except Exception as e:
        fail_job(job_id, lease_version, worker_id, str(e))
        print(f"[{worker_id}] failed {job_id}")