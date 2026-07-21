"""Exchange rate service — CoinGecko API, formát bitcoin.czk"""
import httpx
from decimal import Decimal
from app.config import settings

FALLBACK_CZK_PER_BTC = Decimal('1500000')


async def get_btc_czk_rate() -> Decimal:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(settings.EXCHANGE_RATE_API_URL)
            r.raise_for_status()
            rate = r.json().get('bitcoin', {}).get('czk')
            if not rate:
                raise ValueError("Neplatná odpověď z kurz API")
            return Decimal(str(rate))
    except Exception:
        return FALLBACK_CZK_PER_BTC


def czk_to_sats(czk_amount: Decimal, czk_per_btc: Decimal) -> int:
    sats_per_btc = Decimal('100000000')
    return int((czk_amount / czk_per_btc * sats_per_btc).to_integral_value())
