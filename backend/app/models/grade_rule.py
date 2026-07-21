from sqlalchemy import Column, Integer, Numeric, ForeignKey
from app.database import Base

class GradeRule(Base):
    __tablename__ = "grade_rules"
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    grade = Column(Integer, nullable=False)
    reward_czk = Column(Numeric(10, 2), nullable=False, default=0)
