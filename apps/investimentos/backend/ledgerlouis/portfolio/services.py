"""Casos de uso da carteira, compartilhados pela API REST e pelo servidor MCP."""

from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from ledgerlouis.domain.alerts import Thresholds, triggers
from ledgerlouis.domain.portfolio import exposure, validate_proposal, valuate
from ledgerlouis.market.models import Asset, NewsItem

from .models import EXPECTATION, Alert, Holding, InvestorProfile, PendingChange, Proposal, ProposalItem, Thesis


class ProposalInvalid(ValueError):
    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


def _dec(x) -> Decimal | None:
    if x is None or x == "":
        return None
    try:
        return Decimal(str(x))
    except InvalidOperation:
        return None


def _weight_ok(v) -> bool:
    d = _dec(v)
    return d is not None and 0 < d <= 1


PROFILE_RULES = {
    "horizon_years": lambda v: v is None or (isinstance(v, int) and 0 <= v <= 100),
    "risk_tolerance": lambda v: v in {"", "conservador", "moderado", "arrojado"},
    "monthly_contribution": lambda v: v in (None, "") or (_dec(v) is not None and _dec(v) >= 0),
    "avoid_sectors": lambda v: isinstance(v, list) and all(isinstance(x, str) for x in v),
    "notes": lambda v: isinstance(v, str),
    "alert_daily_drop_pct": lambda v: _dec(v) is not None and 0 < _dec(v) <= 100,
    "alert_max_asset_weight": _weight_ok,
    "alert_max_sector_weight": _weight_ok,
}


def update_profile(p: InvestorProfile, data: dict) -> list[str]:
    """Valida e grava só os campos conhecidos. Devolve os campos inválidos (nada é gravado se houver algum)."""
    data = {k: v for k, v in data.items() if k in PROFILE_RULES}
    errors = [k for k, v in data.items() if not PROFILE_RULES[k](v)]
    if errors:
        return errors
    for k, v in data.items():
        setattr(p, k, _dec(v) if k == "monthly_contribution" or k.startswith("alert_") else v)
    p.save()
    return []


def profile_payload(p: InvestorProfile | None = None) -> dict:
    p = p or InvestorProfile.get()
    return {
        "horizon_years": p.horizon_years,
        "risk_tolerance": p.risk_tolerance,
        "monthly_contribution": p.monthly_contribution,
        "avoid_sectors": p.avoid_sectors,
        "notes": p.notes,
        "alert_daily_drop_pct": p.alert_daily_drop_pct,
        "alert_max_asset_weight": p.alert_max_asset_weight,
        "alert_max_sector_weight": p.alert_max_sector_weight,
        "missing": [f for f in ("horizon_years", "risk_tolerance", "monthly_contribution") if getattr(p, f) in (None, "")],
    }


def portfolio_payload() -> dict:
    positions = []
    for h in Holding.objects.select_related("asset"):
        q = h.asset.latest_quote()
        price = q.price if q else None
        positions.append(
            {
                "ticker": h.asset.ticker,
                "name": h.asset.name,
                "sector": h.asset.sector,
                "quantity": h.quantity,
                "avg_price": h.avg_price,
                "price": price,
                "change_pct": q.change_pct if q else None,
                "gain_pct": price / h.avg_price - 1 if price is not None and h.avg_price else None,
                "source": q.source if q else None,
                "fetched_at": q.fetched_at if q else None,
            }
        )
    v = valuate(positions)
    return {**v, "exposure": {"sector": exposure(v["positions"], "sector")}, "profile": profile_payload()}


