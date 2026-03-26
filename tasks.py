import asyncio
import httpx
from datetime import datetime
from loguru import logger

from lnbits.core.crud import get_wallet
from lnbits.core.services import create_payment

from .crud import get_all_students, update_student


GRADE_REWARD_MAP = {
    1: "reward_grade_1",
    2: "reward_grade_2",
    3: "reward_grade_3",
    4: "reward_grade_4",
    5: "reward_grade_5",
}


async def fetch_bakalari_grades(bakalari_url: str, username: str, password: str):
    """Prihlasi se do Bakalaru a vrati seznam znamek od posledniho logu."""
    token_url = bakalari_url.rstrip("/") + "/api/3/auth"
    grades_url = bakalari_url.rstrip("/") + "/api/3/marks"

    async with httpx.AsyncClient(timeout=30) as client:
        # Ziskat access token
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

        # Ziskat znamky
        grades_resp = await client.get(
            grades_url,
            headers={"Authorization": f"Bearer {token}"},
        )
        grades_resp.raise_for_status()
        return grades_resp.json()


async def process_student_grades(student):
    """Zkontroluje nove znamky studenta a posle odmenu."""
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
            # Datum znamky
            mark_date = mark.get("MarkDate") or mark.get("EditDate", "")
            if last_check and mark_date <= last_check:
                continue
            new_marks.append(mark)

        if not new_marks:
            logger.info(f"Student {student.name}: zadne nove znamky")
            return

        wallet = await get_wallet(student.wallet)
        if not wallet:
            logger.warning(f"Penezenka {student.wallet} nenalezena pro studenta {student.name}")
            return

        total_reward = 0
        for mark in new_marks:
            grade_str = mark.get("MarkText", "").strip()
            try:
                grade = int(grade_str)
            except ValueError:
                # Zkusit znamky jako 1-, 2+, apod.
                if grade_str and grade_str[0].isdigit():
                    grade = int(grade_str[0])
                else:
                    logger.info(f"Nerozpoznana znamka: {grade_str}, preskakuji")
                    continue

            reward_field = GRADE_REWARD_MAP.get(grade)
            if reward_field is None:
                logger.info(f"Znamka {grade} neni v rozsahu 1-5, preskakuji")
                continue

            reward_sats = getattr(student, reward_field, 0)
            if reward_sats > 0:
                subject = mark.get("Subject", "Predmet")
                memo = f"Bakalari Odmena: {student.name} - {subject} - znamka {grade}"
                logger.info(f"Posilam {reward_sats} sat studentu {student.name} za znamku {grade} z {subject}")
                try:
                    await create_payment(
                        wallet_id=student.wallet,
                        payment_request=None,
                        payment_hash=None,
                        amount=reward_sats * 1000,  # msat
                        memo=memo,
                        internal=True,
                        source_wallet_id=wallet.id,
                    )
                    total_reward += reward_sats
                except Exception as pay_err:
                    logger.warning(f"Chyba pri platbe pro {student.name}: {pay_err}")

        # Aktualizovat last_check
        from .models import CreateBakalariStudent
        updated_data = CreateBakalariStudent(
            name=student.name,
            wallet=student.wallet,
            bakalari_url=student.bakalari_url,
            bakalari_username=student.bakalari_username,
            bakalari_password=student.bakalari_password,
            reward_grade_1=student.reward_grade_1,
            reward_grade_2=student.reward_grade_2,
            reward_grade_3=student.reward_grade_3,
            reward_grade_4=student.reward_grade_4,
            reward_grade_5=student.reward_grade_5,
            last_check=datetime.utcnow().isoformat(),
        )
        updated_data.id = student.id
        await update_student(updated_data)
        logger.info(f"Student {student.name}: celkova odmena {total_reward} sat")

    except Exception as exc:
        logger.warning(f"Chyba pri zpracovani studenta {student.name}: {exc}")


async def bakalari_rewards_task():
    """Periodicky kontroluje znamky vsech studentu a posilà odmeny."""
    logger.info("Bakalari Rewards task started.")
    while True:
        try:
            students = await get_all_students()
            logger.info(f"Kontroluji znamky pro {len(students)} studentu")
            for student in students:
                await process_student_grades(student)
            await asyncio.sleep(3600)  # Ceka 1 hodinu
        except asyncio.CancelledError:
            logger.info("Bakalari Rewards task cancelled.")
            break
        except Exception as exc:
            logger.warning(f"Bakalari Rewards task error: {exc}")
            await asyncio.sleep(60)
