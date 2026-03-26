import asyncio

from fastapi import APIRouter
from lnbits.tasks import create_permanent_unique_task
from loguru import logger

from .crud import db
from .tasks import bakalari_rewards_task
from .views import bakalari_rewards_generic_router
from .views_api import bakalari_rewards_api_router

logger.debug("Bakalari Rewards extension loaded.")

bakalari_rewards_ext: APIRouter = APIRouter(
    prefix="/bakalari_rewards", tags=["Bakalari Rewards"]
)
bakalari_rewards_ext.include_router(bakalari_rewards_generic_router)
bakalari_rewards_ext.include_router(bakalari_rewards_api_router)

bakalari_rewards_static_files = [
    {
        "path": "/bakalari_rewards/static",
        "name": "bakalari_rewards_static",
    }
]

scheduled_tasks: list[asyncio.Task] = []


def bakalari_rewards_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def bakalari_rewards_start():
    task = create_permanent_unique_task(
        "ext_bakalari_rewards", bakalari_rewards_task
    )
    scheduled_tasks.append(task)


__all__ = [
    "db",
    "bakalari_rewards_ext",
    "bakalari_rewards_start",
    "bakalari_rewards_static_files",
    "bakalari_rewards_stop",
]