def save_proposal(period: str, summary: str, items: list[dict]) -> Proposal:
    """Grava rascunho. Qualquer problema rejeita a proposta inteira, com a lista completa."""
    parsed = [it | {"target_weight": _dec(it.get("target_weight")), "ticker": str(it.get("ticker", "")).strip().upper()} for it in items]
    assets = {a.ticker: a for a in Asset.objects.filter(ticker__in=[it["ticker"] for it in parsed])}
    problems = validate_proposal(parsed, set(assets))
    if not str(period).strip() or not str(summary).strip():
        problems.insert(0, "período e resumo são obrigatórios")
    if problems:
        raise ProposalInvalid(problems)
    with transaction.atomic():
        prop = Proposal.objects.create(period=period.strip(), summary=summary.strip(), profile_snapshot=_jsonable(profile_payload()))
        for it in parsed:
            a = assets[it["ticker"]]
            q = a.latest_quote()
            ProposalItem.objects.create(
                proposal=prop,
                asset=a,
                action=it["action"],
                target_weight=it["target_weight"],
                thesis=it["thesis"].strip(),
                risks=it["risks"].strip(),
                invalidation=it["invalidation"].strip(),
                sources=list(it["sources"]),
                price_at_proposal=q.price if q else None,
            )
    return prop


def _jsonable(d: dict) -> dict:
    return {k: (str(v) if isinstance(v, Decimal) else v) for k, v in d.items()}


def decide(item: ProposalItem, decision: str, adjusted_weight=None, comment: str = "") -> ProposalItem:
    """Ação exclusiva do Erick (interface). Registra/atualiza a tese no placar."""
    if decision not in {"aprovado", "recusado", "ajustado"}:
        raise ValueError("decisão deve ser aprovado, recusado ou ajustado")
    weight = _dec(adjusted_weight)
    if decision == "ajustado" and (weight is None or not 0 <= weight <= 1):
        raise ValueError("ajuste precisa de um novo peso entre 0 e 100%")
    with transaction.atomic():
        item.decision = decision
        item.adjusted_weight = weight if decision == "ajustado" else None
        item.comment = comment.strip()
        item.decided_at = timezone.now()
        item.save()
        Thesis.objects.update_or_create(
            proposal_item=item,
            defaults={
                "asset": item.asset,
                "summary": item.thesis,
                "expectation": EXPECTATION[item.action],
                "entry_price": item.price_at_proposal,
                "sources": item.sources,
                "origin": "proposta",
                "decision": decision,
            },
        )
    return item


def record_thesis(ticker: str, summary: str, expectation: str, horizon_days: int | None = None, sources=None) -> Thesis:
    a = Asset.objects.filter(ticker=str(ticker).strip().upper()).first()
    if not a:
        raise ValueError(f"ticker não está na base: {ticker}")
    if expectation not in {"alta", "baixa", "neutra"}:
        raise ValueError("expectation deve ser alta, baixa ou neutra")
    if not str(summary).strip() or not sources:
        raise ValueError("tese precisa de resumo e de ao menos uma fonte")
    q = a.latest_quote()
    return Thesis.objects.create(
        asset=a, summary=summary.strip(), expectation=expectation, entry_price=q.price if q else None,
        horizon_days=horizon_days, sources=list(sources),
    )


def scoreboard() -> dict:
    rows = []
    for t in Thesis.objects.select_related("asset"):
        q = t.asset.latest_quote()
        current = q.price if q else None
        ret = current / t.entry_price - 1 if current is not None and t.entry_price else None
        hit = None
        if ret and t.expectation != "neutra":  # retorno 0 = ainda sem movimento: não dá para julgar
            hit = ret > 0 if t.expectation == "alta" else ret < 0
        rows.append(
            {
                "ticker": t.asset.ticker,
                "summary": t.summary,
                "expectation": t.expectation,
                "origin": t.origin,
                "decision": t.decision,
                "entry_price": t.entry_price,
                "current_price": current,
                "return_pct": ret,
                "hit": hit,
                "created_at": t.created_at,
                "horizon_days": t.horizon_days,
                "price_source": q.source if q else None,
                "price_fetched_at": q.fetched_at if q else None,
            }
        )
    scored = [r for r in rows if r["hit"] is not None]
    hits = sum(r["hit"] for r in scored)
    return {"rows": rows, "scored": len(scored), "hits": hits, "hit_rate": Decimal(hits) / len(scored) if scored else None}


