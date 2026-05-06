import asyncio
import hashlib
import os
from datetime import datetime, timedelta, timezone

import httpx
from loguru import logger

from .crud import (
    delete_processed_marks_from,
    get_all_students,
    get_processed_mark,
    save_processed_mark,
    update_student_last_check,
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


def get_env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def get_env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning(
            f"Neplatna integer hodnota pro {name}='{value}', pouzivam default {default}"
        )
        return default


def get_lnbits_config() -> dict:
    return {
        "api_url": os.environ.get("BAKALARI_REWARDS_LNBITS_API_URL", "http://localhost:5000"),
        "api_key": os.environ.get("BAKALARI_REWARDS_LNBITS_API_KEY"),
        "allow_insecure_tls": get_env_bool("BAKALARI_REWARDS_ALLOW_INSECURE_TLS", False),
        "payout_enabled": get_env_bool("BAKALARI_REWARDS_PAYOUT_ENABLED", False),
        "dry_run": get_env_bool("BAKALARI_REWARDS_DRY_RUN", True),
        "max_sats_per_run": get_env_int("BAKALARI_REWARDS_MAX_SATS_PER_RUN", 100000),
    }


def mark_hash(student_id: str, mark: dict) -> str:
    """Vytvori unikatni hash pro kazdou znamku pro deduplication."""
    raw = (
        f"{student_id}:{mark.get('Id', '')}:{mark.get('MarkDate', '')}:"
        f"{mark.get('MarkText', '')}:{mark.get('Subject', '')}"
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def decrypt_bakalari_password(encrypted: str) -> str:
    """Desifruje bakalari_password pokud je aktivni BAKALARI_FERNET_KEY, jinak vraci plaintext."""
    key = os.environ.get("BAKALARI_FERNET_KEY")
    if not key or not encrypted:
        return encrypted
    try:
        from cryptography.fernet import Fernet, InvalidToken

        f = Fernet(key.encode())
        return f.decrypt(encrypted.encode()).decode()
    except InvalidToken:
        logger.warning(
            "decrypt_bakalari_password: InvalidToken - heslo neni zasifrovane nebo klic je spatny, pouzivam plaintext"
        )
        return encrypted
    except Exception as e:
        logger.warning(f"decrypt_bakalari_password: chyba desifrovani ({e}), pouzivam plaintext")
        return encrypted


async def fetch_bakalari_grades(bakalari_url: str, username: str, password: str):
    """Prihlasi se do Bakalaru a vrati seznam znamek."""
    base = bakalari_url.rstrip("/")
    prefixes = ["/webrodice", "/bakalari", "/bakaweb", "/dm", "/mobile", ""]
    last_error = "zadny prefix nevratil uspech"

    async with httpx.AsyncClient(timeout=30, verify=False) as client:
        for prefix in prefixes:
            try:
                token_url = base + prefix + "/api/login"
                logger.debug(f"Zkousim login: {token_url}")

                resp = await client.post(
                    token_url,
                    data={
                        "client_id": "ANDR",
                        "grant_type": "password",
                        "username": username,
                        "password": password,
                    },
                )

                logger.debug(f"Login odpoved {token_url}: HTTP {resp.status_code}")

                if resp.status_code == 404:
                    last_error = f"{token_url} => HTTP 404 (endpoint nenalezen)"
                    continue

                if resp.status_code != 200:
                    body = resp.text[:500]
                    try:
                        err_json = resp.json()
                        err_desc = err_json.get("error_description") or err_json.get("error") or body
                    except Exception:
                        err_desc = body
                    raise ValueError(
                        f"Prihlaseni selhalo na {token_url}: HTTP {resp.status_code} - {err_desc}"
                    )

                token = resp.json().get("access_token")
                if not token:
                    last_error = (
                        f"{token_url} => HTTP 200 ale chybi access_token. "
                        f"Odpoved: {resp.text[:200]}"
                    )
                    logger.debug(f"Login selhal: {last_error}")
                    continue

                logger.info(f"Login uspesny pres: {token_url}")

                grades_url = base + prefix + "/api/3/marks"
                grades_resp = await client.get(
                    grades_url,
                    headers={"Authorization": f"Bearer {token}"},
                )
                grades_resp.raise_for_status()
                data = grades_resp.json()

                logger.info(
                    f"API /api/3/marks odpoved - klice: {list(data.keys())}, "
                    f"pocet Subjects: {len(data.get('Subjects', []))}"
                )
                return data

            except ValueError:
                raise
            except Exception as e:
                last_error = f"{base + prefix}/api/login => vyjimka: {e}"
                logger.debug(f"Login vyjimka: {last_error}")
                continue

    raise ValueError(
        "Nepodarilo se pripojit k Bakalari. "
        f"Zadny ze znamych prefixu nefungoval. Posledni chyba: {last_error}"
    )


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
    try:
        lc_str = student.last_check[:19]
        lc = datetime.strptime(lc_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except Exception:
        return True

    period = getattr(student, "check_period", "weekly")
    delta = timedelta(days=30) if period == "monthly" else timedelta(days=7)
    return (now - lc) >= delta


async def process_student_grades(student) -> None:
    """Zkontroluje nove znamky studenta a posle odmeny."""
    try:
        if not should_check_student(student):
            logger.debug(f"Student {student.name}: prilis brzy na dalsi kontrolu, preskakuji")
            return

        plaintext_password = decrypt_bakalari_password(student.bakalari_password)

        grades_data = await fetch_bakalari_grades(
            student.bakalari_url,
            student.bakalari_username,
            plaintext_password,
        )

        subjects = grades_data.get("Subjects", grades_data.get("Marks", []))
        marks = []

        for subject in subjects:
            subject_name = (
                subject.get("Caption")
                or subject.get("Name")
                or subject.get("SubjectName")
                or "Neznamy predmet"
            )
            subject_marks = subject.get("Marks", [])
            for mark in subject_marks:
                mark["Subject"] = subject_name
                marks.append(mark)

        logger.info(f"Student {student.name}: API vratilo {len(marks)} znamek celkem")

        last_check_dt = None
        if student.last_check:
            try:
                lc_str = student.last_check[:19]
                last_check_dt = datetime.strptime(lc_str, "%Y-%m-%dT%H:%M:%S")
                logger.info(f"Student {student.name}: filtruji znamky novejsi nez {last_check_dt}")
            except Exception:
                pass

        backtest_mode = getattr(student, "backtest_mode", False)
        if backtest_mode and last_check_dt:
            await delete_processed_marks_from(
                student.id, last_check_dt.strftime("%Y-%m-%dT%H:%M:%S")
            )
            logger.info(f"Student {student.name}: backtest rezim - smazany zaznamy od {last_check_dt}")

        new_marks = []
        skipped_old = 0
        skipped_dedup = 0

        for mark in marks:
            mark_date_str = mark.get("MarkDate") or mark.get("EditDate", "")
            if last_check_dt and mark_date_str:
                try:
                    mark_dt = datetime.strptime(mark_date_str[:19], "%Y-%m-%dT%H:%M:%S")
                    if mark_dt <= last_check_dt:
                        skipped_old += 1
                        continue
                except Exception:
                    pass

            mhash = mark_hash(student.id, mark)
            if await get_processed_mark(student.id, mhash):
                skipped_dedup += 1
                continue

            new_marks.append((mark, mhash))

        logger.info(
            f"Student {student.name}: {len(new_marks)} novych, "
            f"{skipped_old} starych, {skipped_dedup} duplikatu"
        )

        if not new_marks:
            logger.info(f"Student {student.name}: zadne nove znamky")
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            await update_student_last_check(student.id, now_iso)
            return

        reward_unit = getattr(student, "reward_unit", "sat")
        czk_per_btc = None
        if reward_unit == "czk":
            czk_per_btc = await get_btc_czk_rate()

        total_reward_sats = 0
        grade_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        processed_marks = []

        for mark, mhash in new_marks:
            grade_str = str(mark.get("MarkText", "")).strip()
            grade = None

            if grade_str and grade_str[0].isdigit():
                grade = int(grade_str[0])

            if grade is None or grade not in GRADE_REWARD_MAP:
                logger.debug(f"Student {student.name}: znamka '{grade_str}' neni ocenitelna, preskakuji")
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

        grade_summary = ", ".join(
            [f"{count}x{grade}" for grade, count in grade_counts.items() if count > 0]
        )
        period = getattr(student, "check_period", "weekly")
        period_text = "mesic" if period == "monthly" else "tyden"
        memo = f"Odmena za {period_text}: {grade_summary} (celkem {len(processed_marks)} znamek)"

        logger.info(
            f"Student {student.name}: celkova odmena za obdobi: "
            f"{total_reward_sats} sat ({grade_summary})"
        )

        payment_sent = False
        if total_reward_sats > 0:
            ln_target = getattr(student, "ln_address", None) or getattr(student, "withdraw_link", None)

            if ln_target:
                payment_sent = await send_reward_via_withdraw_link(
                    ln_target,
                    total_reward_sats,
                    memo,
                )
            else:
                logger.warning(
                    f"Student {student.name}: neni nastavena LN penezenka "
                    f"(ln_address / withdraw_link), preskakuji odmenu"
                )

        for mhash in processed_marks:
            await save_processed_mark(student.id, mhash)

        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        await update_student_last_check(student.id, now_iso)

        if payment_sent:
            logger.info(
                f"Student {student.name}: zpracovano {len(processed_marks)} znamek, "
                f"odeslana 1 platba ({total_reward_sats} sat)"
            )
        else:
            logger.info(
                f"Student {student.name}: zpracovano {len(processed_marks)} znamek, "
                f"platba nebyla odeslana"
            )

    except Exception as exc:
        logger.warning(f"Chyba pri zpracovani studenta {student.name}: {exc}")


async def send_reward_via_withdraw_link(withdraw_link: str, amount_sats: int, memo: str) -> bool:
    """
    Lokalni testovaci implementace:
    - konfigurace LNbits se cte z environment variables
    - payout je defaultne vypnuty
    - dry_run je defaultne zapnuty
    - zatim se ignoruje withdraw_link a testuje se pouze LNbits send pipeline
    """
    try:
        config = get_lnbits_config()

        logger.info(
            f"send_reward_via_withdraw_link: target={withdraw_link}, amount={amount_sats} sat, memo={memo}"
        )

        if amount_sats <= 0:
            logger.warning("LNbits payout preskocen: amount_sats musi byt > 0")
            return False

        if amount_sats > config["max_sats_per_run"]:
            logger.warning(
                f"LNbits payout zablokovan: {amount_sats} sat prekrocilo "
                f"limit max_sats_per_run={config['max_sats_per_run']}"
            )
            return False

        if not config["payout_enabled"]:
            logger.warning(
                "LNbits payout je vypnuty (BAKALARI_REWARDS_PAYOUT_ENABLED=false), "
                "platbu neposilam"
            )
            return False

        if config["dry_run"]:
            logger.info(
                f"DRY RUN: simulace LNbits platby {amount_sats} sat na target '{withdraw_link}' "
                f"s memem '{memo}'"
            )
            return True

        if not config["api_key"]:
            logger.warning("LNbits payout nelze provest: chybi BAKALARI_REWARDS_LNBITS_API_KEY")
            return False

        async with httpx.AsyncClient(
            timeout=30,
            verify=not config["allow_insecure_tls"],
        ) as client:
            create_body = {
                "out": False,
                "amount": amount_sats,
                "memo": memo,
            }
            r_inv = await client.post(
                f"{config['api_url'].rstrip('/')}/api/v1/payments",
                headers={
                    "X-Api-Key": config["api_key"],
                    "Content-Type": "application/json",
                },
                json=create_body,
            )
            r_inv.raise_for_status()
            inv_data = r_inv.json()

            bolt11 = inv_data.get("payment_request") or inv_data.get("bolt11")
            if not bolt11:
                logger.warning(f"LNbits invoice nema payment_request/bolt11: {inv_data}")
                return False

            pay_body = {
                "out": True,
                "bolt11": bolt11,
            }
            r_pay = await client.post(
                f"{config['api_url'].rstrip('/')}/api/v1/payments",
                headers={
                    "X-Api-Key": config["api_key"],
                    "Content-Type": "application/json",
                },
                json=pay_body,
            )
            r_pay.raise_for_status()
            pay_data = r_pay.json()

            status = pay_data.get("status") or pay_data.get("paid")
            if status in ("success", True):
                logger.info(f"LNbits platba uspesna: {amount_sats} sat, memo='{memo}'")
                return True

            logger.warning(f"LNbits platba neuspesna, odpoved: {pay_data}")
            return False

    except Exception as e:
        logger.warning(f"Chyba pri posilani odmeny pres LNbits API: {e}")
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
