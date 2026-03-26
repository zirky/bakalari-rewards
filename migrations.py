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
