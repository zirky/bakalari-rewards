import asyncio
import httpx
from datetime import datetime, timezone
from loguru import logger

# Importy z tvého doplňku
from .crud import get_all_students, update_student_last_check

# Importy z LNbits jádra
from lnbits.core.services import create_invoice
from lnbits.db import Database

GRADE_REWARD_MAP = {
    1: "reward_grade_1",
    2: "reward_grade_2",
    3: "reward_grade_3",
    4: "reward_grade_4",
    5: "reward_grade_5",
}

async def fetch_bakalari_grades(bakalari_url: str, username: str, password: str):
    """Přihlásí se do Bakalářů a vrátí seznam známek."""
    base = bakalari_url.rstrip("/")
    token_url = f"{base}/api/3/auth"
    grades_url = f"{base}/api/3/marks"

    async with httpx.AsyncClient(timeout=30, verify=False) as client:
        try:
            # Autentizace
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

            # Získání známek
            grades_resp = await client.get(
                grades_url,
                headers={"Authorization": f"Bearer {token}"},
            )
            grades_resp.raise_for_status()
            return grades_resp.json()
        except Exception as e:
            logger.error(f"Bakalari API Error ({bakalari_url}): {e}")
            raise

async def send_reward(wallet_id: str, amount_sats: int, memo: str):
    """Vytvoří interní platbu v LNbits, která se zapíše do historie a zvýší zůstatek."""
    try:
        # 1. Vytvoření interní faktury (invoice) v LNbits jádru
        # 'internal=True' zajistí, že se nebude snažit komunikovat s Lightning uzlem
        payment_hash, payment_request = await create_invoice(
            wallet_id=wallet_id,
            amount=amount_sats,
            memo=memo,
            internal=True
        )
        
        # 2. Protože jde o "odměnu" (kredit z ničeho), musíme fakturu v DB 
        # ručně označit jako zaplacenou (pending = false).
        db = Database("database")
        await db.execute(
            """
            UPDATE payments SET pending = false, amount = :amount
            WHERE hash = :hash AND wallet = :wallet
            """,
            {
                "amount": amount_sats * 1000, # LNbits ukládá v milisatoshi
                "hash": payment_hash, 
                "wallet": wallet_id
            },
        )
        logger.success(f"Odměna {amount_sats} sat připsána do peněženky {wallet_id}: {memo}")
    except Exception as e:
        logger.error(f"Chyba při připisování odměny do LNbits: {e}")

async def process_student_grades(student):
    """Zkontroluje nové známky studenta a pošle odměny."""
    try:
        grades_data = await fetch_bakalari_grades(
            student.bakalari_url,
            student.bakalari_username,
            student.bakalari_password,
        )
        
        marks = grades_data.get("Marks", [])
        if not marks:
            logger.info(f"Student {student.name}: Žádné známky v API.")
            return

        # Seřadíme známky podle data vzestupně
        marks.sort(key=lambda x: x.get("MarkDate", ""))

        new_marks_found = False
        latest_date = student.last_check

        for mark in marks:
            mark_date = mark.get("MarkDate")
            
            # Pokud už jsme tuhle známku (nebo novější) viděli, přeskočit
            if student.last_check and mark_date <= student.last_check:
                continue

            # Extrakce známky (řeší i "1-", "2" atd.)
            mark_text = str(mark.get("MarkText", "")).strip()
            if not mark_text or not mark_text[0].isdigit():
                continue
            
            grade = int(mark_text[0])

            if grade in GRADE_REWARD_MAP:
                reward_field = GRADE_REWARD_MAP[grade]
                # Získání hodnoty odměny z modelu studenta (např. student.reward_grade_1)
                reward_sats = getattr(student, reward_field, 0)
                
                if reward_sats > 0:
                    subject = mark.get("SubjectText", "Předmět")
                    memo = f"Bakaláři odměna: {subject} (známka {grade})"
                    await send_reward(student.wallet, reward_sats, memo)
                    new_marks_found = True
                    # Posuneme lokální kurzor data na tuto známku
                    if not latest_date or mark_date > latest_date:
                        latest_date = mark_date

        if new_marks_found:
            await update_student_last_check(student.id, latest_date)
            logger.info(f"Student {student.name}: Poslední kontrola aktualizována na {latest_date}")
        else:
            logger.info(f"Student {student.name}: Žádné nové známky k vyplacení.")

    except Exception as exc:
        logger.warning(f"Chyba při zpracování studenta {student.name}: {exc}")

async def bakalari_rewards_task():
    """Periodicky kontroluje známky všech studentů a posílá odměny."""
    logger.info("Bakalari Rewards task started.")
    # Počkáme pár sekund po startu, aby se stihly zinicializovat DB tabulky
    await asyncio.sleep(10)
    
    while True:
        try:
            students = await get_all_students()
            if not students:
                logger.info("V databázi nejsou žádní studenti ke kontrole.")
            else:
                logger.info(f"Spouštím kontrolu pro {len(students)} studentů")
                for student in students:
                    await process_student_grades(student)
            
            # Kontrola jednou za hodinu (3600s)
            await asyncio.sleep(3600)
            
        except asyncio.CancelledError:
            logger.info("Bakalari Rewards task byl ukončen.")
            break
        except Exception as exc:
            logger.error(f"Chyba v hlavní smyčce Bakalari Rewards: {exc}")
            # Při chybě počkáme minutu a zkusíme znovu
            await asyncio.sleep(60)
