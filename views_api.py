from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from lnbits.core.models import WalletTypeInfo
from lnbits.decorators import require_admin_key, require_invoice_key
from typing import List

from .crud import (
    create_student,
    delete_student,
    get_student,
    get_students,
    update_student,
)
from .models import CreateBakalariStudent, BakalariStudent

bakalari_rewards_api_router = APIRouter()


@bakalari_rewards_api_router.get("/api/v1/students", response_model=List[BakalariStudent])
async def api_get_students(wallet: WalletTypeInfo = Depends(require_invoice_key)):
    return await get_students([wallet.wallet.id])


@bakalari_rewards_api_router.post("/api/v1/students", response_model=BakalariStudent)
async def api_create_student(
    data: CreateBakalariStudent,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    data.wallet = wallet.wallet.id
    return await create_student(data)


@bakalari_rewards_api_router.put("/api/v1/students/{student_id}", response_model=BakalariStudent)
async def api_update_student(
    student_id: str,
    data: CreateBakalariStudent,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    student = await get_student(student_id)
    if not student or student.wallet != wallet.wallet.id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Student not found")
    data.id = student_id
    return await update_student(data)


@bakalari_rewards_api_router.delete("/api/v1/students/{student_id}")
async def api_delete_student(
    student_id: str,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    student = await get_student(student_id)
    if not student or student.wallet != wallet.wallet.id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Student not found")
    await delete_student(student_id)
    return "", HTTPStatus.NO_CONTENT
