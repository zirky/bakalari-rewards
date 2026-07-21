from app.services.payment_provider.base import PaymentProvider, PaymentResult
from app.services.payment_provider.lnbits_provider import LNBitsPaymentProvider
from app.services.payment_provider.mock_provider import MockPaymentProvider
from app.config import settings


def get_payment_provider() -> PaymentProvider:
    if settings.MOCK_MODE:
        return MockPaymentProvider()
    return LNBitsPaymentProvider(
        host=settings.LNBITS_HOST,
        admin_key=settings.LNBITS_ADMIN_KEY,
    )
