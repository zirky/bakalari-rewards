from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash
from typing import Optional, List

from .models import CreateBakalariStudent, BakalariStudent

db = Database("ext_bakalari_rewards")


async def create_student(data: CreateBakalariStudent) -> BakalariStudent:
    data.id = urlsafe_short_hash()
    await db.insert("bakalari_rewards.students", data)
    return BakalariStudent(**data.dict())


async def get_student(student_id: str) -> Optional[BakalariStudent]:
    return await db.fetchone(
        "SELECT * FROM bakalari_rewards.students WHERE id = :id",
        {"id": student_id},
        BakalariStudent,
    )


async def get_students(wallet_ids: List[str]) -> List[BakalariStudent]:
    q = ",".join([f"'{w}'" for w in wallet_ids])
    return await db.fetchall(
        f"SELECT * FROM bakalari_rewards.students WHERE wallet IN ({q})",
        model=BakalariStudent,
    )


async def get_all_students() -> List[BakalariStudent]:
    return await db.fetchall(
        "SELECT * FROM bakalari_rewards.students",
        model=BakalariStudent,
    )


async def update_student(data: CreateBakalariStudent) -> BakalariStudent:
    await db.update("bakalari_rewards.students", data)
    return BakalariStudent(**data.dict())


async def delete_student(student_id: str) -> None:
    await db.execute(
        "DELETE FROM bakalari_rewards.students WHERE id = :id",
        {"id": student_id},
    )


async def update_last_check(student_id: str, last_check: str) -> None:
    await db.execute(
        "UPDATE bakalari_rewards.students SET last_check = :last_check WHERE id = :id",
        {"last_check": last_check, "id": student_id},
    )
