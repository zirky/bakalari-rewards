"""APScheduler — týdenní sync job."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

scheduler = AsyncIOScheduler()


async def run_sync_job(db: Session | None = None):
    """Hlavní sync logika — TODO: implementovat plný workflow.
    
    Kroky:
    1. Pro každé dítě načíst BakalariAccount z DB
    2. Zavolat bakalari_client.fetch_marks(since=last_sync)
    3. Uložit nové známky (idempotentně)
    4. reward_engine.compute_czk_change()
    5. reward_engine.decide_payout()
    6. Pokud payout: vytvořit Payout(status=pending)
    7. Pokud auto_payout=True: spustit platbu přes payment_provider
    8. Uložit SyncRun + Balance
    """
    print("[scheduler] sync job spuštěn")
    # TODO: implementovat


def start_scheduler():
    scheduler.add_job(
        run_sync_job,
        trigger=CronTrigger(day_of_week='sun', hour=8, minute=0),
        id='weekly_sync',
        replace_existing=True,
    )
    scheduler.start()
    print("[scheduler] nastaven týdenní sync (neděle 08:00)")
