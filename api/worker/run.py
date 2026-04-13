import time
from uuid import uuid4

from api.app.queues import dequeue_job
from .worker import claim_job, fail_job, complete_job

worker_id = f"worker-{uuid4().hex[:6]}"

while True:
    print(f"[{worker_id}] waiting for jobs..")
    
    item = dequeue_job()
    
    time.sleep(5)
  
    job_id = item
    
    lease_version = claim_job(job_id, worker_id)
    
    if not lease_version:
        continue