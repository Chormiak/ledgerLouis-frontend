from decimal import Decimal as D

from ledgerlouis.domain.alerts import Thresholds, triggers

T = Thresholds(daily_drop_pct=D(5), max_asset_weight=D("0.20"), max_sector_weight=D("0.35"))


def p(ticker, weight, change, sector="S"):
    return {"ticker": ticker, "sector": sector, "weight": D(weight), "change_pct": None if change is None else D(change)}


def test_daily_drop():
    [t] = triggers([p("AAAA3", "0.1", "-6.2")], {"S": D("0.1")}, T, [])
    assert (t.kind, t.ticker, t.key) == ("queda_forte", "AAAA3", "queda_forte:AAAA3")
    assert t.detail["change_pct"] == D("-6.2")
    assert t.title == "AAAA3 caiu 6,2% hoje"


def test_drop_exactly_at_threshold_triggers_and_missing_change_does_not():
    kinds = [t.kind for t in triggers([p("AAAA3", "0.1", "-5"), p("BBBB3", "0.1", None)], {}, T, [])]
    assert kinds == ["queda_forte"]


def test_concentration_asset_and_sector():
    out = triggers([p("AAAA3", "0.25", "0", "Fin")], {"Fin": D("0.40"), "Tec": D("0.10")}, T, [])
    assert sorted((t.kind, t.key) for t in out) == [
        ("concentracao_ativo", "concentracao_ativo:AAAA3"),
        ("concentracao_setor", "concentracao_setor:Fin"),
    ]


def test_titles_use_decimal_comma():
    out = triggers([p("AAAA3", "0.372", "0", "Fin")], {"Fin": D("0.372")}, T, [])
    assert {t.title for t in out} == {"AAAA3 ocupa 37,2% da carteira", "Fin ocupa 37,2% da carteira"}


def test_new_filing_for_holding():
    filings = [{"ticker": "AAAA3", "title": "Fato relevante: X", "url": "https://cvm/1"}]
    [t] = triggers([], {}, T, filings)
    assert (t.kind, t.key) == ("fato_relevante", "fato_relevante:https://cvm/1")


def test_nothing_to_report():
    assert triggers([p("AAAA3", "0.1", "1")], {"S": D("0.1")}, T, []) == []
