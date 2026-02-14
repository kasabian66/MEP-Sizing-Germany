
from __future__ import annotations
from typing import Dict, List
from .utils import Advisory

def fire_predim(building_use: str, gross_area_m2: float, stories: int, underground: bool) -> Dict[str, object]:
    adv=[]
    # Not a real code checker. Provide a "decision helper" for when a specialist plan is required.
    needs_specialist = True
    reasons = []
    if gross_area_m2 > 5000:
        reasons.append("Area > 5.000 m² (umbral indicative interno)")
    if stories >= 6:
        reasons.append("High-rise building (>=6 storeys, indicative)")
    if underground:
        reasons.append("Espacios below ground presentes")
    if not reasons:
        reasons.append("Requirements depend on the Landesbauordnung, building use, and the fire safety concept.")

    adv.append(Advisory("danger",
        "Fire protection (Brandschutz) almost always requires a specific concept and design. This module is only indicative."))

    adv.append(Advisory("info",
        "For systems: DIN 14675 (fire detection & alarm systems) and DIN EN 12845 / VdS CEA 4001 (sprinklers) may be relevant depending on the case."))

    return {
        "needs_specialist": needs_specialist,
        "reasons": reasons,
        "advisories": adv,
    }
