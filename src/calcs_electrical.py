
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple
import math
import pandas as pd

from .utils import current_3ph_from_kw, pick_cable_section, Advisory

MOTOR_START_METHODS = {
    "Direct on line (DOL)": 6.0,
    "Star-delta": 2.5,
    "Soft-starter": 3.0,
    "VFD (inverter)": 1.2,
}

@dataclass
class LoadItem:
    name: str
    kw: float
    simultaneity: float

def compute_demand(loads: List[LoadItem]) -> Tuple[float, pd.DataFrame]:
    rows=[]
    total_inst=0.0
    total_dem=0.0
    for l in loads:
        inst=l.kw
        dem=l.kw*l.simultaneity
        total_inst += inst
        total_dem += dem
        rows.append({
            "Load": l.name,
            "P instalada (kW)": round(inst,3),
            "Simultaneity": round(l.simultaneity,3),
            "P demanda (kW)": round(dem,3),
        })
    df=pd.DataFrame(rows)
    return total_dem, df

def motor_design_current(kw: float, v_ll: float, pf: float, eff: float, start_method: str) -> Dict[str,float]:
    i_nom = current_3ph_from_kw(kw, v_ll=v_ll, pf=pf, eff=eff)
    mult = MOTOR_START_METHODS.get(start_method, 6.0)
    i_start = i_nom * mult
    return {"I_nom_A": i_nom, "I_start_A": i_start, "mult": mult}

def size_feeder(
    p_dem_kw: float,
    v_ll: float = 400.0,
    pf: float = 0.9,
    eff: float = 0.95,
    length_m: float = 50.0,
    max_vdrop_pct: float = 3.0,
    add_motor: bool = False,
    motor_kw: float = 0.0,
    motor_start_method: str = "Direct on line (DOL)",
) -> Dict[str, object]:
    adv=[]
    i_base = current_3ph_from_kw(p_dem_kw, v_ll=v_ll, pf=pf, eff=eff)
    i_design = i_base

    motor_info=None
    if add_motor and motor_kw>0:
        motor_info = motor_design_current(motor_kw, v_ll, pf, eff, motor_start_method)
        # For protective device and cable thermal sizing, keep i_base;
        # For instantaneous/trip considerations, report I_start and advise.
        adv.append(Advisory("warning",
            f"Motor included: I_start≈{motor_info['I_start_A']:.0f} A (x{motor_info['mult']:.1f} of I_nom). "
            "Check instantaneous breaker trip, starting voltage drop and coordination."))
    # Select section with simplified criteria
    s_mm2, vdrop = pick_cable_section(i_design, max_vdrop_pct, length_m, v_ll=v_ll)

    # Approx short-circuit at end (very rough): Ik ≈ V / (sqrt(3) * R_loop)
    # assume loop resistance ~ 2 * rho * L / S (phase+PE), copper.
    rho = 0.0175
    r_loop = 2 * rho * length_m / s_mm2
    ik = (v_ll) / (math.sqrt(3) * r_loop) if r_loop>0 else float('nan')

    if vdrop > max_vdrop_pct:
        adv.append(Advisory("danger", "Voltage drop exceeds the limit. Increase section or reduce length/load."))
    if ik < 1000:
        adv.append(Advisory("warning",
            "Estimated end short-circuit is low. Verify real impedance, trip times and network conditions."))

    return {
        "P_dem_kW": p_dem_kw,
        "I_design_A": i_design,
        "Section_mm2": s_mm2,
        "Vdrop_pct": vdrop,
        "Ik_end_A_approx": ik,
        "motor": motor_info,
        "advisories": adv,
    }
