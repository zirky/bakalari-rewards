import asyncio
import hashlib
import httpx
from datetime import datetime, timedelta, timezone
from loguru import logger

from lnbits.core.models import CreateInvoice
from lnbits.core.services import create_invoice, pay_invoice
from lnbits.core.crud import get_wallet

from .crud import (
    get_all_students,
    update_student_last_check,
    get_processed_mark,
    save_processed_mark,
)


GRADE_REWARD_MAP = {
    1: "reward_grade_1",
    2: "reward_grade_2",
    3: "reward_grade_3",
    4: "reward_grade_4",
    5: "reward_grade_5",
}


def mark_hash(student_id: str, mark: dict) -> str:
    """Vytvori unikatni hash pro kazdou znamku pro deduplication."""
    raw = f"{student_id}:{mark.get('Id', '')}:{mark.get('MarkDate', '')}:{mark.get('MarkText', '')}:{mark.get('Subject', '')}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


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


async def send_reward(wallet_id: str, amount_sats: int, memo: str) -> bool:
    """Posle satoshi na LNbits penezni ucet studenta pres interni invoice."""
    try:
        # 1) Zkontrolujeme ze cilova penezenka existuje
        wallet = await get_wallet(wallet_id)
        if not wallet:
            logger.warning(f"Penezenka {wallet_id} neexistuje, odmena preskocena")
            return False

        # 2) Vytvorime invoice pro cilovou penezenku studenta
        invoice = await create_invoice(
            wallet_id=wallet_id,
            amount=amount_sats,
            memo=memo,
            internal=True,
        )
        payment_request = invoice.bolt11

        # 3) Zaplatime invoice z teze penezenky (interni kredit - bez LN poplatku)
        # Pro interni prevod ze stejne penezenky (odmena se prida jako kredit)
        # Pouzijeme admin wallet penezenky studenta
        await pay_invoice(
            wallet_id=wallet_id,
            payment_request=payment_request,
            max_sat=amount_sats + 1,
            extra={"tag": "bakalari_rewards"},
        )

        logger.info(f"Odmena {amount_sats} sat pridana na penezenku {wallet_id}: {memo}")
        return True
    except Exception as e:
        logger.warning(f"Chyba pri posilani odmeny na {wallet_id}: {e}")
        return False


def should_check_student(student) -> bool:
    """Rozhodne jestli je cas zkontrolovat znamky studenta podle check_period."""
    if student.last_check is None:
        return True

    now = datetime.now(timezone.utc)
    lc = student.last_check
    if lc.tzinfo is None:
        lc = lc.replace(tzinfo=timezone.utc)

    period = getattr(student, "check_period", "weekly")
    if period == "monthly":
        delta = timedelta(days=30)
    else:
        # weekly je vychozi
        delta = timedelta(days=7)

    return (now - lc) >= delta


async def process_student_grades(student):
    """Zkontroluje nove znamky studenta a posle odmeny."""
    try:
        # Zkontrolujeme jestli uz je cas na kontrolu
        if not should_check_student(student):
            logger.debug(f"Student {student.name}: prilis brzy na dalsi kontrolu, preskakuji")
            return

        grades_data = await fetch_bakalari_grades(
            student.bakalari_url,
            student.bakalari_username,
            student.bakalari_password,
        )

        marks = grades_data.get("Marks", [])
        last_check = student.last_check

        new_marks = []
        for mark in marks:
            mark_date_str = mark.get("MarkDate") or mark.get("EditDate", "")
            if last_check and mark_date_str:
                try:
                    mark_dt_str = mark_date_str[:19]  # "2025-03-01T12:00:00"
                    mark_dt = datetime.strptime(mark_dt_str, "%Y-%m-%dT%H:%M:%S")
                    lc = last_check.replace(tzinfo=None) if last_check.tzinfo else last_check
                    if mark_dt <= lc:
                        continue
                except Exception:
                    pass  # Pokud se datum nepodarilo parsovat, znamku zahrneme

            # Deduplication: zkontrolujeme jestli uz tuto znamku nezpracovavame
            mhash = mark_hash(student.id, mark)
            already_processed = await get_processed_mark(student.id, mhash)
            if already_processed:
                logger.debug(f"Student {student.name}: znamka {mhash} jiz zpracovana, preskakuji")
                continue

            new_marks.append((mark, mhash))

        if not new_marks:
            logger.info(f"Student {student.name}: zadne nove znamky")
            # Aktualizujeme last_check i kdyz nejsou nove znamky
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            await update_student_last_check(student.id, now_iso)
            return

        rewards_sent = 0
        for mark, mhash in new_marks:
            grade_str = str(mark.get("MarkText", "")).strip()
            grade = None
            if grade_str and grade_str[0].isdigit():
                grade = int(grade_str[0])

            if grade is None or grade not in GRADE_REWARD_MAP:
                # Oznacime jako zpracovano i kdyby to nebyla cisticna znamka
                await save_processed_mark(student.id, mhash)
                continue

            reward_field = GRADE_REWARD_MAP[grade]
            reward_sats = getattr(student, reward_field, 0)

            subject = mark.get("Subject", "nezname")
            memo = f"Bakalari odmena: {student.name} - {subject} - znamka {grade}"

            if reward_sats > 0:
                success = await send_reward(student.wallet, reward_sats, memo)
                if success:
                    rewards_sent += 1
                    logger.info(f"Student {student.name}: odmena {reward_sats} sat za znamku {grade} z {subject}")
            else:
                logger.debug(f"Student {student.name}: znamka {grade} ma odmenu 0 sat, preskakuji")

            # Oznacime znamku jako zpracovanou bez ohledu na odmenu
            await save_processed_mark(student.id, mhash)

        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        await update_student_last_check(student.id, now_iso)
        logger.info(f"Student {student.name}: zpracovano {len(new_marks)} znamek, odeslan {rewards_sent} odmeny, last_check aktualizovan")

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
            # Kontrolujeme kazdou hodinu, ale should_check_student rozhodne o frekvenci
            await asyncio.sleep(3600)
        except asyncio.CancelledError:
            logger.info("Bakalari Rewards task cancelled.")
            break
        except Exception as exc:
            logger.warning(f"Bakalari Rewards task error: {exc}")
            await asyncio.sleep(60)
