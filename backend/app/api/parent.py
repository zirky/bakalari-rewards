from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import require_parent

router = APIRouter(prefix="/parent", tags=["parent"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user=Depends(require_parent)):
    """TODO: vrátit ParentDashboard"""
    return {"child_name": "", "running_balance_czk": 0, "last_sync_at": None, "pending_payouts_count": 0}


@router.get("/settings")
def get_settings(db: Session = Depends(get_db), user=Depends(require_parent)):
    """TODO: vrátit nastavení sazeb a LN adresy"""
    return {}


@router.put("/settings")
def update_settings(db: Session = Depends(get_db), user=Depends(require_parent)):
    """TODO: uložit nastavení"""
    return {"status": "ok"}
