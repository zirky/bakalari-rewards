import asyncio
from loguru import logger

from .crud import get_all_students


async def bakalari_rewards_task():
    """Periodicky kontroluje stav - placeholder pro budouci funkce."""
    logger.info("Bakalari Rewards task started.")
    while True:
        try:
            await asyncio.sleep(3600)  # Ceka 1 hodinu
        except asyncio.CancelledError:
            logger.info("Bakalari Rewards task cancelled.")
            break
        except Exception as exc:
            logger.warning(f"Bakalari Rewards task error: {exc}")
            await asyncio.sleep(60)
