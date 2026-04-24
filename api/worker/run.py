import time
from uuid import uuid4
import signal
import sys
from api.app.queues import dequeue_job
from .worker import claim_job, fail_job, complete_job, mark_execution_started, heartbeat

DEQUE_TIMEOUT_SECONDS = 2

shutdown_requested = False
worker_id = f"worker-{uuid4().hex[:6]}"

def handle_shutdown(signum, frame):
    global shutdown_requested
    shutdown_requested = True
    print(f"[{worker_id}] shutdown requested ")

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)
while not shutdown_requested:
    print(f"[{worker_id}] waiting for jobs..")

    job_id = dequeue_job(timeout=DEQUE_TIMEOUT_SECONDS)
    if not job_id:
        continue

    lease_version = claim_job(job_id, worker_id)
    
    

    if not lease_version:
        print(f"[{worker_id}] stale queue signal skipped {job_id}")
        continue

    try:
        print(f"[{worker_id}] claimed {job_id}")
        
        execution_started = mark_execution_started(job_id, lease_version, worker_id)
        if execution_started:
            print(f"[{worker_id}] started executing {job_id}")
        else:
            print(f"[{worker_id}] was unable to execute {job_id}")
            continue
        
        lease_alive = True
        for _ in range(5):
            
            if not heartbeat(job_id, lease_version, worker_id):
                lease_alive = False
                print(f"[{worker_id}] lease lost during execution")
                break
            
            if shutdown_requested:
                print(f"[{worker_id}] shutdown requested, finishing current job")
                break
            time.sleep(1)
        if not lease_alive:
            continue
        
        
        success = complete_job(job_id, lease_version, worker_id)

        if success:
            print(f"[{worker_id}] completed {job_id}")
        else:
            print(f"[{worker_id}] stale completion discarded {job_id}")


    except Exception as e:
        fail_job(job_id, lease_version, worker_id, str(e))
        print(f"[{worker_id}] failed {job_id}")
        
print(f"[{worker_id}] exiting cleanly")
sys.exit(0)