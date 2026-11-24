"""Seed fixo das grandes empresas de tecnologia/IA dos EUA. Editável depois no /admin.

Aliases ajudam a casar notícia: ticker dos EUA raramente aparece literal no título
(diferente de "PETR4" na B3).
"""

US_STOCKS = [
    {"ticker": "AAPL", "name": "Apple", "aliases": ["Apple"]},
    {"ticker": "MSFT", "name": "Microsoft", "aliases": ["Microsoft"]},
    {"ticker": "GOOGL", "name": "Alphabet", "aliases": ["Google", "Alphabet"]},
    {"ticker": "AMZN", "name": "Amazon", "aliases": ["Amazon"]},
    {"ticker": "NVDA", "name": "Nvidia", "aliases": ["Nvidia"]},
    {"ticker": "META", "name": "Meta", "aliases": ["Meta", "Facebook"]},
    {"ticker": "TSLA", "name": "Tesla", "aliases": ["Tesla"]},
    {"ticker": "AMD", "name": "AMD", "aliases": ["AMD"]},
    {"ticker": "AVGO", "name": "Broadcom", "aliases": ["Broadcom"]},
    {"ticker": "ORCL", "name": "Oracle", "aliases": ["Oracle"]},
    {"ticker": "CRM", "name": "Salesforce", "aliases": ["Salesforce"]},
    {"ticker": "ADBE", "name": "Adobe", "aliases": ["Adobe"]},
    {"ticker": "PLTR", "name": "Palantir", "aliases": ["Palantir"]},
    {"ticker": "SNOW", "name": "Snowflake", "aliases": ["Snowflake"]},
    {"ticker": "IBM", "name": "IBM", "aliases": ["IBM"]},
    {"ticker": "INTC", "name": "Intel", "aliases": ["Intel"]},
    {"ticker": "NOW", "name": "ServiceNow", "aliases": ["ServiceNow"]},
    {"ticker": "SMCI", "name": "Super Micro Computer", "aliases": ["Super Micro", "Supermicro"]},
    {"ticker": "MU", "name": "Micron", "aliases": ["Micron"]},
    {"ticker": "TSM", "name": "TSMC", "aliases": ["TSMC", "Taiwan Semiconductor"]},
]

US_NICHE_NAME = "Global Tech & IA (EUA)"
