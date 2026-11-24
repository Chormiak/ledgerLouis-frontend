from decimal import Decimal as D

from ledgerlouis.domain.groups import median, summarize


def test_median_odd_even_and_missing():
    assert median([D(3), D(1), D(2)]) == D(2)
    assert median([D(1), D(2), D(3), D(10)]) == D("2.5")
    assert median([None, D(4), None]) == D(4)
    assert median([None]) is None
    assert median([]) is None


def member(cap, change, pe=None):
    return {"market_cap": cap, "change_pct": change, "indicators": {"pe": pe, "roe": None}}


def test_summarize_weights_change_by_market_cap():
    s = summarize([member(D(1), D(10), D(8)), member(D(3), D(0), D(12)), member(None, D(5))])
    assert s["count"] == 3
    assert s["market_cap"] == D(4)
    assert s["change_pct"] == D("2.5")
    assert s["medians"] == {"pe": D(10), "roe": None}


def test_summarize_empty_group():
    s = summarize([])
    assert s == {"count": 0, "market_cap": None, "change_pct": None, "medians": {}}
