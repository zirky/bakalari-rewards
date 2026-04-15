from pydantic import BaseModel
from typing import Optional


class CreateBakalariStudent(BaseModel):
    id: Optional[str] = None
    name: str
    wallet: Optional[str] = None
    withdraw_link: Optional[str] = None
    bakalari_url: str
    bakalari_username: str
    bakalari_password: str
    reward_grade_1: int = 100
    reward_grade_2: int = 75
    reward_grade_3: int = 50
    reward_grade_4: int = 25
    reward_grade_5: int = 0
    last_check: Optional[str] = None
    use_czk: int = 0
    reward_grade_1_czk: float = 0
    reward_grade_2_czk: float = 0
    reward_grade_3_czk: float = 0
    reward_grade_4_czk: float = 0
    reward_grade_5_czk: float = 0
    check_period: Optional[str] = 'weekly'
    reward_unit: Optional[str] = 'sat'
    email: Optional[str] = None
    payout_method: Optional[str] = 'email'
    czk_deficit: float = 0
    smtp_host: Optional[str] = None
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    smtp_port: Optional[int] = 465
    lnbits_withdraw_key: Optional[str] = None
        backtest_mode: bool = False


class BakalariStudent(BaseModel):
    id: str
    name: str
    wallet: Optional[str] = None
    withdraw_link: Optional[str] = None
    bakalari_url: str
    bakalari_username: str
    bakalari_password: str
    reward_grade_1: int = 100
    reward_grade_2: int = 75
    reward_grade_3: int = 50
    reward_grade_4: int = 25
    reward_grade_5: int = 0
    last_check: Optional[str] = None
    use_czk: int = 0
    reward_grade_1_czk: float = 0
    reward_grade_2_czk: float = 0
    reward_grade_3_czk: float = 0
    reward_grade_4_czk: float = 0
    reward_grade_5_czk: float = 0
    check_period: Optional[str] = 'weekly'
    reward_unit: Optional[str] = 'sat'
    email: Optional[str] = None
    payout_method: Optional[str] = 'email'
    czk_deficit: float = 0
    smtp_host: Optional[str] = None
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    smtp_port: Optional[int] = 465
    lnbits_withdraw_key: Optional[str] = None
    backtest_mode: bool = False
