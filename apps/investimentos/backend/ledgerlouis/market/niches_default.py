"""Ponto de partida dos nichos. Edite no admin: tickers mudam (fusões, trocas de código).

Só os tickers já presentes na base são ligados; os demais são ignorados sem erro.
Códigos macro: 432 Selic, 13522 IPCA 12m, 1 Dólar PTAX.
"""

from .us_stocks_default import US_NICHE_NAME, US_STOCKS

DEFAULT_NICHES = [
    {
        "name": "Varejo",
        "description": "Varejo de moda, supermercados, e-commerce e lojas especializadas.",
        "macro": ["432", "13522"],
        "tickers": ["MGLU3", "LREN3", "ASAI3", "CRFB3", "PETZ3", "SBFG3", "AZZA3", "GMAT3"],
    },
    {
        "name": "IA e tecnologia",
        "description": "Software, dados e plataformas digitais na B3, e BDRs de tecnologia quando estiverem na base.",
        "macro": ["432", "1"],
        "tickers": ["TOTS3", "LWSA3", "POSI3", "INTB3", "BMOB3", "NVDC34", "MSFT34", "GOGL34"],
    },
    {
        "name": "Imóveis",
        "description": "Construtoras, shoppings e fundos imobiliários.",
        "macro": ["432", "13522"],
        "tickers": ["CYRE3", "MRVE3", "EZTC3", "DIRR3", "CURY3", "MULT3", "ALOS3", "IGTI11", "HGLG11", "KNRI11", "XPML11"],
    },
    {
        "name": "Bancos e financeiro",
        "description": "Bancos, seguradoras, holdings financeiras e a bolsa.",
        "macro": ["432"],
        "tickers": ["ITUB4", "BBDC4", "BBAS3", "SANB11", "BPAC11", "B3SA3", "BBSE3", "ITSA4"],
    },
    {
        "name": "Energia e saneamento",
        "description": "Geração, transmissão e distribuição de energia, e saneamento.",
        "macro": ["432", "13522"],
        "tickers": ["AXIA3", "EGIE3", "TAEE11", "CMIG4", "SBSP3", "EQTL3", "ENGI11", "CPFE3"],
    },
    {
        "name": "Commodities",
        "description": "Petróleo, minério, siderurgia e celulose.",
        "macro": ["1"],
        "tickers": ["PETR4", "PETR3", "VALE3", "PRIO3", "GGBR4", "CSNA3", "SUZB3", "KLBN11", "CMIN3", "USIM5"],
    },
    {
        "name": "Agronegócio",
        "description": "Produtores, terras agrícolas, açúcar e etanol, insumos.",
        "macro": ["1"],
        "tickers": ["SLCE3", "AGRO3", "SMTO3", "TTEN3", "SOJA3"],
    },
    {
        "name": "Saúde",
        "description": "Hospitais, planos, laboratórios e farmácias.",
        "macro": ["13522", "432"],
        "tickers": ["RDOR3", "HAPV3", "FLRY3", "RADL3", "HYPE3", "ODPV3"],
    },
    {
        "name": US_NICHE_NAME,
        "description": "Grandes empresas de tecnologia e IA dos EUA, direto da bolsa americana (fora da B3).",
        "macro": [],
        "tickers": [s["ticker"] for s in US_STOCKS],
        "external": True,  # fora da listagem de "Setores e nichos"; a tela própria busca pelo slug
    },
]

# Feeds iniciais de geopolítica e "bolha da IA" (editável depois no /admin, igual os nichos).
DEFAULT_NEWS_FEEDS = [
    {"name": "BBC World News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml", "category": "geopolitica"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "category": "geopolitica"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "category": "ia_bolha"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "category": "ia_bolha"},
]
