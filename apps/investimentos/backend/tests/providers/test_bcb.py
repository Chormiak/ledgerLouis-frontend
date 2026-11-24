from datetime import date
from decimal import Decimal as D

import httpx
import respx

from ledgerlouis.infrastructure.providers.bcb import BcbClient, sgs_url


@respx.mock
def test_series_parses_dates_and_values():
    respx.get(sgs_url(432, 2)).mock(
        return_value=httpx.Response(
            200, json=[{"data": "30/09/2026", "valor": "10.50"}, {"data": "01/10/2026", "valor": "10,75"}]
        )
    )
    points = BcbClient().series(432, last=2)
    assert [(p.date, p.value) for p in points] == [
        (date(2026, 9, 30), D("10.50")),
        (date(2026, 10, 1), D("10.75")),
    ]
