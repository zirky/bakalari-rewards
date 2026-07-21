from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class MarkOut(BaseModel):
    id: int
    subject: str
    mark_text: str
    mark_numeric: int | None
    mark_date: datetime
    reward_czk: Decimal
    processed: bool

    class Config:
        from_attributes = True
