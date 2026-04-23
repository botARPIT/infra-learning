from sqlalchemy import Column, String, Integer, DateTime, Text, Enum as SAEnum
from datetime import datetime, timezone
from enum import Enum
from .db import Base



class Job(Base):
    __tablename__ = "jobs"

    id            = Column(String, primary_key=True)

    status        = Column(String, nullable=False)

    result        = Column(Text, nullable=True)
    error         = Column(Text, nullable=True)

    retry_count   = Column(Integer, default=0, nullable=False)
    lease_version = Column(Integer, default=0, nullable=False)

    owned_by      = Column(String, nullable=True)

    created_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    claimed_at    = Column(DateTime(timezone=True), nullable=True)
    execution_started_at = Column(DateTime(timezone=True), nullable=True)
    last_heartbeat_at = Column(DateTime(timezone=True), nullable=True)