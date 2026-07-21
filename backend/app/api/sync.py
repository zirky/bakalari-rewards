from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import require_parent
from app.scheduler.jobs import run_sync_job

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/run")
def trigger_sync(background_tasks: BackgroundTasks,
                db: Session = Depends(get_db),
                user=Depends(require_parent)):
    """Ruční spuštění synchronizace."""
    background_tasks.add_task(run_sync_job, db)
    return {"status": "sync started"}


@router.get("/history")
def sync_history(db: Session = Depends(get_db), user=Depends(require_parent)):
    """TODO: vrátit historii sync_runs"""
    return []
