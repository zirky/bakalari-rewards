from pydantic import BaseModel
from typing import Optional
import os

# Fernet sifrovani - volitelne, aktivuje se env promennou BAKALARI_FERNET_KEY
try:
    from cryptography.fernet import Fernet
    _fernet_key = os.environ.get("BAKALARI_FERNET_KEY", "")
    _fernet = Fernet(_fernet_key.encode()) if _fernet_key else None
except ImportError:
    _fernet = None


def encrypt_password(plaintext: str) -> str:
    """Zasifrovani hesla Fernetem. Pokud klic neni nastaven, vraci plaintext."""
    if _fernet and plaintext:
        return _fernet.encrypt(plaintext.encode()).decode()
    return plaintext


def decrypt_password(ciphertext: str) -> str:
    """Desifrovani hesla Fernetem. Pokud klic neni nastaven, vraci plaintext."""
    if _fernet and ciphertext:
        try:
            return _fernet.decrypt(ciphertext.encode()).decode()
        except Exception:
            return ciphertext  # fallback - uz plaintext
    return ciphertext


class CreateBakalariStudent(BaseModel):
    id: Optional[str] = None
    name: str
    wallet: Optional[str] = None
    bakalari_url: str
    bakalari_username: str
    bakalari_password: str
    ln_address: Optional[str] = None
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
    czk_deficit: float = 0
    backtest_mode: bool = False


class BakalariStudent(BaseModel):
    id: str
    name: str
    wallet: Optional[str] = None
    bakalari_url: str
    bakalari_username: str
    bakalari_password: str
    ln_address: Optional[str] = None
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
    czk_deficit: float = 0
    backtest_mode: bool = False


class BakalariStudentPublic(BaseModel):
    """Model pro API odpovedi - neobsahuje citliva pole (hesla)."""
    id: str
    name: str
    wallet: Optional[str] = None
    bakalari_url: str
    bakalari_username: str
    ln_address: Optional[str] = None
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
    czk_deficit: float = 0
    backtest_mode: bool = False
    # Vynechana citliva pole: bakalari_password
# --- Extension Settings ---

class ExtensionSettings(BaseModel):
    id: str = "global"
    lnbits_api_url: Optional[str] = None
    lnbits_api_key_enc: Optional[str] = None  # Fernet zasifrovany API key
    payout_enabled: Optional[bool] = True
    dry_run: Optional[bool] = False
    max_sats_per_run: Optional[int] = 1_000_000
    allow_insecure_tls: Optional[bool] = False


class CreateExtensionSettings(BaseModel):
    lnbits_api_url: Optional[str] = None
    lnbits_api_key: Optional[str] = None  # plaintext pri zapisu, nikdy se neuklada
    payout_enabled: Optional[bool] = None
    dry_run: Optional[bool] = None
    max_sats_per_run: Optional[int] = None
    allow_insecure_tls: Optional[bool] = None
    clear_api_key: bool = False  # True = smazat ulozeny klic


def encrypt_api_key(plaintext: str) -> str:
    if _fernet and plaintext:
        return _fernet.encrypt(plaintext.encode()).decode()
    return plaintext


def decrypt_api_key(ciphertext: str) -> Optional[str]:
    if _fernet and ciphertext:
        try:
            return _fernet.decrypt(ciphertext.encode()).decode()
        except Exception:
            return None
    return None
