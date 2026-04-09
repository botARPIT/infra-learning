from sqlalchemy import Column, String
from .db import Base

class Job(Base):
    __tablename__= "jobs"
    
    id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    result = Column(String, nullable=True)