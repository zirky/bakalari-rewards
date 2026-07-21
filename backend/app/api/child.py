from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import require_child

router = APIRouter(prefix="/child", tags=["child"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user=Depends(require_child)):
    """TODO: vrátit ChildDashboard (read-only)"""
    return {"child_name": "", "running_balance_czk": 0, "estimated_sats": None, "last_sync_at": None, "total_paid_sats": 0}


@router.get("/marks")
def get_marks(db: Session = Depends(get_db), user=Depends(require_child)):
    """TODO: vrátit seznam známek dítěte"""
    return []


@router.get("/payouts")
def get_payouts(db: Session = Depends(get_db), user=Depends(require_child)):
    """TODO: vrátit historii payoutů dítěte"""
    return []
