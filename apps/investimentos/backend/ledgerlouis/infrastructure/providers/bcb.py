from datetime import datetime

import httpx

from .types import MacroData, dec

SOURCE = "bcb-sgs"

# código SGS -> (nome, unidade)
SERIES = {
    432: ("Selic meta", "% a.a."),
    13522: ("IPCA 12 meses", "%"),
    1: ("Dólar PTAX (venda)", "R$"),
}


def sgs_url(code: int, last: int) -> str:
    return f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados/ultimos/{last}?formato=json"


class BcbClient:
    def __init__(self, http: httpx.Client | None = None):
        self.http = http or httpx.Client(timeout=20)

    def series(self, code: int, last: int) -> list[MacroData]:
        r = self.http.get(sgs_url(code, last))
        r.raise_for_status()
        return [
            MacroData(date=datetime.strptime(p["data"], "%d/%m/%Y").date(), value=dec(p["valor"]))
            for p in r.json()
        ]
