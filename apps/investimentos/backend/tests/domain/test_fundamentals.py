from decimal import Decimal as D

import pytest

from ledgerlouis.domain import fundamentals as f


def test_price_to_earnings():
    assert f.price_to_earnings(D(30), D(3)) == D(10)


@pytest.mark.parametrize("eps", [D(0), D(-2), None])
def test_price_to_earnings_without_profit_is_none(eps):
    assert f.price_to_earnings(D(30), eps) is None


def test_enterprise_value():
    assert f.enterprise_value(D(100), D(40), D(10)) == D(130)


def test_ev_to_ebitda():
    assert f.ev_to_ebitda(D(130), D(13)) == D(10)


@pytest.mark.parametrize("ebitda", [D(0), D(-5), None])
def test_ebitda_not_positive_is_none(ebitda):
    assert f.ev_to_ebitda(D(130), ebitda) is None
    assert f.net_debt_to_ebitda(D(40), D(10), ebitda) is None


def test_net_debt_to_ebitda():
    assert f.net_debt_to_ebitda(D(40), D(10), D(15)) == D(2)


def test_net_cash_gives_negative_leverage():
    assert f.net_debt_to_ebitda(D(10), D(40), D(15)) == D(-2)


def test_net_income_from_eps():
    assert f.net_income_from_eps(D(3), D(1000), D(30)) == D(100)


def test_net_margin():
    assert f.net_margin(D(100), D(400)) == D("0.25")


@pytest.mark.parametrize("revenue", [D(0), D(-1), None])
def test_net_margin_without_revenue_is_none(revenue):
    assert f.net_margin(D(100), revenue) is None


def test_any_missing_input_is_none():
    assert f.enterprise_value(None, D(1), D(1)) is None
    assert f.net_income_from_eps(D(1), None, D(1)) is None
    assert f.net_income_from_eps(D(1), D(1), D(0)) is None


def test_compute_indicators():
    out = f.compute_indicators(
        {
            "price": D(30),
            "market_cap": D(1000),
            "eps": D(3),
            "revenue": D(400),
            "ebitda": D(13),
            "total_debt": D(40),
            "total_cash": D(10),
            "roe_reported": D("0.18"),
        }
    )
    assert out == {
        "pe": D(10),
        "ev_ebitda": D(1030) / D(13),
        "net_debt_ebitda": D(30) / D(13),
        "net_margin": D("0.25"),
        "roe": D("0.18"),
    }


def test_compute_indicators_with_nothing():
    assert set(f.compute_indicators({}).values()) == {None}
