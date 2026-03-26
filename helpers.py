# Pomocné funkce pro Bakaláři Rewards

from lnbits.core.crud import get_wallet


async def get_wallet_name(wallet_id: str) -> str:
    """Vrátí název peněženky podle ID."""
    wallet = await get_wallet(wallet_id)
    if wallet:
        return wallet.name
    return "Neznámá peněženka"
