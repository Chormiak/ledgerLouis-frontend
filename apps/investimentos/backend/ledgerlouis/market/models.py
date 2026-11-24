from django.db import models

MONEY = {"max_digits": 24, "decimal_places": 4, "null": True, "blank": True}
RATIO = {"max_digits": 18, "decimal_places": 8, "null": True, "blank": True}


class Asset(models.Model):
    MARKET_CHOICES = [("B3", "B3"), ("US", "US")]

    ticker = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=200)
    kind = models.CharField(max_length=20, default="stock")
    market = models.CharField(max_length=2, choices=MARKET_CHOICES, default="B3")
    sector = models.CharField(max_length=100, blank=True)
    subsector = models.CharField(max_length=100, blank=True)
    logo_url = models.URLField(max_length=500, blank=True)
    cnpj = models.CharField(max_length=18, blank=True, db_index=True)  # liga fatos relevantes da CVM
    aliases = models.JSONField(default=list, blank=True)  # nomes alternativos para casar notícia (ex.: "Amazon")
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["ticker"]

    def __str__(self):
        return self.ticker

    def latest_quote(self):
        return self.quotes.order_by("-fetched_at").first()

    def latest_fundamentals(self):
        return self.fundamentals.order_by("-fetched_at").first()


class Quote(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="quotes")
    price = models.DecimalField(**MONEY)
    change_pct = models.DecimalField(**RATIO)  # em pontos percentuais, como a fonte entrega (1.5 = +1,5%)
    volume = models.DecimalField(**MONEY)
    market_cap = models.DecimalField(**MONEY)
    source = models.CharField(max_length=50)
    fetched_at = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [models.Index(fields=["asset", "-fetched_at"], name="quote_latest_per_asset")]


class FundamentalsSnapshot(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="fundamentals")
    revenue = models.DecimalField(**MONEY)
    ebitda = models.DecimalField(**MONEY)
    total_debt = models.DecimalField(**MONEY)
    total_cash = models.DecimalField(**MONEY)
    eps = models.DecimalField(**RATIO)
    roe_reported = models.DecimalField(**RATIO)  # fração (0.18 = 18%)
    source = models.CharField(max_length=50)
    fetched_at = models.DateTimeField(db_index=True)


class MacroPoint(models.Model):
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)
    date = models.DateField()
    value = models.DecimalField(max_digits=18, decimal_places=6)
    source = models.CharField(max_length=50)
    fetched_at = models.DateTimeField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["code", "date"], name="unique_macro_point")]
        ordering = ["code", "-date"]


class Niche(models.Model):
    """Grupo temático editável pelo Erick (ex.: IA e tecnologia), atravessando setores e países."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    macro_codes = models.JSONField(default=list, blank=True)  # códigos de MacroPoint relevantes
    assets = models.ManyToManyField(Asset, related_name="niches", blank=True)
    external = models.BooleanField(default=False)  # fora de "/grupos": a tela própria busca pelo slug direto

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class NewsFeed(models.Model):
    CATEGORY_CHOICES = [("ticker", "ticker"), ("geopolitica", "geopolítica"), ("ia_bolha", "bolha da IA")]

    name = models.CharField(max_length=100)
    url = models.URLField(unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="ticker")
    active = models.BooleanField(default=True)
    fetched_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class NewsItem(models.Model):
    """Só título, link, fonte e data: nunca o texto da matéria."""

    title = models.CharField(max_length=500)
    url = models.URLField(max_length=600, unique=True)
    source = models.CharField(max_length=100)
    kind = models.CharField(max_length=40)  # "fato_relevante", "comunicado", "noticia"
    published_at = models.DateTimeField(db_index=True)
    assets = models.ManyToManyField(Asset, related_name="news", blank=True)

    class Meta:
        ordering = ["-published_at"]


class ScreenContext(models.Model):
    """O que está aberto no dashboard agora (linha única). Lido pelo servidor MCP, que é outro processo."""

    payload = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)


class PriceBar(models.Model):
    """Candle diário. O plano gratuito da brapi cobre cerca de 3 meses."""

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="bars")
    date = models.DateField()
    open = models.DecimalField(**MONEY)
    high = models.DecimalField(**MONEY)
    low = models.DecimalField(**MONEY)
    close = models.DecimalField(**MONEY)
    volume = models.DecimalField(**MONEY)
    source = models.CharField(max_length=50)
    fetched_at = models.DateTimeField()

    class Meta:
        ordering = ["date"]
        constraints = [models.UniqueConstraint(fields=["asset", "date"], name="unique_bar_per_day")]


class ScreenCommand(models.Model):
    """Pedido do Claude para o dashboard (ex.: abrir uma tela). O frontend consulta os novos e executa."""

    action = models.CharField(max_length=30)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
