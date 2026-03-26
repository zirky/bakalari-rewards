import asyncio
import httpx
from datetime import datetime, timezone
from loguru import logger

from .crud import get_all_students, update_last_check


async def fetch_grades(bakalari_url: str, username: str, password: str):
    """
    Přihlasí se do Bakalářů a vrátí seznam nových známek.
    """
    try:
        async with httpx.AsyncClient(verify=False) as client:
            # Login
            login_url = f"{bakalari_url}/api/3/auth"
            resp = await client.post(login_url, json={
                "client_id": "ANDR",
                "grant_type": "password",
                "username": username,
                "password": password,
            })
            resp.raise_for_status()
            token = resp.json().get("access_token")

            # Znamky
            grades_url = f"{bakalari_url}/api/3/marks"
            headers = {"Authorization": f"Bearer {token}"}
            grades_resp = await client.get(grades_url, headers=headers)
            grades_resp.raise_for_status()
            return grades_resp.json().get("Marks", [])
    except Exception as e:
        logger.error(f"Bakalari fetch error: {e}")
        return []


async def pay_student(wallet_id: str, amount_sats: int, memo: str):
    """
    Odešle interní platbu přes LNbits wallet API.
    """
    try:
        from lnbits.core.services import pay_invoice
        from lnbits.core.crud import get_wallet
        wallet = await get_wallet(wallet_id)
        if not wallet:
            logger.error(f"Wallet {wallet_id} not found")
            return
        logger.info(f"Paying {amount_sats} sats to wallet {wallet_id}: {memo}")
        # TODO: implement actual payment when LN source is configured
    except Exception as e:
        logger.error(f"Payment error: {e}")


async def bakalari_rewards_task():
    """
    Hlavní úloha - spouští se každých 7 dní.
    Zkontroluje Bakaláře a vyplatí žáky za nové známky.
    """
    logger.info("Bakalari Rewards task started.")
    while True:
        try:
            students = await get_all_students()
            logger.info(f"Checking {len(students)} students...")

            for student in students:
                logger.info(f"Processing student: {student.name}")
                grades = await fetch_grades(
                    student.bakalari_url,
                    student.bakalari_username,
                    student.bakalari_password,
                )

                rewards = {
                    1: student.reward_grade_1,
                    2: student.reward_grade_2,
                    3: student.reward_grade_3,
                    4: student.reward_grade_4,
                    5: student.reward_grade_5,
                }

                total_sats = 0
                new_grades = []

                for grade in grades:
                    grade_value = grade.get("MarkText")
                    grade_date = grade.get("MarkDate", "")

                    # Zkontroluj jestli je známka nová (po poslední kontrole)
                    if student.last_check and grade_date < student.last_check:
                        continue

                    try:
                        grade_num = int(grade_value)
                        if 1 <= grade_num <= 5:
                            sats = rewards.get(grade_num, 0)
                            if sats > 0:
                                total_sats += sats
                                new_grades.append(f"{grade_num} ({sats} sats)")
                    except (ValueError, TypeError):
                        continue

                if total_sats > 0:
                    memo = f"Bakalari odměna: {', '.join(new_grades)}"
                    await pay_student(student.wallet, total_sats, memo)
                    logger.info(f"Paid {total_sats} sats to {student.name}")

                now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                await update_last_check(student.id, now)

        except Exception as e:
            logger.error(f"Bakalari Rewards task error: {e}")

        # Čekej 7 dní
        await asyncio.sleep(7 * 24 * 60 * 60)
