from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("parents.id"))
    action = Column(String(128), nullable=False)
    detail = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
