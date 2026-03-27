from pydantic import BaseModel
from typing import Optional

class CreateBakalariStudent(BaseModel):
    name: str
    wallet: Optional[str] = None
    bakalari_url: str
    bakalari_username: str
    bakalari_password: str
    reward_grade_1: int = 100
    reward_grade_2: int = 75
    reward_grade_3: int = 50
    reward_grade_4: int = 25
    reward_grade_5: int = 0
    last_check: Optional[str] = None

class BakalariStudent(BaseModel):
    id: str
    name: str
    wallet: str
    bakalari_url: str
    bakalari_username: str
    bakalari_password: str
    reward_grade_1: int
    reward_grade_2: int
    reward_grade_3: int
    reward_grade_4: int
    reward_grade_5: int
    last_check: Optional[str] = None
