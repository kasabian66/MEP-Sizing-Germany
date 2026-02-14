
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
import pandas as pd
from .utils import Advisory, clamp

# Very simplified benchmark ranges (user can override)
DEFAULT_LOADS_W_M2 = {
    "Office": {"heat": 50, "cool": 70},
    "Retail": {"heat": 60, "cool": 100},
    "Residential": {"heat": 45, "cool": 50},
    "Data/IT (light)": {"heat": 80, "cool": 150},
}

# Ventilation baseline (EN 16798 categories; examples from REHVA slide deck)
VENT_CAT = {
    "Cat I": {"lps_person": 10.0, "lps_m2": 1.0},
    "Cat II": {"lps_person": 7.0, "lps_m2": 0.7},
    "Cat III": {"lps_person": 4.0, "lps_m2": 0.4},
}

def hvac_predim(area_m2: float, use: str, heat_w_m2: float, cool_w_m2: float, diversity: float) -> Dict[str, float]:
    diversity = clamp(diversity, 0.3, 1.0)
    qh_kw = area_m2 * heat_w_m2 / 1000.0 * diversity
    qc_kw = area_m2 * cool_w_m2 / 1000.0 * diversity
    return {"Q_heat_kW": qh_kw, "Q_cool_kW": qc_kw, "diversity": diversity}

def ventilation_flow(area_m2: float, persons: int, category: str) -> Dict[str,float]:
    cat = VENT_CAT.get(category, VENT_CAT["Cat II"])
    q_lps = persons * cat["lps_person"] + area_m2 * cat["lps_m2"]
    q_m3h = q_lps * 3.6
    ach = None
    return {"q_outdoor_lps": q_lps, "q_outdoor_m3h": q_m3h, "category": category}

def hvac_advisories(use: str) -> List[Advisory]:
    adv=[]
    adv.append(Advisory("info", "Pre-sizing based on adjustable specific loads (W/m²)."))
    adv.append(Advisory("warning",
        "For final design: detailed heating calc per DIN EN 12831-1 / DIN/TS 12831-1 and cooling per VDI 2078."))
    if use.lower().startswith("data"):
        adv.append(Advisory("warning", "IT rooms: heat loads and N+1 redundancy typically require detailed engineering."))
    return adv
