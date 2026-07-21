"""LNBits payment provider — přímá platba přes LNBits wallet API."""
import httpx
from app.services.payment_provider.base import PaymentProvider, PaymentResult


class LNBitsPaymentProvider(PaymentProvider):
    def __init__(self, host: str, admin_key: str):
        self.host = host.rstrip('/')
        self.admin_key = admin_key
        self._headers = {
            'X-Api-Key': admin_key,
            'Content-Type': 'application/json',
        }

    async def check_wallet_balance(self) -> int:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"{self.host}/api/v1/wallet",
                headers=self._headers
            )
            r.raise_for_status()
            return r.json().get('balance', 0) // 1000  # msats → sats

    async def pay_invoice(self, bolt11: str) -> PaymentResult:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{self.host}/api/v1/payments",
                headers=self._headers,
                json={'out': True, 'bolt11': bolt11}
            )
            if r.status_code == 201:
                data = r.json()
                return PaymentResult(
                    success=True,
                    payment_hash=data.get('payment_hash')
                )
            return PaymentResult(
                success=False,
                error=f"LNBits chyba {r.status_code}: {r.text}"
            )
