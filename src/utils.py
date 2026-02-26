
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
import math
import pandas as pd

COPPER_RESISTIVITY_OHM_MM2_PER_M = 0.0175  # approx at 20°C

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def kva_from_kw(kw: float, pf: float) -> float:
    if pf <= 0:
        return float('nan')
    return kw / pf

def current_3ph_from_kw(kw: float, v_ll: float = 400.0, pf: float = 0.9, eff: float = 0.95) -> float:
    # I = P / (sqrt(3) * V * pf * eff)
    denom = math.sqrt(3) * v_ll * pf * eff
    if denom <= 0:
        return float('nan')
    return (kw * 1000.0) / denom

def voltage_drop_3ph_percent(i_a: float, length_m: float, v_ll: float, s_mm2: float, cosphi: float = 0.9) -> float:
    # Simplified 3-phase voltage drop (resistive dominated):
    # ΔU ≈ sqrt(3) * I * R * L ; R = rho / S
    if s_mm2 <= 0 or v_ll <= 0:
        return float('nan')
    r_per_m = COPPER_RESISTIVITY_OHM_MM2_PER_M / s_mm2
    du = math.sqrt(3) * i_a * r_per_m * length_m
    return (du / v_ll) * 100.0

STANDARD_CU_SECTIONS_MM2 = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240]

# Very simplified conservative ampacity table for Cu multi-core cable in conduit/tray in building services.
# NOTE: Real design must use VDE 0298-4 / IEC 60364-5-52 correction factors.
SIMPLIFIED_AMPACITY_A = {
    1.5: 16,
    2.5: 20,
    4: 26,
    6: 34,
    10: 46,
    16: 61,
    25: 80,
    35: 99,
    50: 119,
    70: 151,
    95: 182,
    120: 210,
    150: 240,
    185: 273,
    240: 320,
}

def pick_cable_section(i_design_a: float, max_vdrop_pct: float, length_m: float, v_ll: float = 400.0) -> Tuple[float, float]:
    """Pick smallest standard section meeting simplified ampacity and voltage drop."""
    for s in STANDARD_CU_SECTIONS_MM2:
        amp = SIMPLIFIED_AMPACITY_A.get(s, 1e9)
        if i_design_a <= amp:
            vd = voltage_drop_3ph_percent(i_design_a, length_m, v_ll, s)
            if vd <= max_vdrop_pct:
                return s, vd
    # if none fits: return largest
    s = STANDARD_CU_SECTIONS_MM2[-1]
    vd = voltage_drop_3ph_percent(i_design_a, length_m, v_ll, s)
    return s, vd

@dataclass
class Advisory:
    level: str  # "info" | "warning" | "danger"
    text: str

def advisories_to_df(advs: List[Advisory]) -> pd.DataFrame:
    return pd.DataFrame([{"Level": a.level, "Alert": a.text} for a in advs])
