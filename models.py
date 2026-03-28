from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CreateBakalariStudent(BaseModel):
    id: Optional[str] = None
    name: str
    wallet: str
    bakalari_url: str
    bakalari_username: str
    bakalari_password: str
    reward_grade_1: int = 100
    reward_grade_2: int = 75
    reward_grade_3: int = 50
    reward_grade_4: int = 25
    reward_grade_5: int = 0
    last_check: Optional[datetime] = None
    use_czk: int = 0
    reward_grade_1_czk: float = 0
    reward_grade_2_czk: float = 0
    reward_grade_3_czk: float = 0
    reward_grade_4_czk: float = 0
    reward_grade_5_czk: float = 0
    check_period: str = 'weekly'


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
    last_check: Optional[datetime] = None
    use_czk: int = 0
    reward_grade_1_czk: float = 0
    reward_grade_2_czk: float = 0
    reward_grade_3_czk: float = 0
    reward_grade_4_czk: float = 0
    reward_grade_5_czk: float = 0
    check_period: str = 'weekly'
