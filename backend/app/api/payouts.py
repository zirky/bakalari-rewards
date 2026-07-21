from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import require_parent
from app.models.payout import Payout
from app.schemas.payouts import PayoutOut, PayoutApprove

router = APIRouter(prefix="/payouts", tags=["payouts"])


@router.get("/", response_model=list[PayoutOut])
def list_payouts(db: Session = Depends(get_db), user=Depends(require_parent)):
    return db.query(Payout).order_by(Payout.created_at.desc()).all()


@router.post("/approve")
def approve_payout(req: PayoutApprove, db: Session = Depends(get_db), user=Depends(require_parent)):
    """TODO: schválit pending payout a spustit platbu"""
    payout = db.query(Payout).filter(Payout.id == req.payout_id, Payout.status == "pending").first()
    if not payout:
        return {"error": "Payout not found or not pending"}
    # TODO: volat payment_provider.pay()
    return {"status": "approved", "payout_id": payout.id}
