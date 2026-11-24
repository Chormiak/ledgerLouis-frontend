import io
import zipfile
from datetime import date

import httpx
import pytest
import respx

from ledgerlouis.infrastructure.providers.cvm import CvmClient, CvmFormatError, fca_url, ipe_url, only_digits

IPE_HEADER = "CNPJ_Companhia;Nome_Companhia;Codigo_CVM;Data_Referencia;Categoria;Tipo;Especie;Assunto;Data_Entrega;Tipo_Apresentacao;Protocolo_Entrega;Versao;Link_Download"


def zipped(name: str, text: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(name, text.encode("latin-1"))
    return buf.getvalue()


IPE = "\n".join(
    [
        IPE_HEADER,
        "33.000.167/0001-01;PETRÓLEO BRASILEIRO S.A.;9512;2026-10-20;Fato Relevante;;;Aquisição de participação;2026-10-21;AP;1;1;https://cvm/1",
        "33.000.167/0001-01;PETRÓLEO BRASILEIRO S.A.;9512;2026-10-20;Assembleia;;;Edital;2026-10-21;AP;2;1;https://cvm/2",
        "33.592.510/0001-54;VALE S.A.;4170;2026-10-22;Comunicado ao Mercado;;;Produção do trimestre;2026-10-23;AP;3;1;https://cvm/3",
    ]
)


@respx.mock
def test_filings_keeps_relevant_categories_and_decodes_latin1():
    respx.get(ipe_url(2026)).mock(return_value=httpx.Response(200, content=zipped("ipe_cia_aberta_2026.csv", IPE)))
    filings = CvmClient().filings(2026)
    assert [(f.cnpj, f.kind, f.url) for f in filings] == [
        ("33000167000101", "fato_relevante", "https://cvm/1"),
        ("33592510000154", "comunicado", "https://cvm/3"),
    ]
    assert filings[0].title == "Fato relevante: Aquisição de participação"
    assert filings[0].company == "PETRÓLEO BRASILEIRO S.A."
    assert filings[0].delivered == date(2026, 10, 21)


@respx.mock
def test_missing_column_is_a_clear_error():
    respx.get(ipe_url(2026)).mock(
        return_value=httpx.Response(200, content=zipped("ipe_cia_aberta_2026.csv", "CNPJ_Companhia;Assunto\n1;x"))
    )
    with pytest.raises(CvmFormatError, match="Categoria"):
        CvmClient().filings(2026)


@respx.mock
def test_tickers_by_cnpj_from_fca():
    fca = "\n".join(
        [
            "CNPJ_Companhia;Nome_Empresarial;Valor_Mobiliario;Codigo_Negociacao;Mercado",
            "33.000.167/0001-01;PETROBRAS;Ações Ordinárias;PETR3;Bolsa",
            "33.000.167/0001-01;PETROBRAS;Ações Preferenciais;PETR4;Bolsa",
            "33.000.167/0001-01;PETROBRAS;Debêntures;;Balcão",
        ]
    )
    other = "CNPJ_Companhia;Outro\n1;2"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("fca_cia_aberta_geral_2026.csv", other.encode("latin-1"))
        z.writestr("fca_cia_aberta_valor_mobiliario_2026.csv", fca.encode("latin-1"))
    respx.get(fca_url(2026)).mock(return_value=httpx.Response(200, content=buf.getvalue()))
    assert CvmClient().tickers_by_cnpj(2026) == {"33000167000101": {"PETR3", "PETR4"}}


def test_only_digits():
    assert only_digits("33.000.167/0001-01") == "33000167000101"
