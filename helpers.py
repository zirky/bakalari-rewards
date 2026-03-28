# Pomocné funkce pro Bakaláři Rewards

import httpx
from lnbits.core.crud import get_wallet


async def get_wallet_name(wallet_id: str) -> str:
    """Vrátí název peněženky podle ID."""
    wallet = await get_wallet(wallet_id)
    if wallet:
        return wallet.name
    return "Neznámá peněženka"


async def get_btc_czk_rate() -> float:
    """Vrátí aktuální kurz BTC/CZK z CoinGecko API."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "bitcoin", "vs_currencies": "czk"},
                timeout=10,
            )
            data = resp.json()
            return float(data["bitcoin"]["czk"])
    except Exception:
        return 0.0


async def czk_to_sats(czk_amount: float) -> int:
    """Přepočítá CZK částku na satoshi pomocí aktuálního kurzu."""
    rate = await get_btc_czk_rate()
    if rate <= 0:
        return 0
    # 1 BTC = 100_000_000 sat
    sats = round((czk_amount / rate) * 100_000_000)
    return max(0, sats)
