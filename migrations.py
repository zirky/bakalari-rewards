# Migrations file - nikdy nemazej, pouze pridavej!


async def _safe_alter(db, sql):
    """Provede ALTER TABLE - ignoruje chybu pokud sloupec jiz existuje."""
    try:
        await db.execute(sql)
    except Exception:
        pass  # sloupec jiz existuje


async def m001_initial(db):
    """
    Vytvoří tabulku pro žáky Bakálář Rewards.
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
    Pridá sloupce pro CZK menu, frekvenci kontroly a poslední kontrolu.
    """
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN use_czk INTEGER DEFAULT 0")
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN reward_grade_1_czk REAL DEFAULT 0")
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN reward_grade_2_czk REAL DEFAULT 0")
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN reward_grade_3_czk REAL DEFAULT 0")
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN reward_grade_4_czk REAL DEFAULT 0")
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN reward_grade_5_czk REAL DEFAULT 0")
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN check_period TEXT DEFAULT 'weekly'")


async def m003_convert_last_check_datetime(db):
    """
    Migrace m003 je preskocena - DROP COLUMN neni podporovan ve starsich verzich SQLite.
    Pro nove instalace neni potreba (last_check je jiz TEXT v m001).
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
    """
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN withdraw_link TEXT DEFAULT NULL")


async def m006_add_email_payout_deficit(db):
    """
    Pridá sloupce pro email, payout_method, czk_deficit a SMTP konfiguraci.
    """
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN email TEXT DEFAULT NULL")
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN payout_method TEXT DEFAULT 'email'")
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN czk_deficit REAL DEFAULT 0")
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN smtp_host TEXT DEFAULT NULL")
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN smtp_user TEXT DEFAULT NULL")
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN smtp_pass TEXT DEFAULT NULL")
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN smtp_port INTEGER DEFAULT 465")


async def m007_add_reward_unit(db):
    """
    Pridá sloupec reward_unit pro volbu meny odmeny (sat nebo czk).
    """
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN reward_unit TEXT DEFAULT 'sat'")
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN lnbits_withdraw_key TEXT DEFAULT NULL")

async def m008_add_backtest_mode(db):
    """
    Pridá sloupec backtest_mode pro bezpečné testování historických dat.
    """
    await _safe_alter(db, "ALTER TABLE bakalari_rewards.students ADD COLUMN backtest_mode INTEGER DEFAULT 0")
