# Migrations file - nikdy nemaž, pouze přidávej!

async def m001_initial(db):
    """
    Vytvoří tabulku pro žáky Bakáláři Rewards.
    """
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS bakalari_rewards.students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            wallet TEXT NOT NULL,
            bakalari_url TEXT NOT NULL,
            bakalari_username TEXT NOT NULL,
            bakalari_password TEXT NOT NULL,
            reward_grade_1 INTEGER DEFAULT 100,
            reward_grade_2 INTEGER DEFAULT 75,
            reward_grade_3 INTEGER DEFAULT 50,
            reward_grade_4 INTEGER DEFAULT 25,
            reward_grade_5 INTEGER DEFAULT 0,
            last_check TEXT
        )
        """
    )


async def m002_add_czk_and_period(db):
    """
    Přidá sloupce pro CZK měnu, frekvenci kontroly a poslední kontrolu.
    """
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN use_czk INTEGER DEFAULT 0"
    )
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN reward_grade_1_czk REAL DEFAULT 0"
    )
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN reward_grade_2_czk REAL DEFAULT 0"
    )
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN reward_grade_3_czk REAL DEFAULT 0"
    )
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN reward_grade_4_czk REAL DEFAULT 0"
    )
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN reward_grade_5_czk REAL DEFAULT 0"
    )
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN check_period TEXT DEFAULT 'weekly'"
    )


async def m003_convert_last_check_datetime(db):
    """
    Migrace m003 je přeskočena - DROP COLUMN není podporován ve starších verzích SQLite.
    Pro nové instalace není potřeba (last_check je již TEXT v m001).
    """
    pass


async def m004_add_processed_marks(db):
    """
    Vytvori tabulku pro zaznamy zpracovatych znamek (deduplication).
    """
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS bakalari_rewards.processed_marks (
            student_id TEXT NOT NULL,
            mark_hash TEXT NOT NULL,
            processed_at TEXT NOT NULL,
            PRIMARY KEY (student_id, mark_hash)
        )
        """
    )


async def m005_add_withdraw_link(db):
    """
    Prida sloupec withdraw_link pro LNURL-withdraw odkaz studenta.
    Wallet pole zustava ale stava se volitelnym.
    """
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN withdraw_link TEXT DEFAULT NULL"
    )


async def m006_add_email_payout_deficit(db):
    """
    Přidá sloupce pro:
    - email: emailová adresa žáka pro odeslání QR kódu voucheru
    - payout_method: způsob výplaty ('email' nebo 'wallet')
    - czk_deficit: kumulovaný deficit z předchozích období v CZK
    - smtp_host, smtp_user, smtp_pass, smtp_port: SMTP nastavení (globální, uloženo u prvního studenta)
    """
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN email TEXT DEFAULT NULL"
    )
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN payout_method TEXT DEFAULT 'email'"
    )
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN czk_deficit REAL DEFAULT 0"
    )
    # SMTP konfigurace ulozena per-student (admin muze mit ruzne SMTP pro ruzne zaky)
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN smtp_host TEXT DEFAULT NULL"
    )
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN smtp_user TEXT DEFAULT NULL"
    )
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN smtp_pass TEXT DEFAULT NULL"
    )
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN smtp_port INTEGER DEFAULT 465"
    )
    # lnbits_withdraw_adminkey: API klic pro withdraw extension
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN lnbits_withdraw_key TEXT DEFAULT NULL"
    )
