# Migrations file - nikdy nemaž, pouze přidávej!

async def m001_initial(db):
    """
    Vytvoří tabulku pro žáky Bakaláři Rewards.
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
    Převod pole last_check z TEXT na skutečný timestamp.
    """
    await db.execute(
        "ALTER TABLE bakalari_rewards.students ADD COLUMN last_check_new TIMESTAMP"
    )
    
    # Zkopírování dat z textového pole do timestamp pole (pokud jsou validní)
    await db.execute(
        """
        UPDATE bakalari_rewards.students 
        SET last_check_new = CASE 
            WHEN last_check IS NOT NULL AND last_check != '' 
            THEN datetime(last_check) 
            ELSE NULL 
        END
        """
    )
    
    # Smazání starého sloupce
    await db.execute(
        "ALTER TABLE bakalari_rewards.students DROP COLUMN last_check"
    )
    
    # Přejmenování nového sloupce
    await db.execute(
        "ALTER TABLE bakalari_rewards.students RENAME COLUMN last_check_new TO last_check"
    )


async def m004_add_processed_marks(db):
    """
    Vytvori tabulku pro zaznamy zpracovatych znamek (deduplication).
    """
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS bakalari_rewards.processed_marks (
            student_id TEXT NOT NULL,
            mark_hash  TEXT NOT NULL,
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
