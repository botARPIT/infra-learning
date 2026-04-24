import redis
from .config import settings
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)



def ping_redis():
    return r.ping()

def enqueue_job(job_id: str):
    r.rpush("jobs", job_id)


def dequeue_job(timeout = 2):
    item = r.blpop("jobs", timeout=timeout)
    if not item:
        return None
    
    _, job_id = item
    
    return job_id.decode()

def get_queue_depth():
    return r.llen("jobs")