def run_alerts(today=None) -> int:
    """Avalia os gatilhos sobre a carteira e grava alertas novos. Devolve quantos foram criados."""
    today = today or timezone.localdate()
    p = InvestorProfile.get()
    port = portfolio_payload()
    held = {x["ticker"] for x in port["positions"]}
    recent = NewsItem.objects.filter(
        kind="fato_relevante", assets__ticker__in=held, published_at__gte=timezone.now() - timedelta(days=3)
    ).prefetch_related("assets")
    filings = [
        {"ticker": a.ticker, "title": n.title, "url": n.url}
        for n in recent
        for a in n.assets.all()
        if a.ticker in held and not Alert.objects.filter(key=f"fato_relevante:{n.url}").exists()
    ]
    found = triggers(
        port["positions"],
        port["exposure"]["sector"],
        Thresholds(p.alert_daily_drop_pct, p.alert_max_asset_weight, p.alert_max_sector_weight),
        filings,
    )
    assets = {a.ticker: a for a in Asset.objects.filter(ticker__in=held)}
    created = 0
    for t in found:
        _, new = Alert.objects.get_or_create(
            key=t.key,
            created_on=today,
            defaults={"kind": t.kind, "title": t.title, "asset": assets.get(t.ticker), "detail": _jsonable(t.detail)},
        )
        created += new
    return created


# ---- Sugestões do Claude: ele propõe, o Erick aplica ou recusa na interface ----


def propose_holding_change(ticker: str, quantity, avg_price=None, reason: str = "") -> PendingChange:
    """quantity 0 = remover a posição."""
    a = Asset.objects.filter(ticker=str(ticker).strip().upper()).first()
    if not a:
        raise ValueError(f"ticker não está na base: {ticker}")
    qty, avg = _dec(quantity), _dec(avg_price)
    if qty is None or qty < 0 or (avg is not None and avg <= 0):
        raise ValueError("quantidade deve ser 0 (remover) ou positiva; preço médio, se informado, positivo")
    if qty == 0 and not Holding.objects.filter(asset=a).exists():
        raise ValueError(f"{a.ticker} não está na carteira para ser removida")
    if not str(reason).strip():
        raise ValueError("explique o motivo da sugestão")
    return PendingChange.objects.create(
        kind="holding", reason=reason.strip(),
        payload={"ticker": a.ticker, "quantity": str(qty), "avg_price": None if avg is None else str(avg)},
    )


def propose_profile_change(changes: dict, reason: str = "") -> PendingChange:
    unknown = [k for k in changes if k not in PROFILE_RULES]
    invalid = [k for k, v in changes.items() if k in PROFILE_RULES and not PROFILE_RULES[k](v)]
    if not changes or unknown or invalid:
        raise ValueError(f"mudança de perfil inválida; desconhecidos: {unknown}, inválidos: {invalid}")
    if not str(reason).strip():
        raise ValueError("explique o motivo da sugestão")
    return PendingChange.objects.create(kind="profile", payload=changes, reason=reason.strip())


def apply_change(c: PendingChange) -> None:
    """Ação exclusiva do Erick. Revalida no momento de aplicar: os dados podem ter mudado desde a sugestão."""
    if c.status != "pendente":
        raise ValueError("esta sugestão já foi decidida")
    with transaction.atomic():
        if c.kind == "holding":
            a = Asset.objects.get(ticker=c.payload["ticker"])
            qty = _dec(c.payload["quantity"])
            if qty == 0:
                Holding.objects.filter(asset=a).delete()
            else:
                Holding.objects.update_or_create(asset=a, defaults={"quantity": qty, "avg_price": _dec(c.payload["avg_price"])})
        else:
            errors = update_profile(InvestorProfile.get(), c.payload)
            if errors:
                raise ValueError(f"campos inválidos: {', '.join(errors)}")
        c.status, c.decided_at = "aplicada", timezone.now()
        c.save()


def reject_change(c: PendingChange) -> None:
    if c.status != "pendente":
        raise ValueError("esta sugestão já foi decidida")
    c.status, c.decided_at = "recusada", timezone.now()
    c.save()
