from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

class ParentDashboard(BaseModel):
    child_name: str
    running_balance_czk: Decimal
    last_sync_at: datetime | None
    pending_payouts_count: int

class ChildDashboard(BaseModel):
    child_name: str
    running_balance_czk: Decimal
    estimated_sats: int | None
    last_sync_at: datetime | None
    total_paid_sats: int
