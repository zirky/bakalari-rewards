import asyncio
import hashlib
import httpx
from datetime import datetime, timedelta, timezone
from loguru import logger

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

GRADE_REWARD_CZK_MAP = {
    1: "reward_grade_1_czk",
    2: "reward_grade_2_czk",
    3: "reward_grade_3_czk",
    4: "reward_grade_4_czk",
    5: "reward_grade_5_czk",
}


def mark_hash(student_id: str, mark: dict) -> str:
    """Vytvori unikatni hash pro kazdou znamku pro deduplication."""
    raw = f"{student_id}:{mark.get('Id', '')}:{mark.get('MarkDate', '')}:{mark.get('MarkText', '')}:{mark.get('Subject', '')}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


async def fetch_bakalari_grades(bakalari_url: str, username: str, password: str):
    """Prihlasi se do Bakalaru a vrati seznam znamek."""
    base = bakalari_url.rstrip("/")
    prefixes = ["/bakalari", "/bakaweb", "/webrodice", "/dm", "/mobile", ""]
    last_exc = None
    async with httpx.AsyncClient(timeout=30, verify=False) as client:
        for prefix in prefixes:
            try:
                token_url = base + prefix + "/api/3/login"
                resp = await client.post(
                    token_url,
                    data={
                        "client_id": "ANDR",
                        "grant_type": "password",
                        "username": username,
                        "password": password,
                    },
                )
                if resp.status_code != 200:
                    continue
                token = resp.json().get("access_token")
                if not token:
                    continue
                grades_url = base + prefix + "/api/3/marks"
                grades_resp = await client.get(
                    grades_url,
                    headers={"Authorization": f"Bearer {token}"},
                )
                grades_resp.raise_for_status()
                return grades_resp.json()
            except Exception as e:
                last_exc = e
                continue
    raise ValueError(f"Nepodarilo se pripojit k Bakalari: {last_exc}")


