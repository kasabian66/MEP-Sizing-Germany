
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, Tuple

DATA_PATH = Path(__file__).resolve().parent.parent / "data"

# Ventilation (outdoor air) category defaults — indicative values aligned with EN 16798 examples.
# Note: ventilation flow targets depend mainly on IAQ category and occupancy, not on climate.
VENT_CAT_DEFAULTS = {
    "Cat I": {"qp_Ls_per_person": 10.0, "qB_Ls_per_m2": 1.0},
    "Cat II": {"qp_Ls_per_person": 7.0, "qB_Ls_per_m2": 0.7},
    "Cat III": {"qp_Ls_per_person": 4.0, "qB_Ls_per_m2": 0.4},
}

def estimate_ventilation_flow_m3h(area_m2: float, persons: int, vent_cat: str = "Cat II") -> dict:
    """Estimate outdoor air flow using people + area method (pre-sizing).

    q = n*qp + A*qB
    where qp and qB are in L/s.
    Returns both L/s and m³/h.
    """
    area_m2 = max(0.0, float(area_m2))
    persons = max(0, int(persons))
    d = VENT_CAT_DEFAULTS.get(str(vent_cat), VENT_CAT_DEFAULTS["Cat II"])
    qp = float(d["qp_Ls_per_person"])
    qB = float(d["qB_Ls_per_m2"])
    q_ls = persons * qp + area_m2 * qB
    q_m3h = q_ls * 3.6  # 1 L/s = 3.6 m3/h
    return {"vent_cat": str(vent_cat), "qp_Ls_per_person": qp, "qB_Ls_per_m2": qB, "q_Ls": q_ls, "q_m3h": q_m3h}

def ventilation_sensible_loads_kw(q_m3h: float, t_in_C: float, t_out_C: float) -> float:
    """Sensible ventilation load (kW), very simplified.
    Uses rho_air=1.2 kg/m3 and cp=1.005 kJ/kgK.
    """
    rho = 1.2
    cp_kJ = 1.005
    q_m3s = max(0.0, float(q_m3h)) / 3600.0
    m_dot = rho * q_m3s  # kg/s
    dT = float(t_out_C) - float(t_in_C)
    # kW = (kg/s)*(kJ/kgK)*(K) = kJ/s = kW
    return m_dot * cp_kJ * dT

def load_use_profiles() -> Dict[str, Any]:
    return json.load(open(DATA_PATH / "use_profiles.json", "r", encoding="utf-8"))

def load_city_presets() -> Dict[str, Any]:
    return json.load(open(DATA_PATH / "city_presets.json", "r", encoding="utf-8"))

def estimate_occupancy(area_above_m2: float, use_profile: Dict[str, Any]) -> int:
    m2_per_person = float(use_profile.get("occupancy_m2_per_person", 10) or 10)
    if m2_per_person <= 0:
        m2_per_person = 10
    return int(max(0, round(area_above_m2 / m2_per_person)))

def estimate_tech_rooms_and_shafts(area_total_m2: float, floors_above: int, use_profile: Dict[str, Any]) -> Dict[str, float]:
    tech_ratio = float(use_profile.get("tech_rooms_ratio", 0.015) or 0.015)
    shafts_ratio = float(use_profile.get("shafts_ratio", 0.008) or 0.008)
    tech_m2 = max(0.0, area_total_m2 * tech_ratio)
    shafts_m2 = max(0.0, area_total_m2 * shafts_ratio)
    floors_above = max(1, int(floors_above or 1))
    return {
        "tech_rooms_m2": tech_m2,
        "shafts_m2": shafts_m2,
        "shafts_m2_per_floor": shafts_m2 / floors_above,
    }

def estimate_hvac_electrical_kw(area_above_m2: float, use_profile: Dict[str, Any], design_summer_C: float = 32.0) -> Tuple[float, Dict[str, float]]:
    # Very simplified: P_elec ≈ Q_cool / EER + fans/aux
    cool_w_m2 = float(use_profile.get("cooling_W_m2", 0) or 0)
    eer = float(use_profile.get("hvac_eer_cooling", 3.0) or 3.0)
    fans_w_m2 = float(use_profile.get("hvac_fans_W_m2", 5.0) or 5.0)
    cool_factor = climate_adjust_cooling_factor(float(design_summer_C))
    hvac_elec_w_m2 = ((cool_w_m2 * cool_factor) / eer) + fans_w_m2
    hvac_kw = max(0.0, area_above_m2) * hvac_elec_w_m2 / 1000.0
    return hvac_kw, {
        "cooling_W_m2": cool_w_m2,
        "eer": eer,
        "fans_W_m2": fans_w_m2,
        "hvac_elec_W_m2": hvac_elec_w_m2,
        "cooling_factor": cool_factor,
    }

