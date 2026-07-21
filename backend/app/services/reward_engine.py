"""Reward engine — port z původního index.js.

Mapování: '1+' → 1, '2-' → 2 (ignoruje +/-)
Výpočet: součet CZK odměn za nové známky
Balance logika: newBalance = runningBalance + czkChange
  - newBalance > 0 → vytvoř payout za celé newBalance, balance = 0
  - newBalance <= 0 → bez payoutu, ulož záporný zůstatek
"""
from decimal import Decimal
from typing import NamedTuple


def map_grade_to_numeric(grade_text: str) -> int | None:
    """'1+' → 1, '2-' → 2, 'N' → None"""
    cleaned = grade_text.strip().replace('+', '').replace('-', '')
    try:
        return int(cleaned)
    except ValueError:
        return None


def compute_czk_change(marks: list[dict], grade_rules: dict[int, Decimal]) -> Decimal:
    """Sečte CZK dopad nových známek podle pravidel rodiče."""
    total = Decimal('0')
    for mark in marks:
        numeric = map_grade_to_numeric(mark['value'])
        if numeric is not None and numeric in grade_rules:
            total += grade_rules[numeric]
    return total


class PayoutDecision(NamedTuple):
    should_pay: bool
    payout_czk: Decimal
    new_balance: Decimal


def decide_payout(running_balance: Decimal, czk_change: Decimal) -> PayoutDecision:
    """Rozhodnutí o payoutu podle balance logiky z původního skriptu."""
    new_balance = running_balance + czk_change
    if new_balance > 0:
        return PayoutDecision(should_pay=True, payout_czk=new_balance, new_balance=Decimal('0'))
    return PayoutDecision(should_pay=False, payout_czk=Decimal('0'), new_balance=new_balance)
