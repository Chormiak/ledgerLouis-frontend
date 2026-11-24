from decimal import Decimal

from django.db import models

from ledgerlouis.market.models import Asset

MONEY = {"max_digits": 24, "decimal_places": 4}
WEIGHT = {"max_digits": 7, "decimal_places": 6}  # fração: 0.250000 = 25%


class InvestorProfile(models.Model):
    """Linha única. Nada é assumido: campos vazios ficam vazios e a proposta avisa."""

    RISK = [("conservador", "Conservador"), ("moderado", "Moderado"), ("arrojado", "Arrojado")]

    horizon_years = models.PositiveSmallIntegerField(null=True, blank=True)
    risk_tolerance = models.CharField(max_length=20, choices=RISK, blank=True)
    monthly_contribution = models.DecimalField(**MONEY, null=True, blank=True)
    avoid_sectors = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    # limiares dos alertas, editáveis
    alert_daily_drop_pct = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal(5))
    alert_max_asset_weight = models.DecimalField(**WEIGHT, default=Decimal("0.20"))
    alert_max_sector_weight = models.DecimalField(**WEIGHT, default=Decimal("0.35"))
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get(cls) -> "InvestorProfile":
        return cls.objects.get_or_create(pk=1)[0]


class Holding(models.Model):
    asset = models.OneToOneField(Asset, on_delete=models.PROTECT, related_name="holding")
    quantity = models.DecimalField(max_digits=20, decimal_places=6)
    avg_price = models.DecimalField(**MONEY, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class Proposal(models.Model):
    period = models.CharField(max_length=20)  # ex.: "2026-11"
    summary = models.TextField()
    profile_snapshot = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def status(self) -> str:
        decisions = [i.decision for i in self.items.all()]
        if all(d == ProposalItem.PENDING for d in decisions):
            return "rascunho"
        return "concluida" if ProposalItem.PENDING not in decisions else "em_revisao"


class ProposalItem(models.Model):
    PENDING = "pendente"
    DECISIONS = [(PENDING, "Pendente"), ("aprovado", "Aprovado"), ("recusado", "Recusado"), ("ajustado", "Ajustado")]
    ACTIONS = [(a, a.capitalize()) for a in ("entrar", "sair", "aumentar", "reduzir", "manter")]

    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name="items")
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)
    action = models.CharField(max_length=20, choices=ACTIONS)
    target_weight = models.DecimalField(**WEIGHT)
    thesis = models.TextField()
    risks = models.TextField()
    invalidation = models.TextField()
    sources = models.JSONField(default=list)
    price_at_proposal = models.DecimalField(**MONEY, null=True, blank=True)
    decision = models.CharField(max_length=20, choices=DECISIONS, default=PENDING)
    adjusted_weight = models.DecimalField(**WEIGHT, null=True, blank=True)
    comment = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-target_weight"]


EXPECTATION = {"entrar": "alta", "aumentar": "alta", "sair": "baixa", "reduzir": "baixa", "manter": "neutra"}


class Thesis(models.Model):
    """Entrada do placar: o que se esperava, a que preço e quando. Avaliada contra o preço atual."""

    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name="theses")
    summary = models.TextField()
    expectation = models.CharField(max_length=10, choices=[("alta", "Alta"), ("baixa", "Baixa"), ("neutra", "Neutra")])
    entry_price = models.DecimalField(**MONEY, null=True, blank=True)
    horizon_days = models.PositiveIntegerField(null=True, blank=True)
    sources = models.JSONField(default=list)
    origin = models.CharField(max_length=20, default="avulsa")  # "proposta" ou "avulsa"
    decision = models.CharField(max_length=20, blank=True)
    proposal_item = models.OneToOneField(ProposalItem, null=True, blank=True, on_delete=models.CASCADE, related_name="thesis_record")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Alert(models.Model):
    kind = models.CharField(max_length=30)
    key = models.CharField(max_length=300)
    title = models.CharField(max_length=500)
    asset = models.ForeignKey(Asset, null=True, blank=True, on_delete=models.CASCADE)
    detail = models.JSONField(default=dict)
    created_on = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    class Meta:
        ordering = ["seen", "-created_at"]
        constraints = [models.UniqueConstraint(fields=["key", "created_on"], name="unique_alert_per_day")]


class PendingChange(models.Model):
    """Sugestão do Claude para a carteira ou o perfil. Só vale depois que o Erick aplica na interface."""

    kind = models.CharField(max_length=20, choices=[("holding", "Posição"), ("profile", "Perfil")])
    payload = models.JSONField()
    reason = models.TextField()
    status = models.CharField(max_length=20, default="pendente")  # pendente, aplicada, recusada
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