async def get_btc_czk_rate() -> float:
    """Ziska aktualni kurz BTC/CZK z CoinGecko."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "bitcoin", "vs_currencies": "czk"},
            )
            r.raise_for_status()
            return float(r.json()["bitcoin"]["czk"])
    except Exception as e:
        logger.warning(f"CoinGecko API chyba: {e}, pouzivam fallback kurz 1 500 000 CZK/BTC")
        return 1_500_000.0


def czk_to_sats(czk: float, czk_per_btc: float) -> int:
    """Prevede CZK na satoshi."""
    return round((czk / czk_per_btc) * 100_000_000)


def should_check_student(student) -> bool:
    """Rozhodne jestli je cas zkontrolovat znamky studenta podle check_period."""
    if student.last_check is None:
        return True
    now = datetime.now(timezone.utc)
    # last_check je Optional[str] - parsujeme z ISO stringu
    try:
        lc_str = student.last_check[:19]  # "2025-03-01T12:00:00"
        lc = datetime.strptime(lc_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except Exception:
        return True
    period = getattr(student, "check_period", "weekly")
    delta = timedelta(days=30) if period == "monthly" else timedelta(days=7)
    return (now - lc) >= delta


async def process_student_grades(student):
    """Zkontroluje nove znamky studenta a posle odmeny."""
    try:
        if not should_check_student(student):
            logger.debug(f"Student {student.name}: prilis brzy na dalsi kontrolu, preskakuji")
            return

        grades_data = await fetch_bakalari_grades(
            student.bakalari_url,
            student.bakalari_username,
            student.bakalari_password,
        )
        marks = grades_data.get("Marks", [])

        # Parsujeme last_check jako datetime pro porovnani
        last_check_dt = None
        if student.last_check:
            try:
                lc_str = student.last_check[:19]
                last_check_dt = datetime.strptime(lc_str, "%Y-%m-%dT%H:%M:%S")
            except Exception:
                pass

        new_marks = []
        for mark in marks:
            mark_date_str = mark.get("MarkDate") or mark.get("EditDate", "")
            if last_check_dt and mark_date_str:
                try:
                    mark_dt = datetime.strptime(mark_date_str[:19], "%Y-%m-%dT%H:%M:%S")
                    if mark_dt <= last_check_dt:
                        continue
                except Exception:
                    pass
            mhash = mark_hash(student.id, mark)
            if await get_processed_mark(student.id, mhash):
                continue
            new_marks.append((mark, mhash))

        if not new_marks:
            logger.info(f"Student {student.name}: zadne nove znamky")
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            await update_student_last_check(student.id, now_iso)
            return

        # Ziskame kurz pokud je treba
        reward_unit = getattr(student, "reward_unit", "sat")
        czk_per_btc = None
        if reward_unit == "czk":
            czk_per_btc = await get_btc_czk_rate()

        rewards_sent = 0
        for mark, mhash in new_marks:
            grade_str = str(mark.get("MarkText", "")).strip()
            grade = None
            if grade_str and grade_str[0].isdigit():
                grade = int(grade_str[0])

            if grade is None or grade not in GRADE_REWARD_MAP:
                await save_processed_mark(student.id, mhash)
                continue

            # Vypocet odmeny v sats
            if reward_unit == "czk":
                czk_field = GRADE_REWARD_CZK_MAP[grade]
                czk_amount = getattr(student, czk_field, 0) or 0
                # Deficit logika
                current_deficit = getattr(student, "czk_deficit", 0) or 0
                balance = czk_amount - current_deficit
                if balance <= 0:
                    # Uloz deficit a preskoc
                    from .crud import update_student_czk_deficit
                    await update_student_czk_deficit(student.id, abs(balance))
                    await save_processed_mark(student.id, mhash)
                    continue
                reward_sats = czk_to_sats(balance, czk_per_btc)
                from .crud import update_student_czk_deficit
                await update_student_czk_deficit(student.id, 0)
            else:
                sat_field = GRADE_REWARD_MAP[grade]
                reward_sats = getattr(student, sat_field, 0) or 0

            subject = mark.get("Subject", "nezname")
            memo = f"Bakalari odmena: {student.name} - {subject} - znamka {grade}"

            if reward_sats > 0:
                payout_method = getattr(student, "payout_method", "email")
                success = False
                if payout_method == "lnbits" and student.withdraw_link:
                    success = await send_reward_via_withdraw_link(student.withdraw_link, reward_sats, memo)
                elif payout_method == "email" and student.email and student.lnbits_withdraw_key:
                    success = await send_reward_via_email(student, reward_sats, memo)
                else:
                    logger.warning(f"Student {student.name}: neni nastavena metoda vyplaty, preskakuji odmenu")
                if success:
                    rewards_sent += 1
            await save_processed_mark(student.id, mhash)

        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        await update_student_last_check(student.id, now_iso)
        logger.info(f"Student {student.name}: zpracovano {len(new_marks)} znamek, odeslan {rewards_sent} odmeny")
    except Exception as exc:
        logger.warning(f"Chyba pri zpracovani studenta {student.name}: {exc}")


async def send_reward_via_withdraw_link(withdraw_link: str, amount_sats: int, memo: str) -> bool:
    """Posle odmenu primo na LN adresu/LNURL studenta."""
    try:
        # TODO: implementace LNURL-pay/withdraw
        logger.info(f"send_reward_via_withdraw_link: {withdraw_link}, {amount_sats} sat - TODO")
        return False
    except Exception as e:
        logger.warning(f"Chyba pri posilani odmeny pres withdraw_link: {e}")
        return False


async def send_reward_via_email(student, amount_sats: int, memo: str) -> bool:
    """Vytvori LNURL-withdraw voucher a odesle email s QR kodem."""
    try:
        # TODO: implementace vytvoreni withdraw voucheru pres lnbits_withdraw_key a odeslani emailu
        logger.info(f"send_reward_via_email: {student.email}, {amount_sats} sat - TODO")
        return False
    except Exception as e:
        logger.warning(f"Chyba pri posilani odmeny emailem: {e}")
        return False


async def bakalari_rewards_task():
    """Periodicky kontroluje znamky vsech studentu a posila odmeny."""
    logger.info("Bakalari Rewards task started.")
    while True:
        try:
            students = await get_all_students()
            logger.info(f"Kontroluji znamky pro {len(students)} studentu")
            for student in students:
                await process_student_grades(student)
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            logger.info("Bakalari Rewards task cancelled.")
            break
        except Exception as exc:
            logger.warning(f"Bakalari Rewards task error: {exc}")
            await asyncio.sleep(60)
