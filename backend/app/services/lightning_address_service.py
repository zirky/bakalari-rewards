"""Lightning Address (LNURL-pay) service.

Dvoukrokový flow:
1. Resolve lightning address → LNURL-pay metadata + callback URL
2. Zavolat callback s amount_msats → získat BOLT11 invoice
"""
import httpx


def parse_lightning_address(address: str) -> tuple[str, str]:
    """'user@domain.cz' → ('user', 'domain.cz')"""
    user, domain = address.split('@', 1)
    return user, domain


async def resolve_lnurl_pay(lightning_address: str) -> dict:
    """Stáhne LNURL-pay metadata z .well-known/lnurlp/{user}"""
    user, domain = parse_lightning_address(lightning_address)
    url = f"https://{domain}/.well-known/lnurlp/{user}"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
    if data.get('tag') != 'payRequest':
        raise ValueError(f"Neplatná LNURL-pay odpověď pro {lightning_address}")
    return data


async def get_invoice(lightning_address: str, amount_sats: int) -> str:
    """Vrátí BOLT11 invoice pro daný počet sats."""
    metadata = await resolve_lnurl_pay(lightning_address)
    callback = metadata['callback']
    min_msats = metadata.get('minSendable', 1000)
    max_msats = metadata.get('maxSendable', 10_000_000_000)
    amount_msats = amount_sats * 1000

    if not (min_msats <= amount_msats <= max_msats):
        raise ValueError(
            f"Částka {amount_sats} sats ({amount_msats} msats) mimo rozsah "
            f"[{min_msats}–{max_msats} msats]"
        )

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(callback, params={'amount': amount_msats})
        r.raise_for_status()
        data = r.json()

    invoice = data.get('pr')
    if not invoice:
        raise ValueError("Callback nevrátil BOLT11 invoice")
    return invoice
