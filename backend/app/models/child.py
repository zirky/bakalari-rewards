from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from app.database import Base

class Child(Base):
    __tablename__ = "children"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)
    lightning_address = Column(String(255))
    auto_payout = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
