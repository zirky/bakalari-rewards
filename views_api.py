from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from lnbits.core.models import WalletTypeInfo
from lnbits.decorators import require_admin_key, require_invoice_key
from typing import List
import os

from .crud import (
    create_student,
    delete_student,
    get_student,
    get_students,
    update_student,
    get_extension_settings,
    upsert_extension_settings,
)
from .models import (
    CreateBakalariStudent,
    BakalariStudent,
    BakalariStudentPublic,
    CreateExtensionSettings,
)

bakalari_rewards_api_router = APIRouter()


@bakalari_rewards_api_router.get("/api/v1/students", response_model=List[BakalariStudentPublic])
async def api_get_students(wallet: WalletTypeInfo = Depends(require_invoice_key)):
    return await get_students([wallet.wallet.id])


@bakalari_rewards_api_router.post("/api/v1/students", response_model=BakalariStudentPublic)
async def api_create_student(
    data: CreateBakalariStudent,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    data.wallet = wallet.wallet.id
    return await create_student(data)


@bakalari_rewards_api_router.put("/api/v1/students/{student_id}", response_model=BakalariStudentPublic)
async def api_update_student(
    student_id: str,
    data: CreateBakalariStudent,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    student = await get_student(student_id)
    if not student or student.wallet != wallet.wallet.id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Student not found")
    data.id = student_id
    data.wallet = wallet.wallet.id
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


# --- Extension Settings ---

@bakalari_rewards_api_router.get("/api/v1/settings")
async def api_get_settings(wallet: WalletTypeInfo = Depends(require_admin_key)):
    s = await get_extension_settings()
    return {
        "lnbits_api_url": os.environ.get("BAKALARI_REWARDS_LNBITS_API_URL")
            or (s.lnbits_api_url if s else None),
        "api_key_set": bool(
            os.environ.get("BAKALARI_REWARDS_LNBITS_API_KEY")
            or (s.lnbits_api_key_enc if s else None)
        ),
        "payout_enabled": s.payout_enabled if s else True,
        "dry_run": s.dry_run if s else False,
        "max_sats_per_run": s.max_sats_per_run if s else 1_000_000,
        "allow_insecure_tls": s.allow_insecure_tls if s else False,
        "managed_by_env": {
            "lnbits_api_url": bool(os.environ.get("BAKALARI_REWARDS_LNBITS_API_URL")),
            "lnbits_api_key": bool(os.environ.get("BAKALARI_REWARDS_LNBITS_API_KEY")),
            "dry_run": bool(os.environ.get("BAKALARI_REWARDS_DRY_RUN")),
        },
    }


@bakalari_rewards_api_router.put("/api/v1/settings")
async def api_update_settings(
    data: CreateExtensionSettings,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    return await upsert_extension_settings(data)
