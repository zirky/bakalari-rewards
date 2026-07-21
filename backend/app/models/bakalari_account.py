from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database import Base

class BakalariAccount(Base):
    __tablename__ = "bakalari_accounts"
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    base_url = Column(String(255), nullable=False)
    username = Column(String(128), nullable=False)
    encrypted_password = Column(Text, nullable=False)
