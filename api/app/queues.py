import redis

r = redis.Redis(host="redis", port=6381, decode_responses=True)

def enqueue_job(job_id: str):
    r.rpush("jobs", job_id)