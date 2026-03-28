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
