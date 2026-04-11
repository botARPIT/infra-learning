from sqlalchemy import Column, String, Integer, DateTime, Text
from datetime import datetime
from .db import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)

    status = Column(String, nullable=False)

    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)

    retry_count = Column(Integer, default=0, nullable=False)
    lease_version = Column(Integer, default=0, nullable=False)

    owned_by = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    claimed_at = Column(DateTime, nullable=True)
    
# TODO: Change update at to: updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow), use enum for states