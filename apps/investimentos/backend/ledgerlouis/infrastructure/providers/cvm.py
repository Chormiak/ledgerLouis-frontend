"""Dados abertos da CVM: fatos relevantes (IPE) e mapa CNPJ -> tickers (FCA valor_mobiliario)."""

import csv
import io
import re
import zipfile
from dataclasses import dataclass
from datetime import date

import httpx

SOURCE = "CVM"
BASE = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC"
KINDS = {"Fato Relevante": "fato_relevante", "Comunicado ao Mercado": "comunicado"}


class CvmFormatError(Exception):
    pass


def ipe_url(year: int) -> str:
    return f"{BASE}/IPE/DADOS/ipe_cia_aberta_{year}.zip"


def fca_url(year: int) -> str:
    return f"{BASE}/FCA/DADOS/fca_cia_aberta_{year}.zip"


def only_digits(cnpj: str) -> str:
    return re.sub(r"\D", "", cnpj)


@dataclass(frozen=True)
class Filing:
    cnpj: str
    company: str
    kind: str
    title: str
    delivered: date
    url: str


def read_csv_from_zip(content: bytes, name_contains: str, required: list[str]) -> list[dict]:
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        names = [n for n in z.namelist() if name_contains in n and n.endswith(".csv")]
        if not names:
            raise CvmFormatError(f"arquivo com '{name_contains}' não encontrado no ZIP da CVM")
        raw = z.read(names[0])
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")  # a CVM costuma publicar em latin-1
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    missing = [c for c in required if c not in (reader.fieldnames or [])]
    if missing:
        raise CvmFormatError(f"coluna ausente no CSV da CVM ({names[0]}): {', '.join(missing)}")
    return list(reader)


class CvmClient:
    def __init__(self, http: httpx.Client | None = None):
        self.http = http or httpx.Client(timeout=120, follow_redirects=True)

    def _get(self, url: str) -> bytes:
        r = self.http.get(url)
        r.raise_for_status()
        return r.content

    def filings(self, year: int) -> list[Filing]:
        cols = ["CNPJ_Companhia", "Nome_Companhia", "Categoria", "Assunto", "Data_Entrega", "Link_Download"]
        rows = read_csv_from_zip(self._get(ipe_url(year)), "ipe_cia_aberta", cols)
        return [
            Filing(
                cnpj=only_digits(r["CNPJ_Companhia"]),
                company=r["Nome_Companhia"],
                kind=KINDS[r["Categoria"]],
                title=f"{r['Categoria'].capitalize()}: {r['Assunto']}"[:500],
                delivered=date.fromisoformat(r["Data_Entrega"][:10]),
                url=r["Link_Download"],
            )
            for r in rows
            if r["Categoria"] in KINDS and r["Link_Download"]
        ]

    def tickers_by_cnpj(self, year: int) -> dict[str, set[str]]:
        rows = read_csv_from_zip(
            self._get(fca_url(year)), "valor_mobiliario", ["CNPJ_Companhia", "Codigo_Negociacao"]
        )
        out: dict[str, set[str]] = {}
        for r in rows:
            ticker = (r["Codigo_Negociacao"] or "").strip().upper()
            if ticker:
                out.setdefault(only_digits(r["CNPJ_Companhia"]), set()).add(ticker)
        return out
