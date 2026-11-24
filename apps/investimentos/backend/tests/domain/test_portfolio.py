from decimal import Decimal as D

from ledgerlouis.domain.portfolio import exposure, valuate, validate_proposal


def pos(ticker, qty, price, sector="S"):
    return {"ticker": ticker, "sector": sector, "quantity": D(qty), "price": None if price is None else D(price)}


def test_valuate_values_and_weights():
    out = valuate([pos("AAAA3", 10, 30, "Fin"), pos("BBBB3", 10, 10, "Fin"), pos("CCCC3", 5, None, "Tec")])
    by = {p["ticker"]: p for p in out["positions"]}
    assert out["total"] == D(400)
    assert by["AAAA3"]["value"] == D(300)
    assert by["AAAA3"]["weight"] == D("0.75")
    assert by["CCCC3"]["value"] is None and by["CCCC3"]["weight"] is None
    assert out["unpriced"] == ["CCCC3"]


def test_valuate_empty():
    assert valuate([]) == {"positions": [], "total": None, "unpriced": []}


def test_exposure_by_sector():
    out = valuate([pos("AAAA3", 10, 30, "Fin"), pos("BBBB3", 10, 10, "Tec")])
    assert exposure(out["positions"], "sector") == {"Fin": D("0.75"), "Tec": D("0.25")}


def item(ticker="AAAA3", weight="0.2", **kw):
    base = {
        "ticker": ticker,
        "action": "entrar",
        "target_weight": D(weight),
        "thesis": "tese",
        "risks": "riscos",
        "invalidation": "o que invalida",
        "sources": ["brapi 2026-10-29"],
    }
    return base | kw


def test_valid_proposal_has_no_problems():
    assert validate_proposal([item(), item("BBBB3", "0.8")], {"AAAA3", "BBBB3"}) == []


def test_proposal_problems_are_all_listed():
    problems = validate_proposal(
        [
            item("NADA3"),
            item("AAAA3", "-0.1"),
            item("BBBB3", "0.95", sources=[]),
            item("CCCC3", thesis=" ", action="comprar"),
        ],
        {"AAAA3", "BBBB3", "CCCC3"},
    )
    text = " | ".join(problems)
    assert "NADA3: ticker fora da base" in text
    assert "AAAA3: peso fora de 0 a 100%" in text
    assert "BBBB3: sem fontes" in text
    assert "CCCC3: tese vazia" in text
    assert "CCCC3: ação inválida" in text
    assert "soma dos pesos" in text


def test_duplicate_ticker_is_a_problem():
    assert any("repetido" in p for p in validate_proposal([item(), item()], {"AAAA3"}))


def test_empty_proposal_is_a_problem():
    assert validate_proposal([], set()) == ["a proposta não tem itens"]
