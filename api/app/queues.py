import redis
from .config import settings
r = redis.Redis(host="redis", port=settings.REDIS_PORT, decode_responses=True)


def enqueue_job(job_id: str):
    r.rpush("jobs", job_id)


def dequeue_job():
    item = r.blpop("jobs")
    return item[1]

def get_queue_depth():
    return r.llen("jobs")