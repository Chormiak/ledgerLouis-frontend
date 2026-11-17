from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from ledgerlouis.market.models import Asset

from . import services as s
from .models import Alert, Holding, InvestorProfile, PendingChange, Proposal, ProposalItem


def local_api(methods):
    """Uso local de um só usuário (servidor em localhost): sem sessão, sem CSRF."""

    def wrap(fn):
        return api_view(methods)(authentication_classes([])(permission_classes([])(fn)))

    return wrap


@local_api(["GET", "PUT"])
def profile(request):
    p = InvestorProfile.get()
    if request.method == "PUT":
        errors = s.update_profile(p, request.data)
        if errors:
            return Response({"errors": errors}, status=400)
    return Response(s.profile_payload(p))


@api_view()
def portfolio(request):
    return Response(s.portfolio_payload())


@local_api(["PUT", "DELETE"])
def holding(request, ticker):
    asset = get_object_or_404(Asset, ticker=ticker.upper())
    if request.method == "DELETE":
        Holding.objects.filter(asset=asset).delete()
        return Response(status=204)
    qty, avg = s._dec(request.data.get("quantity")), s._dec(request.data.get("avg_price"))
    if qty is None or qty <= 0 or (avg is not None and avg <= 0):
        return Response({"error": "quantidade deve ser maior que zero; preço médio, se informado, também"}, status=400)
    Holding.objects.update_or_create(asset=asset, defaults={"quantity": qty, "avg_price": avg})
    return Response(s.portfolio_payload())


def item_payload(it: ProposalItem) -> dict:
    q = it.asset.latest_quote()
    return {
        "id": it.id,
        "ticker": it.asset.ticker,
        "name": it.asset.name,
        "sector": it.asset.sector,
        "action": it.action,
        "target_weight": it.target_weight,
        "thesis": it.thesis,
        "risks": it.risks,
        "invalidation": it.invalidation,
        "sources": it.sources,
        "price_at_proposal": it.price_at_proposal,
        "current_price": q.price if q else None,
        "decision": it.decision,
        "adjusted_weight": it.adjusted_weight,
        "comment": it.comment,
        "decided_at": it.decided_at,
    }


def proposal_head(p: Proposal) -> dict:
    return {"id": p.id, "period": p.period, "created_at": p.created_at, "status": p.status, "count": p.items.count()}


@api_view()
def proposals(request):
    return Response([proposal_head(p) for p in Proposal.objects.prefetch_related("items")])


@api_view()
def proposal_detail(request, pk):
    p = get_object_or_404(Proposal, pk=pk)
    items = p.items.select_related("asset")
    weights = [i.adjusted_weight if i.decision == "ajustado" else i.target_weight for i in items if i.decision != "recusado"]
    return Response(
        {
            **proposal_head(p),
            "summary": p.summary,
            "profile_snapshot": p.profile_snapshot,
            "items": [item_payload(i) for i in items],
            "approved_weight": sum(weights, Decimal(0)),
        }
    )


@local_api(["POST"])
def decision(request, pk):
    it = get_object_or_404(ProposalItem.objects.select_related("asset"), pk=pk)
    try:
        s.decide(it, request.data.get("decision"), request.data.get("adjusted_weight"), request.data.get("comment") or "")
    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)
    return Response(item_payload(it))


@api_view()
def alerts(request):
    return Response(
        [
            {"id": a.id, "kind": a.kind, "title": a.title, "ticker": a.asset and a.asset.ticker, "detail": a.detail,
             "created_on": a.created_on, "seen": a.seen}
            for a in Alert.objects.select_related("asset")[:100]
        ]
    )


@local_api(["POST"])
def alert_seen(request, pk):
    Alert.objects.filter(pk=pk).update(seen=True)
    return Response(status=204)


@api_view()
def scoreboard(request):
    return Response(s.scoreboard())


def change_payload(c: PendingChange) -> dict:
    return {"id": c.id, "kind": c.kind, "payload": c.payload, "reason": c.reason, "status": c.status,
            "created_at": c.created_at, "decided_at": c.decided_at}


@api_view()
def pending_changes(request):
    return Response([change_payload(c) for c in PendingChange.objects.filter(status="pendente")[:50]])


@local_api(["POST"])
def decide_change(request, pk, verb):
    c = get_object_or_404(PendingChange, pk=pk)
    try:
        (s.apply_change if verb == "apply" else s.reject_change)(c)
    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)
    return Response(change_payload(c))
