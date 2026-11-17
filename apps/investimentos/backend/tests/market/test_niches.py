import pytest

from ledgerlouis.market.management.commands.seed_niches import seed_niches
from ledgerlouis.market.models import Asset, Niche

pytestmark = pytest.mark.django_db


def test_seed_niches_links_only_existing_tickers_and_is_idempotent():
    Asset.objects.create(ticker="MGLU3", name="Magalu")
    Asset.objects.create(ticker="TOTS3", name="Totvs")

    seed_niches()
    seed_niches()

    assert Niche.objects.count() == 9
    varejo = Niche.objects.get(slug="varejo")
    assert list(varejo.assets.values_list("ticker", flat=True)) == ["MGLU3"]
    assert Niche.objects.get(slug="ia-e-tecnologia").assets.get().ticker == "TOTS3"
    assert varejo.macro_codes == ["432", "13522"]
    assert not Asset.objects.filter(ticker="LREN3").exists()
