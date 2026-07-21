import pytest
from app.services.payment_provider.mock_provider import MockPaymentProvider


@pytest.mark.asyncio
async def test_mock_provider_success():
    provider = MockPaymentProvider()
    result = await provider.pay_invoice("lnbc_test_invoice")
    assert result.success is True
    assert result.payment_hash.startswith("mock_")
    assert "lnbc_test_invoice" in provider.paid_invoices


@pytest.mark.asyncio
async def test_mock_provider_failure():
    provider = MockPaymentProvider(should_fail=True)
    result = await provider.pay_invoice("lnbc_test")
    assert result.success is False
    assert result.error is not None


@pytest.mark.asyncio
async def test_mock_wallet_balance():
    provider = MockPaymentProvider()
    balance = await provider.check_wallet_balance()
    assert balance == 1_000_000
