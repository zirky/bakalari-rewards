from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash
from typing import Optional, List

from .models import CreateBakalariStudent, BakalariStudent

db = Database("ext_bakalari_rewards")


async def create_student(data: CreateBakalariStudent) -> BakalariStudent:
    student_id = urlsafe_short_hash()
    student = BakalariStudent(
        id=student_id,
        name=data.name,
        wallet=data.wallet,
        bakalari_url=data.bakalari_url,
        bakalari_username=data.bakalari_username,
        bakalari_password=data.bakalari_password,
        reward_grade_1=data.reward_grade_1,
        reward_grade_2=data.reward_grade_2,
        reward_grade_3=data.reward_grade_3,
        reward_grade_4=data.reward_grade_4,
        reward_grade_5=data.reward_grade_5,
        last_check=data.last_check,
        use_czk=data.use_czk,
        reward_grade_1_czk=data.reward_grade_1_czk,
        reward_grade_2_czk=data.reward_grade_2_czk,
        reward_grade_3_czk=data.reward_grade_3_czk,
        reward_grade_4_czk=data.reward_grade_4_czk,
        reward_grade_5_czk=data.reward_grade_5_czk,
        check_period=data.check_period,
    )
    await db.insert("bakalari_rewards.students", student)
    return student


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


async def delete_student(student_id: str) -> None:
    await db.execute(
        "DELETE FROM bakalari_rewards.students WHERE id = :id",
        {"id": student_id},
    )


async def update_student(data: CreateBakalariStudent) -> Optional[BakalariStudent]:
    await db.execute(
        """
        UPDATE bakalari_rewards.students SET
            name = :name,
            wallet = :wallet,
            bakalari_url = :bakalari_url,
            bakalari_username = :bakalari_username,
            bakalari_password = :bakalari_password,
            reward_grade_1 = :reward_grade_1,
            reward_grade_2 = :reward_grade_2,
            reward_grade_3 = :reward_grade_3,
            reward_grade_4 = :reward_grade_4,
            reward_grade_5 = :reward_grade_5,
            use_czk = :use_czk,
            reward_grade_1_czk = :reward_grade_1_czk,
            reward_grade_2_czk = :reward_grade_2_czk,
            reward_grade_3_czk = :reward_grade_3_czk,
            reward_grade_4_czk = :reward_grade_4_czk,
            reward_grade_5_czk = :reward_grade_5_czk,
            check_period = :check_period
        WHERE id = :id
        """,
        {
            "id": data.id,
            "name": data.name,
            "wallet": data.wallet,
            "bakalari_url": data.bakalari_url,
            "bakalari_username": data.bakalari_username,
            "bakalari_password": data.bakalari_password,
            "reward_grade_1": data.reward_grade_1,
            "reward_grade_2": data.reward_grade_2,
            "reward_grade_3": data.reward_grade_3,
            "reward_grade_4": data.reward_grade_4,
            "reward_grade_5": data.reward_grade_5,
            "use_czk": data.use_czk,
            "reward_grade_1_czk": data.reward_grade_1_czk,
            "reward_grade_2_czk": data.reward_grade_2_czk,
            "reward_grade_3_czk": data.reward_grade_3_czk,
            "reward_grade_4_czk": data.reward_grade_4_czk,
            "reward_grade_5_czk": data.reward_grade_5_czk,
            "check_period": data.check_period,
        },
    )
    return await get_student(data.id)


async def update_student_last_check(student_id: str, last_check: str) -> None:
    await db.execute(
        """
        UPDATE bakalari_rewards.students SET last_check = :last_check WHERE id = :id
        """,
        {"id": student_id, "last_check": last_check},
    )


# ---- Processed marks (deduplication) ----

async def get_processed_mark(student_id: str, mark_hash: str) -> bool:
    """Vrati True pokud jiz byla tato znamka zpracovana."""
    row = await db.fetchone(
        "SELECT 1 FROM bakalari_rewards.processed_marks WHERE student_id = :sid AND mark_hash = :mh",
        {"sid": student_id, "mh": mark_hash},
    )
    return row is not None


async def save_processed_mark(student_id: str, mark_hash: str) -> None:
    """Ulozi zaznam o zpracovane znamce."""
    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    await db.execute(
        """
        INSERT OR IGNORE INTO bakalari_rewards.processed_marks
            (student_id, mark_hash, processed_at)
        VALUES (:sid, :mh, :ts)
        """,
        {"sid": student_id, "mh": mark_hash, "ts": now_iso},
    )
