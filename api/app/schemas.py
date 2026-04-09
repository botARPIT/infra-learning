from pydantic import BaseModel

class JobRequest(BaseModel):
    task: str