from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey, func
from app.database import Base

class Payout(Base):
    __tablename__ = "payouts"
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    sync_run_id = Column(Integer, ForeignKey("sync_runs.id"))
    status = Column(String(32), default="pending")  # pending|processing|paid|failed|cancelled
    amount_czk = Column(Numeric(10, 2), nullable=False)
    amount_sats = Column(Integer)
    btc_czk_rate = Column(Numeric(16, 2))
    lightning_address = Column(String(255))
    payment_hash = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
