from datetime import timedelta
from decimal import Decimal as D

import pytest
from django.utils import timezone

from ledgerlouis.market.models import Asset, NewsItem, Quote
from ledgerlouis.portfolio import services as s
from ledgerlouis.portfolio.models import Alert, Holding, InvestorProfile, ProposalItem, Thesis

pytestmark = pytest.mark.django_db


def asset(ticker, price, change="0", sector="Fin"):
    a = Asset.objects.create(ticker=ticker, name=ticker, sector=sector)
    if price is not None:
        Quote.objects.create(asset=a, price=D(price), change_pct=D(change), market_cap=D(1000), source="brapi", fetched_at=timezone.now())
    return a


def item(ticker, weight, action="entrar"):
    return {
        "ticker": ticker,
        "action": action,
        "target_weight": weight,
        "thesis": f"tese {ticker}",
        "risks": "riscos",
        "invalidation": "invalida se...",
        "sources": ["brapi, 29/10/2026"],
    }


def test_portfolio_payload_values_weights_and_unpriced():
    a, b, c = asset("AAAA3", "30", sector="Fin"), asset("BBBB3", "10", sector="Tec"), asset("CCCC3", None)
    Holding.objects.create(asset=a, quantity=D(10), avg_price=D(20))
    Holding.objects.create(asset=b, quantity=D(10))
    Holding.objects.create(asset=c, quantity=D(1))
    p = s.portfolio_payload()
    by = {x["ticker"]: x for x in p["positions"]}
    assert p["total"] == D(400)
    assert by["AAAA3"]["weight"] == D("0.75")
    assert by["AAAA3"]["gain_pct"] == D("0.5")
    assert by["BBBB3"]["gain_pct"] is None
    assert p["unpriced"] == ["CCCC3"]
    assert p["exposure"]["sector"] == {"Fin": D("0.75"), "Tec": D("0.25")}
    assert p["profile"]["risk_tolerance"] == ""


def test_save_proposal_valid_records_price_and_profile():
    asset("AAAA3", "30")
    InvestorProfile.objects.create(pk=1, risk_tolerance="moderado")
    prop = s.save_proposal("2026-11", "resumo", [item("AAAA3", 0.3)])
    it = prop.items.get()
    assert (it.target_weight, it.price_at_proposal) == (D("0.3"), D(30))
    assert prop.profile_snapshot["risk_tolerance"] == "moderado"
    assert prop.status == "rascunho"


def test_save_proposal_invalid_saves_nothing():
    asset("AAAA3", "30")
    with pytest.raises(s.ProposalInvalid) as exc:
        s.save_proposal("2026-11", "resumo", [item("AAAA3", 0.7), item("NADA3", 0.5)])
    assert any("NADA3" in p for p in exc.value.problems)
    assert any("soma dos pesos" in p for p in exc.value.problems)
    assert not ProposalItem.objects.exists()


def test_decide_creates_then_updates_thesis():
    asset("AAAA3", "30")
    it = s.save_proposal("2026-11", "resumo", [item("AAAA3", 0.3)]).items.get()
    s.decide(it, "aprovado", comment="ok")
    s.decide(it, "ajustado", adjusted_weight=D("0.2"), comment="menos")
    t = Thesis.objects.get()
    assert (t.decision, t.expectation, t.entry_price, t.origin) == ("ajustado", "alta", D(30), "proposta")
    it.refresh_from_db()
    assert (it.decision, it.adjusted_weight, it.comment) == ("ajustado", D("0.2"), "menos")
    assert it.proposal.status == "concluida"


@pytest.mark.parametrize("kwargs", [{"decision": "ajustado"}, {"decision": "pendente"}, {"decision": "talvez"}, {"decision": "ajustado", "adjusted_weight": D("1.5")}])
def test_decide_rejects_invalid(kwargs):
    asset("AAAA3", "30")
    it = s.save_proposal("2026-11", "resumo", [item("AAAA3", 0.3)]).items.get()
    with pytest.raises(ValueError):
        s.decide(it, **kwargs)


def test_scoreboard_scores_direction():
    a = asset("AAAA3", "30")
    b = asset("BBBB3", "10")
    s.record_thesis("AAAA3", "deve subir", "alta", sources=["x"])
    s.record_thesis("BBBB3", "deve cair", "baixa", sources=["x"])
    s.record_thesis("BBBB3", "lateral", "neutra", sources=["x"])
    Quote.objects.create(asset=a, price=D(33), source="brapi", fetched_at=timezone.now() + timedelta(seconds=1))
    Quote.objects.create(asset=b, price=D(11), source="brapi", fetched_at=timezone.now() + timedelta(seconds=1))
    board = s.scoreboard()
    by = {(r["ticker"], r["expectation"]): r for r in board["rows"]}
    assert by[("AAAA3", "alta")]["return_pct"] == D("0.1")
    assert by[("AAAA3", "alta")]["hit"] is True
    assert by[("BBBB3", "baixa")]["hit"] is False
    assert by[("BBBB3", "neutra")]["hit"] is None
    assert (board["scored"], board["hits"], board["hit_rate"]) == (2, 1, D("0.5"))


def test_thesis_without_price_movement_is_not_scored():
    asset("AAAA3", "30")
    s.record_thesis("AAAA3", "deve subir", "alta", sources=["x"])
    board = s.scoreboard()
    assert board["rows"][0]["hit"] is None
    assert board["scored"] == 0 and board["hit_rate"] is None


def test_record_thesis_validates():
    asset("AAAA3", "30")
    with pytest.raises(ValueError):
        s.record_thesis("NADA3", "x", "alta", sources=["x"])
    with pytest.raises(ValueError):
        s.record_thesis("AAAA3", "x", "lua", sources=["x"])
    with pytest.raises(ValueError):
        s.record_thesis("AAAA3", "x", "alta", sources=[])


def test_run_alerts_creates_once_per_day():
    a = asset("AAAA3", "30", change="-7")
    Holding.objects.create(asset=a, quantity=D(10))
    news = NewsItem.objects.create(title="Fato relevante: X", url="https://cvm/1", source="CVM", kind="fato_relevante", published_at=timezone.now())
    news.assets.add(a)
    assert s.run_alerts() == 4  # queda, ativo 100%, setor 100%, fato relevante
    assert s.run_alerts() == 0
    assert set(Alert.objects.values_list("kind", flat=True)) == {"queda_forte", "concentracao_ativo", "concentracao_setor", "fato_relevante"}


def test_run_alerts_with_empty_portfolio():
    assert s.run_alerts() == 0
