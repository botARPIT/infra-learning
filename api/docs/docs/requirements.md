# Async Job Processing Service Requirements

## Functional Requirements

1. Client submits a job using POST /jobs
2. System returns unique job_id immediately
3. Worker processes job asynchronouslys
4. Client checks job state using GET /jobs/{id}

## Non-Functional Requirements (SLOs)

1. 95% of POST /jobs requests complete under 300ms
2. 99% of POST /jobs requests succeed during 1 hour test window
3. 90% of jobs complete within 15 seconds
4. Worker crash recovery occurs within 30 seconds

## Initial Constraints

1. Single machine deployment allowed
2. PostgreSQL required for persistence
3. Redis required for queue
4. No authentication in initial version

# Initial Architecture Decision

## Components

1. FastAPI API service
2. PostgreSQL persistence layer
3. Redis queue
4. Worker process

## Request Flow

1. Client submits request
2. API validates input
3. API writes job row into PostgreSQL
4. API enqueues job_id into Redis
5. API returns response immediately

## Processing Flow

1. Worker waits on Redis queue
2. Worker receives job_id
3. Worker processes job
4. Worker updates PostgreSQL status/result

## Reasoning

This separates request latency from processing latency, allowing request SLO to remain under 300ms while background work may take longer.
