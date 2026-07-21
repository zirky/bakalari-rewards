from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class PayoutOut(BaseModel):
    id: int
    status: str
    amount_czk: Decimal
    amount_sats: int | None
    btc_czk_rate: Decimal | None
    lightning_address: str | None
    payment_hash: str | None
    created_at: datetime
    paid_at: datetime | None
    error_message: str | None

    class Config:
        from_attributes = True

class PayoutApprove(BaseModel):
    payout_id: int
