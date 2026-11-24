import math

import pytest

from ledgerlouis.domain.health import compare_to_median
from ledgerlouis.domain.technical import annualized_volatility, period_return, rsi, sma


def test_sma_aligned_with_input():
    assert sma([1, 2, 3, 4], 2) == [None, 1.5, 2.5, 3.5]
    assert sma([1, 2], 3) == [None, None]


def test_rsi_extremes_and_balance():
    assert rsi(list(range(1, 17)), 14) == 100  # só altas
    assert rsi(list(range(16, 0, -1)), 14) == 0  # só quedas
    assert rsi([10, 11] * 8, 14) == pytest.approx(50, abs=5)
    assert rsi([1, 2, 3], 14) is None  # dados insuficientes


def test_volatility():
    assert annualized_volatility([10] * 30) == 0
    # dois retornos log: +ln(1.1) e -ln(1.1) -> desvio amostral = ln(1.1)*sqrt(2)
    expected = math.log(1.1) * math.sqrt(2) * math.sqrt(252)
    assert annualized_volatility([10, 11, 10]) == pytest.approx(expected)
    assert annualized_volatility([10, 11]) is None


def test_period_return():
    assert period_return([10, 11, 12, 15], 3) == pytest.approx(0.5)
    assert period_return([10, 11], 3) is None


def test_compare_to_median_direction_and_tolerance():
    out = compare_to_median(
        {"pe": 8, "ev_ebitda": 10.5, "net_debt_ebitda": 3, "net_margin": 0.05, "roe": None},
        {"pe": 10, "ev_ebitda": 10, "net_debt_ebitda": 2, "net_margin": 0.10, "roe": 0.15},
    )
    assert out == {
        "pe": "melhor",  # menor é melhor
        "ev_ebitda": "na_media",  # dentro de 10% da mediana
        "net_debt_ebitda": "pior",
        "net_margin": "pior",  # maior é melhor
        "roe": None,
    }


def test_compare_without_median_is_none():
    assert compare_to_median({"pe": 8}, {"pe": None}) == {"pe": None}
