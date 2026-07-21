from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, func
from app.database import Base

class Balance(Base):
    __tablename__ = "balances"
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, unique=True)
    running_balance_czk = Column(Numeric(10, 2), default=0)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