def estimate_lifts_kw(area_above_m2: float, use_profile: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
    area_per_lift = float(use_profile.get("lift_area_m2_per_lift", 5000) or 5000)
    p_per_lift = float(use_profile.get("lift_power_kW_per_lift", 15.0) or 0.0)
    diversity = float(use_profile.get("lift_diversity", 0.6) or 0.0)
    if p_per_lift <= 0 or diversity <= 0 or area_above_m2 <= 0:
        return 0.0, {"n_lifts": 0, "area_m2_per_lift": area_per_lift, "power_kW_per_lift": p_per_lift, "diversity": diversity}
    n_lifts = max(1, int(math.ceil(area_above_m2 / area_per_lift)))
    lifts_kw = n_lifts * p_per_lift * diversity
    return lifts_kw, {
        "n_lifts": n_lifts,
        "area_m2_per_lift": area_per_lift,
        "power_kW_per_lift": p_per_lift,
        "diversity": diversity,
    }

def estimate_electrical_loads(area_above_m2: float, use_profile: Dict[str, Any]) -> Dict[str, float]:
    lighting_w_m2 = float(use_profile.get("lighting_W_m2", 8) or 0)
    sockets_w_m2 = float(use_profile.get("sockets_W_m2", 15) or 0)
    other_w_m2 = float(use_profile.get("other_W_m2", 5) or 0)
    lighting_kw = area_above_m2 * lighting_w_m2 / 1000.0
    sockets_kw = area_above_m2 * sockets_w_m2 / 1000.0
    other_kw = area_above_m2 * other_w_m2 / 1000.0
    hvac_kw, _ = estimate_hvac_electrical_kw(area_above_m2, use_profile)
    lifts_kw, _ = estimate_lifts_kw(area_above_m2, use_profile)
    return {
        "lighting_kw": lighting_kw,
        "sockets_kw": sockets_kw,
        "hvac_kw": hvac_kw,
        "lifts_kw": lifts_kw,
        "other_kw": other_kw,
    }


def climate_adjust_cooling_factor(summer_temp_C: float, reference_summer_C: float = 32.0) -> float:
    """Very simplified climate adjustment for cooling loads (pre-sizing).

    Assumption: sensible cooling demand scales approximately with ΔT above indoor setpoint.
    Factor = (Tout_summer - Tin_summer) / (Tref_summer - Tin_summer)
    using Tin_summer = 26°C and reference_summer = 32°C by default.
    """
    T_in = 26.0
    denom = (float(reference_summer_C) - T_in)
    if denom <= 0:
        return 1.0
    factor = (float(summer_temp_C) - T_in) / denom
    return max(0.7, min(1.4, float(factor)))

def climate_adjust_heating_factor(design_temp_C: float, reference_temp_C: float = -10.0) -> float:
    """Very simplified climate adjustment for heating loads (pre-sizing).

    Assumption: heating specific load scales approximately with ΔT.
    Factor = (Tindoor - Tout_design) / (Tindoor - Tref)
    using Tindoor = 20°C and Tref = -10°C by default.
    """
    T_in = 20.0
    denom = (T_in - float(reference_temp_C))
    if denom <= 0:
        return 1.0
    factor = (T_in - float(design_temp_C)) / denom
    return max(0.7, min(1.4, float(factor)))

def estimate_hvac_capacities(
    area_above_m2: float,
    use_profile: Dict[str, Any],
    diversity: float = 0.8,
    design_temp_C: float = -10.0,
    persons: int = 0,
    vent_cat: str = "Cat II",
    design_summer_C: float = 32.0,
) -> Dict[str, float]:
    """Very simplified HVAC capacity pre-sizing (kW).

    - Base loads use W/m² benchmarks from the use profile.
    - Adds a simplified sensitivity for climate using design winter/summer temperatures.
    - Adds sensible ventilation load from the EN 16798-style people+area outdoor air flow estimate.

    This is NOT a DIN EN 12831 or VDI 2078 compliant load calculation.
    """
    heat_w_m2 = float(use_profile.get("heating_W_m2", 50) or 0)
    cool_w_m2 = float(use_profile.get("cooling_W_m2", 70) or 0)
    diversity = max(0.3, min(1.0, float(diversity)))

    heat_factor = climate_adjust_heating_factor(design_temp_C)
    cool_factor = climate_adjust_cooling_factor(design_summer_C)

    # Ventilation outdoor air flow (people + area method)
    vent = estimate_ventilation_flow_m3h(area_above_m2, persons, vent_cat)
    q_m3h = float(vent["q_m3h"])

    # Sensible ventilation loads (kW)
    vent_heat_kw = -ventilation_sensible_loads_kw(q_m3h, t_in_C=20.0, t_out_C=design_temp_C)  # heating magnitude
    vent_cool_kw = max(0.0, ventilation_sensible_loads_kw(q_m3h, t_in_C=26.0, t_out_C=design_summer_C))  # cooling magnitude

    base_heat_kw = max(0.0, area_above_m2) * heat_w_m2 / 1000.0 * diversity * heat_factor
    base_cool_kw = max(0.0, area_above_m2) * cool_w_m2 / 1000.0 * diversity * cool_factor

    return {
        "heating_kw": float(base_heat_kw + max(0.0, vent_heat_kw)),
        "cooling_kw": float(base_cool_kw + max(0.0, vent_cool_kw)),
        "heat_W_m2": float(heat_w_m2),
        "cool_W_m2": float(cool_w_m2),
        "diversity": float(diversity),
        "design_temp_C": float(design_temp_C),
        "design_summer_C": float(design_summer_C),
        "heating_factor": float(heat_factor),
        "cooling_factor": float(cool_factor),
        "vent_cat": str(vent_cat),
        "vent_m3h": float(q_m3h),
        "vent_heat_kw": float(max(0.0, vent_heat_kw)),
        "vent_cool_kw": float(max(0.0, vent_cool_kw)),
    }

def estimate_rain_flow_lps(roof_area_m2: float, r_l_s_ha: float, runoff_coeff: float = 0.9) -> float:
    # Q = r · C · A ; r in L/(s·ha), A in ha
    A_ha = max(0.0, float(roof_area_m2)) / 10000.0
    r = max(0.0, float(r_l_s_ha))
    C = max(0.1, min(1.0, float(runoff_coeff)))
    return r * C * A_ha

def estimate_fixtures_from_occupancy(use_type: str, persons: int) -> Dict[str, int]:
    # Very rough rule-of-thumb to seed plumbing pre-sizing.
    persons = max(0, int(persons))
    if persons == 0:
        return {"Washbasin": 0, "WC cistern": 0, "Urinal": 0, "Kitchen sink": 0, "Shower": 0}

    if use_type == "Office":
        return {
            "Washbasin": max(1, int(math.ceil(persons / 25))),
            "WC cistern": max(1, int(math.ceil(persons / 25))),
            "Urinal": max(0, int(math.ceil(persons / 50))),
            "Kitchen sink": max(1, int(math.ceil(persons / 100))),
            "Shower": max(0, int(math.ceil(persons / 200))),
        }
    if use_type == "Retail":
        return {
            "Washbasin": max(1, int(math.ceil(persons / 30))),
            "WC cistern": max(1, int(math.ceil(persons / 30))),
            "Urinal": max(0, int(math.ceil(persons / 60))),
            "Kitchen sink": max(1, int(math.ceil(persons / 150))),
            "Shower": 0,
        }
    if use_type == "Hotel":
        return {
            "Washbasin": max(1, int(math.ceil(persons / 10))),
            "WC cistern": max(1, int(math.ceil(persons / 10))),
            "Urinal": max(0, int(math.ceil(persons / 30))),
            "Kitchen sink": max(1, int(math.ceil(persons / 50))),
            "Shower": max(1, int(math.ceil(persons / 10))),
        }
    if use_type == "Residential":
        return {
            "Washbasin": max(1, int(math.ceil(persons / 3))),
            "WC cistern": max(1, int(math.ceil(persons / 3))),
            "Urinal": 0,
            "Kitchen sink": max(1, int(math.ceil(persons / 3))),
            "Shower": max(1, int(math.ceil(persons / 3))),
        }

    return {"Washbasin": 0, "WC cistern": 0, "Urinal": 0, "Kitchen sink": 0, "Shower": 0}
