from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PaymentResult:
    success: bool
    payment_hash: str | None = None
    error: str | None = None


class PaymentProvider(ABC):
    @abstractmethod
    async def pay_invoice(self, bolt11: str) -> PaymentResult:
        """Zaplatí BOLT11 invoice a vrátí výsledek."""
        ...

    @abstractmethod
    async def check_wallet_balance(self) -> int:
        """Vrátí zůstatek peněženky v sats."""
        ...
