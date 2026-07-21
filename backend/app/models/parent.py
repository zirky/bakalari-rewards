from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class Parent(Base):
    __tablename__ = "parents"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
