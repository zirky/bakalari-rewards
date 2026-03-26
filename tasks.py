import asyncio
import httpx
from datetime import datetime, timezone
from loguru import logger

from .crud import get_all_students, update_student_last_check


GRADE_REWARD_MAP = {
    1: "reward_grade_1",
    2: "reward_grade_2",
    3: "reward_grade_3",
    4: "reward_grade_4",
    5: "reward_grade_5",
}


async def fetch_bakalari_grades(bakalari_url: str, username: str, password: str):
    """Prihlasi se do Bakalaru a vrati seznam znamek."""
    base = bakalari_url.rstrip("/")
    token_url = base + "/api/3/auth"
    grades_url = base + "/api/3/marks"

    async with httpx.AsyncClient(timeout=30, verify=False) as client:
        resp = await client.post(
            token_url,
            data={
                "client_id": "ANDR",
                "grant_type": "password",
                "username": username,
                "password": password,
            },
        )
        resp.raise_for_status()
        token = resp.json().get("access_token")
        if not token:
            raise ValueError("Nepodarilo se ziskat access token z Bakalaru")

        grades_resp = await client.get(
            grades_url,
            headers={"Authorization": f"Bearer {token}"},
        )
        grades_resp.raise_for_status()
        return grades_resp.json()


async def send_reward(wallet_id: str, amount_sats: int, memo: str):
    """Prida satoshi na LNbits penezni ucet studenta (interni kredit)."""
    try:
        from lnbits.core.crud import get_wallet
        from lnbits.db import Database

        # Pouzijeme interni DB pro primy update zustatku
        core_db = Database("database")
        await core_db.execute(
            """
            UPDATE wallets SET balance = balance + :amount
            WHERE id = :wallet_id
            """,
            {"wallet_id": wallet_id, "amount": amount_sats * 1000},
        )
        logger.info(f"Odmena {amount_sats} sat pridana na penezni ucet {wallet_id}: {memo}")
    except Exception as e:
        logger.warning(f"Chyba pri pridani odmeny: {e}")


async def process_student_grades(student):
    """Zkontroluje nove znamky studenta a posle odmeny."""
    try:
        grades_data = await fetch_bakalari_grades(
            student.bakalari_url,
            student.bakalari_username,
            student.bakalari_password,
        )
        marks = grades_data.get("Marks", [])
        last_check = student.last_check

        new_marks = []
        for mark in marks:
            mark_date = mark.get("MarkDate") or mark.get("EditDate", "")
            if last_check and mark_date and mark_date <= last_check:
                continue
            new_marks.append(mark)

        if not new_marks:
            logger.info(f"Student {student.name}: zadne nove znamky")
            return

        for mark in new_marks:
            grade_str = str(mark.get("MarkText", "")).strip()
            grade = None
            if grade_str and grade_str[0].isdigit():
                grade = int(grade_str[0])

            if grade is None or grade not in GRADE_REWARD_MAP:
                continue

            reward_field = GRADE_REWARD_MAP[grade]
            reward_sats = getattr(student, reward_field, 0)
            if reward_sats > 0:
                subject = mark.get("Subject", "")
                memo = f"Bakalari odmena: {student.name} - {subject} - znamka {grade}"
                await send_reward(student.wallet, reward_sats, memo)

        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        await update_student_last_check(student.id, now_iso)
        logger.info(f"Student {student.name}: last_check aktualizovan")

    except Exception as exc:
        logger.warning(f"Chyba pri zpracovani studenta {student.name}: {exc}")


async def bakalari_rewards_task():
    """Periodicky kontroluje znamky vsech studentu a posila odmeny."""
    logger.info("Bakalari Rewards task started.")
    while True:
        try:
            students = await get_all_students()
            logger.info(f"Kontroluji znamky pro {len(students)} studentu")
            for student in students:
                await process_student_grades(student)
            await asyncio.sleep(3600)
        except asyncio.CancelledError:
            logger.info("Bakalari Rewards task cancelled.")
            break
        except Exception as exc:
            logger.warning(f"Bakalari Rewards task error: {exc}")
            await asyncio.sleep(60)
