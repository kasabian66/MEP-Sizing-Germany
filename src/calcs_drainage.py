
from __future__ import annotations
from typing import Dict, List
import math
from .utils import Advisory

def rain_flow_lps(area_m2: float, r_lps_m2: float) -> float:
    return area_m2 * r_lps_m2

def suggest_rain_pipe_d_mm(q_lps: float, v: float = 2.0) -> float:
    # Simplified full-flow circular pipe
    q = q_lps / 1000.0
    d = math.sqrt(4*q/(math.pi*v))
    return d*1000.0

def wastewater_flow_lps(dfus: float, k: float=0.5) -> float:
    # Placeholder: dfus is "equivalent fixture flow sum" in L/s.
    # k is a crude simultaneity factor.
    return dfus * k

def drainage_advisories() -> List[Advisory]:
    return [
        Advisory("warning", "For final design: DIN EN 12056 (gravity drainage) and DIN 1986-100 (German scope for private ground drainage)."),
        Advisory("info", "Rain intensity r must come from local datasets (e.g., KOSTRA/DWD) per the adopted method."),
    ]
