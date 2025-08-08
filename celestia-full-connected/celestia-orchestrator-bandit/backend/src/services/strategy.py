from __future__ import annotations
from typing import List, Dict
from sources.capabilities import SOURCE_PRIORS, Mode

def decide_mode(source: str, *, creds_ok: bool, http_health: dict[str, dict]) -> List[Mode]:
    # Heurística baseada em priors + saúde HTTP
    priors = SOURCE_PRIORS.get(source, [Mode.HTTP])
    # se Selenium na frente mas não há credenciais, empurra Selenium p/ o fim
    if priors and priors[0] == Mode.SELENIUM and not creds_ok:
        priors = [m for m in priors if m != Mode.SELENIUM] + [Mode.SELENIUM]

    sr_http = http_health.get(source, {}).get("success_rate_http", 0.0)
    # Boost HTTP se a taxa de sucesso recente for boa
    if sr_http >= 0.6 and Mode.HTTP in priors:
        ordered = [Mode.HTTP] + [m for m in priors if m != Mode.HTTP]
    else:
        ordered = priors
    return ordered
