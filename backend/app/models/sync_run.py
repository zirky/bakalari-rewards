from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.database import Base

class SyncRun(Base):
    __tablename__ = "sync_runs"
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))
    status = Column(String(32), default="running")
    new_marks_count = Column(Integer, default=0)
    error_message = Column(Text)
