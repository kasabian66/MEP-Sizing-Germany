
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
import pandas as pd
from .utils import Advisory, clamp

# Simplified fixture unit approach (not a substitute for DIN 1988-300 / EN 806-3)
FIXTURE_DEFAULTS = {
    "Washbasin": {"q_lps": 0.07},
    "Shower": {"q_lps": 0.15},
    "WC cistern": {"q_lps": 0.13},
    "Kitchen sink": {"q_lps": 0.10},
    "Urinal": {"q_lps": 0.10},
}

def peak_flow_lps(fixtures: Dict[str,int], simultaneity: float) -> Dict[str, float]:
    simultaneity = clamp(simultaneity, 0.1, 1.0)
    q_sum = 0.0
    for k,n in fixtures.items():
        q = FIXTURE_DEFAULTS.get(k, {"q_lps":0.1})["q_lps"]
        q_sum += q * n
    q_peak = q_sum * simultaneity
    return {"q_sum_lps": q_sum, "q_peak_lps": q_peak, "simultaneity": simultaneity}

def suggest_pipe_diameter_mm(q_lps: float, v_max: float = 2.0) -> float:
    # d = sqrt(4Q/(pi*v)) ; Q in m3/s
    import math
    q = q_lps / 1000.0
    if v_max<=0: v_max=2.0
    d = math.sqrt(4*q/(math.pi*v_max))
    return d*1000.0  # mm

def acs_energy_kwh_per_day(persons: int, liters_per_person_day: float, deltaT_K: float = 35.0, eff: float=0.9) -> float:
    # E = m*cp*ΔT ; m~liters kg ; cp 4.186 kJ/kgK
    m = persons * liters_per_person_day
    e_kj = m * 4.186 * deltaT_K
    e_kwh = e_kj / 3600.0
    return e_kwh/eff

def plumbing_advisories() -> List[Advisory]:
    return [
        Advisory("warning", "This module uses a simplified method. For final sizing: DIN 1988-300 and EN 806-3 (and DVGW requirements)."),
        Advisory("info", "Typical internal network velocities are usually limited (e.g., 2 m/s as a reference)."),
    ]
