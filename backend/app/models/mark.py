from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, UniqueConstraint
from app.database import Base

class Mark(Base):
    __tablename__ = "marks"
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    sync_run_id = Column(Integer, ForeignKey("sync_runs.id"))
    subject = Column(String(128), nullable=False)
    mark_text = Column(String(16), nullable=False)
    mark_numeric = Column(Integer)
    mark_date = Column(DateTime(timezone=True), nullable=False)
    reward_czk = Column(Numeric(10, 2), default=0)
    processed = Column(Boolean, default=False)
    __table_args__ = (
        UniqueConstraint("child_id", "subject", "mark_text", "mark_date", name="uq_mark_idempotent"),
    )
