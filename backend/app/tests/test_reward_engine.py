from decimal import Decimal
from app.services.reward_engine import map_grade_to_numeric, compute_czk_change, decide_payout


def test_map_grade_ignores_plus_minus():
    assert map_grade_to_numeric("1+") == 1
    assert map_grade_to_numeric("2-") == 2
    assert map_grade_to_numeric("3") == 3
    assert map_grade_to_numeric("N") is None


def test_compute_czk_change():
    rules = {1: Decimal('50'), 2: Decimal('30'), 3: Decimal('0'),
             4: Decimal('-10'), 5: Decimal('-20')}
    marks = [
        {'value': '1', 'subject': 'Mat'},
        {'value': '2+', 'subject': 'Čj'},
        {'value': '4-', 'subject': 'Dej'},
    ]
    assert compute_czk_change(marks, rules) == Decimal('70')


def test_decide_payout_positive():
    result = decide_payout(Decimal('0'), Decimal('70'))
    assert result.should_pay is True
    assert result.payout_czk == Decimal('70')
    assert result.new_balance == Decimal('0')


def test_decide_payout_negative_carries_over():
    result = decide_payout(Decimal('10'), Decimal('-30'))
    assert result.should_pay is False
    assert result.new_balance == Decimal('-20')


def test_decide_payout_debt_repaid():
    result = decide_payout(Decimal('-20'), Decimal('50'))
    assert result.should_pay is True
    assert result.payout_czk == Decimal('30')
