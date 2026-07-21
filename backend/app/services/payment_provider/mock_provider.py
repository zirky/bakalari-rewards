"""MockPaymentProvider — pro testování bez skutečné Lightning platby."""
import uuid
from app.services.payment_provider.base import PaymentProvider, PaymentResult


class MockPaymentProvider(PaymentProvider):
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.paid_invoices: list[str] = []

    async def check_wallet_balance(self) -> int:
        return 1_000_000  # mock: 1M sats

    async def pay_invoice(self, bolt11: str) -> PaymentResult:
        if self.should_fail:
            return PaymentResult(success=False, error="Mock: platba záměrně selhala")
        self.paid_invoices.append(bolt11)
        return PaymentResult(
            success=True,
            payment_hash=f"mock_{uuid.uuid4().hex}"
        )
