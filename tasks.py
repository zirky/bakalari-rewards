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
    delete_processed_marks_from,
)
from .models import decrypt_password

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
    prefixes = ["/webrodice", "/bakalari", "/bakaweb", "/dm", "/mobile", ""]
    last_error = "zadny prefix nevratil uspech"
    async with httpx.AsyncClient(timeout=30, verify=False) as client:
        for prefix in prefixes:
            token_url = f"{base}{prefix}/api/3/login"
            logger.debug(f"Zkousim login: {token_url}")
            try:
                resp = await client.post(
                    token_url,
                    data={"username": username, "password": password},
                )
                logger.debug(f"Login odpoved {token_url}: HTTP {resp.status_code}")
                if resp.status_code != 200:
                    last_error = f"Prihlaseni selhalo na {token_url}: HTTP {resp.status_code} - {resp.text[:200]}"
                    continue
                token_data = resp.json()
                access_token = token_data.get("access_token")
                if not access_token:
                    last_error = f"Token nenalezen v odpovedi z {token_url}"
                    continue
                logger.info(f"Login uspesny pres: {token_url}")
                marks_url = f"{base}{prefix}/api/3/marks"
                marks_resp = await client.get(
                    marks_url,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if marks_resp.status_code != 200:
                    last_error = f"Nepodarilo se nacist znamky z {marks_url}: HTTP {marks_resp.status_code}"
                    continue
                data = marks_resp.json()
                logger.info(
                    f"API /api/3/marks odpoved - klice: {list(data.keys())}, pocet Subjects: {len(data.get('Subjects', []))}"
                )
                marks = []
                for subject in data.get("Subjects", []):
                    for mark in subject.get("Marks", []):
                        mark["Subject"] = subject.get("Subject", "")
                        marks.append(mark)
                return marks
            except Exception as e:
                last_error = f"Vyjimka pri pokusu o {token_url}: {e}"
                continue
    raise Exception(last_error)


async def get_czk_per_btc() -> float:
    """Ziska aktualni kurz BTC/CZK z CoinGecko."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "bitcoin", "vs_currencies": "czk"},
            )
            if resp.status_code == 200:
                return float(resp.json()["bitcoin"]["czk"])
    except Exception as e:
        logger.warning(f"CoinGecko API chyba: {e}, pouzivam fallback kurz 1 500 000 CZK/BTC")
    return 1_500_000.0


def czk_to_sats(czk_amount: float, czk_per_btc: float) -> int:
    """Prevede CZK na satoshi."""
    if czk_per_btc <= 0:
        return 0
    btc = czk_amount / czk_per_btc
    return int(btc * 100_000_000)


async def send_reward_via_ln_address(
    ln_address: str, amount_sats: int, memo: str, wallet_id: str
) -> bool:
    """Odesle odmenu na Lightning adresu pres LNURL-pay flow."""
    try:
        if "@" not in ln_address:
            logger.warning(f"Neplatna LN adresa: {ln_address}")
            return False
        user, domain = ln_address.split("@", 1)
        lnurlp_url = f"https://{domain}/.well-known/lnurlp/{user}"
        async with httpx.AsyncClient(timeout=15, verify=False) as client:
            r1 = await client.get(lnurlp_url)
            if r1.status_code != 200:
                logger.warning(f"LNURL fetch chyba pro {ln_address}: HTTP {r1.status_code}")
                return False
            lnurl_data = r1.json()
            callback = lnurl_data.get("callback")
            min_sendable = lnurl_data.get("minSendable", 1000)
            max_sendable = lnurl_data.get("maxSendable", 100_000_000_000)
            comment_allowed = lnurl_data.get("commentAllowed", 0)
            if not callback:
                logger.warning(f"Chybi callback v LNURL odpovedi pro {ln_address}")
                return False
            amount_msats = amount_sats * 1000
            if amount_msats < min_sendable or amount_msats > max_sendable:
                logger.warning(
                    f"Castka {amount_sats} sat mimo limity pro {ln_address} "
                    f"(min={min_sendable // 1000} sat, max={max_sendable // 1000} sat)"
                )
                return False
            params: dict = {"amount": amount_msats}
            if comment_allowed > 0 and memo:
                params["comment"] = memo[:comment_allowed]
            r2 = await client.get(callback, params=params)
            if r2.status_code != 200:
                logger.warning(f"Invoice chyba pro {ln_address}: HTTP {r2.status_code} - {r2.text[:200]}")
                return False
            invoice_data = r2.json()
            if invoice_data.get("status") == "ERROR":
                logger.warning(f"Invoice chyba pro {ln_address}: {invoice_data.get('reason', 'neznama chyba')}")
                return False
            payment_request = invoice_data.get("pr")
            if not payment_request:
                logger.warning(f"Chybi 'pr' v invoice odpovedi pro {ln_address}")
                return False
        from lnbits.core.services import pay_invoice
        await pay_invoice(
            wallet_id=wallet_id,
            payment_request=payment_request,
            max_sat=amount_sats + 10,
            extra={"tag": "bakalari_rewards", "memo": memo},
        )
        return True
    except Exception as e:
        logger.warning(f"Platba selhala pro {ln_address}: {e}")
        return False


async def process_student_grades(student) -> None:
    """Zpracuje znamky pro jednoho studenta a odesle odmenu."""
    try:
        username = getattr(student, "bakalari_username", None)
        password_raw = getattr(student, "bakalari_password", None)
        bakalari_url = getattr(student, "bakalari_url", None)
        if not username or not password_raw or not bakalari_url:
            logger.warning(f"Student {student.name}: chybi prihlasovaci udaje nebo URL")
            return
        password = decrypt_password(password_raw)
        marks = await fetch_bakalari_grades(bakalari_url, username, password)
        logger.info(f"Student {student.name}: API vratilo {len(marks)} znamek celkem")
        last_check_str = getattr(student, "last_check", None)
        if last_check_str:
            try:
                last_check_dt = datetime.fromisoformat(last_check_str)
                if last_check_dt.tzinfo is None:
                    last_check_dt = last_check_dt.replace(tzinfo=timezone.utc)
            except Exception:
                last_check_dt = datetime.now(timezone.utc) - timedelta(days=7)
        else:
            last_check_dt = datetime.now(timezone.utc) - timedelta(days=7)
        logger.info(f"Student {student.name}: filtruji znamky novejsi nez {last_check_dt}")
        new_marks = []
        skipped_old = 0
        skipped_dedup = 0
        for mark in marks:
            date_str = mark.get("MarkDate", "")
            if date_str:
                try:
                    mark_dt = datetime.fromisoformat(date_str)
                    if mark_dt.tzinfo is None:
                        mark_dt = mark_dt.replace(tzinfo=timezone.utc)
                    if mark_dt <= last_check_dt:
                        skipped_old += 1
                        continue
                except Exception:
                    pass
            mhash = mark_hash(student.id, mark)
            existing = await get_processed_mark(student.id, mhash)
            if existing:
                skipped_dedup += 1
                continue
            new_marks.append((mark, mhash))
        logger.info(
            f"Student {student.name}: {len(new_marks)} novych, {skipped_old} starych, {skipped_dedup} duplikatu"
        )
        if not new_marks:
            return
        backtest = getattr(student, "backtest_mode", False)
        if backtest:
            logger.info(f"Student {student.name}: backtest rezim - smazany zaznamy od {last_check_dt}")
            await delete_processed_marks_from(student.id, last_check_dt)
        czk_per_btc = await get_czk_per_btc()
        reward_unit = getattr(student, "reward_unit", "sats")
        total_reward_sats = 0
        grade_counts: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        processed_marks = []
        for mark, mhash in new_marks:
            grade_text = mark.get("MarkText", "")
            try:
                grade = int(grade_text)
            except (ValueError, TypeError):
                processed_marks.append(mhash)
                continue
            if grade not in GRADE_REWARD_MAP:
                processed_marks.append(mhash)
                continue
            if reward_unit == "czk":
                czk_field = GRADE_REWARD_CZK_MAP[grade]
                czk_amount = getattr(student, czk_field, 0) or 0
                current_deficit = getattr(student, "czk_deficit", 0) or 0
                balance = czk_amount - current_deficit
                if balance <= 0:
                    from .crud import update_student_czk_deficit
                    await update_student_czk_deficit(student.id, abs(balance))
                    processed_marks.append(mhash)
                    continue
                reward_sats = czk_to_sats(balance, czk_per_btc)
                from .crud import update_student_czk_deficit
                await update_student_czk_deficit(student.id, 0)
            else:
                sat_field = GRADE_REWARD_MAP[grade]
                reward_sats = getattr(student, sat_field, 0) or 0
            total_reward_sats += reward_sats
            grade_counts[grade] += 1
            processed_marks.append(mhash)
        grade_summary = ", ".join([f"{count}x{grade}" for grade, count in grade_counts.items() if count > 0])
        period = getattr(student, "check_period", "weekly")
        period_text = "mesic" if period == "monthly" else "tyden"
        memo = f"Odmena za {period_text}: {grade_summary} (celkem {len(processed_marks)} znamek)"
        logger.info(f"Student {student.name}: celkova odmena za obdobi: {total_reward_sats} sat ({grade_summary})")
        payment_sent = False
        if total_reward_sats > 0:
            ln_address = getattr(student, "ln_address", None)
            if ln_address:
                payment_sent = await send_reward_via_ln_address(
                    ln_address, total_reward_sats, memo, student.wallet
                )
            else:
                logger.warning(f"Student {student.name}: neni nastavena Lightning adresa, preskakuji odmenu")
        for mhash in processed_marks:
            await save_processed_mark(student.id, mhash)
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        await update_student_last_check(student.id, now_iso)
        if payment_sent:
            logger.info(
                f"Student {student.name}: zpracovano {len(processed_marks)} znamek, odeslana platba ({total_reward_sats} sat) na {ln_address}"
            )
        else:
            logger.info(f"Student {student.name}: zpracovano {len(processed_marks)} znamek, platba nebyla odeslana")
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
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            logger.info("Bakalari Rewards task cancelled.")
            break
        except Exception as exc:
            logger.warning(f"Bakalari Rewards task error: {exc}")
            await asyncio.sleep(60)
