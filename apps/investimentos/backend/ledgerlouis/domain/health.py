"""Semáforo de saúde relativo: cada indicador contra a mediana do grupo. Sem limites absolutos inventados."""

LOWER_IS_BETTER = {"pe", "ev_ebitda", "net_debt_ebitda"}
TOLERANCE = 0.10  # dentro de 10% da mediana conta como "na média"


def compare_to_median(indicators: dict, medians: dict) -> dict:
    out = {}
    for k, v in indicators.items():
        m = medians.get(k)
        if v is None or m is None:
            out[k] = None
            continue
        v, m = float(v), float(m)
        diff = (m - v) if k in LOWER_IS_BETTER else (v - m)  # positivo = melhor que a mediana
        band = abs(m) * TOLERANCE
        out[k] = "na_media" if abs(diff) <= band else "melhor" if diff > 0 else "pior"
    return out
