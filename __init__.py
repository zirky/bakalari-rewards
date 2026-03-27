import asyncio

from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from lnbits.db import Database
from lnbits.helpers import template_renderer
from lnbits.tasks import create_permanent_unique_task

from .crud import (
    create_student,
    delete_student,
    get_student,
    get_students,
    update_student, # Přidáno
)
from .models import BakalariStudent, CreateBakalariStudent
from .tasks import bakalari_rewards_task
from .views import bakalari_rewards_generic_router

db = Database("ext_bakalari_rewards")

# Definice API routeru
bakalari_rewards_api_router = APIRouter()

# --- API ENDPOINTY ---

@bakalari_rewards_api_router.get("/api/v1/students", response_model=list[BakalariStudent])
async def api_students(wallet=Depends(get_key_type)):
    return await get_students([wallet.wallet.id])

@bakalari_rewards_api_router.post("/api/v1/students", response_model=BakalariStudent)
async def api_student_create(data: CreateBakalariStudent, wallet=Depends(get_key_type)):
    data.wallet = wallet.wallet.id
    return await create_student(data)

# NOVÝ ENDPOINT PRO EDITACI
@bakalari_rewards_api_router.put("/api/v1/students/{student_id}", response_model=BakalariStudent)
async def api_student_update(
    student_id: str,
    data: CreateBakalariStudent,
    wallet=Depends(get_key_type)
):
    student = await get_student(student_id)
    if not student:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Student nebyl nalezen.")
    
    if student.wallet != wallet.wallet.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Nejste majitelem tohoto záznamu.")

    return await update_student(student_id, data)

@bakalari_rewards_api_router.delete("/api/v1/students/{student_id}")
async def api_student_delete(student_id: str, wallet=Depends(get_key_type)):
    student = await get_student(student_id)
    if not student:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Student nebyl nalezen.")

    if student.wallet != wallet.wallet.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Nejste majitelem tohoto záznamu.")

    await delete_student(student_id)
    return "", HTTPStatus.NO_CONTENT

# --- REGISTRACE DOPLŇKU ---

bakalari_rewards_ext: APIRouter = APIRouter(
    prefix="/bakalari_rewards", tags=["Bakalari Rewards"]
)
bakalari_rewards_ext.include_router(bakalari_rewards_generic_router)
bakalari_rewards_ext.include_router(bakalari_rewards_api_router)

def bakalari_rewards_renderer():
    return template_renderer(["bakalari_rewards/templates"])

# Spuštění tasku na pozadí
tasks: list[asyncio.Task] = []

def bakalari_rewards_start():
    task = create_permanent_unique_task("bakalari_rewards", bakalari_rewards_task)
    tasks.append(task)

def bakalari_rewards_stop():
    for task in tasks:
        try:
            task.cancel()
        except Exception:
            pass

__all__ = [
    "bakalari_rewards_ext",
    "bakalari_rewards_start",
    "bakalari_rewards_stop",
]
