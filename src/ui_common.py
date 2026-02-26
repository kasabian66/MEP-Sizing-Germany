import json
from pathlib import Path
import streamlit as st

BUNDESLANDS = [
    "Generic (Germany)",
    "Berlin",
    "North Rhine-Westphalia (Düsseldorf)",
    "Baden-Württemberg",
    "Bayern",
    "Brandenburg",
    "Bremen",
    "Hamburg",
    "Hessen",
    "Mecklenburg-Vorpommern",
    "Niedersachsen",
    "Rheinland-Pfalz",
    "Saarland",
    "Sachsen",
    "Sachsen-Anhalt",
    "Schleswig-Holstein",
    "Thüringen",
]

DATA_PATH = Path(__file__).resolve().parent.parent / "data"


def _load_json(name: str):
    return json.load(open(DATA_PATH / name, "r", encoding="utf-8"))


def sidebar():
    """Project definition sidebar (pre-sizing).

    Auto-estimates update live with area / use / storeys and can be switched to manual overrides.
    """
    st.sidebar.header("Project definition")

    city_presets = _load_json("city_presets.json")
    use_profiles = _load_json("use_profiles.json")

    city = st.sidebar.selectbox("City (Germany)", list(city_presets.keys()), index=0)
    bundesland = st.sidebar.selectbox("Federal state (Bundesland)", BUNDESLANDS, index=0)
    use_type = st.sidebar.selectbox("Main use", list(use_profiles.keys()), index=0)

    area_above = st.sidebar.number_input(
        "Above-ground area (m²)",
        min_value=0.0,
        value=float(st.session_state.get("area_above_m2", 10000.0)),
        step=100.0,
    )
    area_below = st.sidebar.number_input(
        "Below-ground area (m²)",
        min_value=0.0,
        value=float(st.session_state.get("area_below_m2", 0.0)),
        step=100.0,
    )

    floors_above = st.sidebar.number_input(
        "Above-ground storeys",
        min_value=0,
        value=int(st.session_state.get("floors_above", 8)),
        step=1,
    )
    floors_below = st.sidebar.number_input(
        "Below-ground storeys",
        min_value=0,
        value=int(st.session_state.get("floors_below", 0)),
        step=1,
    )

    prof = use_profiles.get(use_type, {})

    st.sidebar.subheader("Auto-estimates (editable)")

    # Occupancy
    m2_per_person = float(prof.get("occupancy_m2_per_person", 10)) or 10.0
    occ_est = 0 if area_above <= 0 else int(max(0, round(area_above / m2_per_person)))
    auto_occupancy = st.sidebar.toggle(
        "Auto occupancy from area + use profile",
        value=bool(st.session_state.get("auto_occupancy", True)),
        help="If enabled, occupancy updates automatically when area or use changes.",
    )
    if auto_occupancy:
        st.sidebar.number_input(
            "Occupancy (persons) — auto",
            min_value=0,
            value=int(occ_est),
            step=5,
            disabled=True,
        )
        persons = int(occ_est)
    else:
        persons = st.sidebar.number_input(
            "Occupancy (persons) — manual",
            min_value=0,
            value=int(st.session_state.get("persons", occ_est)),
            step=5,
        )

    with st.sidebar.expander("Occupancy assumptions"):
        st.write(f"Use profile density: {m2_per_person} m²/person")
        st.write(f"Computed persons: {occ_est}")

    # Roof area
    roof_est = 0.0 if area_above <= 0 else float(area_above) / max(1, int(floors_above or 1))
    auto_roof = st.sidebar.toggle(
        "Auto roof area from footprint (area/storeys)",
        value=bool(st.session_state.get("auto_roof_area", True)),
        help="If enabled, roof area updates automatically when area or storeys change.",
    )
    if auto_roof:
        st.sidebar.number_input(
            "Roof area (m²) — auto footprint",
            min_value=0.0,
            value=float(roof_est),
            step=50.0,
            disabled=True,
        )
        roof_area = float(roof_est)
    else:
        roof_area = st.sidebar.number_input(
            "Roof area (m²) — manual",
            min_value=0.0,
            value=float(st.session_state.get("roof_area_m2", roof_est)),
            step=50.0,
        )

    # Technical rooms & shafts
    from .project_presizing import estimate_tech_rooms_and_shafts

    area_total = float(area_above) + float(area_below)
    allowances = estimate_tech_rooms_and_shafts(area_total, int(floors_above or 1), prof)

    auto_spaces = st.sidebar.toggle(
        "Auto technical rooms & shafts from area ratios",
        value=bool(st.session_state.get("auto_spaces", True)),
        help="If enabled, these areas update automatically when areas, use or storeys change.",
    )
    if auto_spaces:
        st.sidebar.number_input(
            "Technical rooms (m²) — auto",
            min_value=0.0,
            value=float(allowances["tech_rooms_m2"]),
            step=10.0,
            disabled=True,
        )
        st.sidebar.number_input(
            "Shafts total (m²) — auto",
            min_value=0.0,
            value=float(allowances["shafts_m2"]),
            step=10.0,
            disabled=True,
        )
        tech_rooms_m2 = float(allowances["tech_rooms_m2"])
        shafts_m2 = float(allowances["shafts_m2"])
        st.sidebar.caption(f"Net shafts per storey: {allowances['shafts_m2_per_floor']:.2f} m²/storey")
    else:
        tech_rooms_m2 = st.sidebar.number_input(
            "Technical rooms (m²) — manual",
            min_value=0.0,
            value=float(st.session_state.get("tech_rooms_m2", allowances["tech_rooms_m2"])),
            step=10.0,
        )
        shafts_m2 = st.sidebar.number_input(
            "Shafts total (m²) — manual",
            min_value=0.0,
            value=float(st.session_state.get("shafts_m2", allowances["shafts_m2"])),
            step=10.0,
        )
        st.sidebar.caption(f"Net shafts per storey: {shafts_m2 / max(1, int(floors_above or 1)):.2f} m²/storey")

    st.sidebar.subheader("Design context (pre-sizing)")
    vent_cat = st.sidebar.selectbox("Indoor air category (EN 16798 example)", ["Cat I", "Cat II", "Cat III"], index=1)
    geg = st.sidebar.selectbox(
        "GEG context",
        ["Existing building", "New build (GEG baseline)", "High performance (indicative)"],
        index=0,
    )

    # Summer design temperature (context for pre-sizing)
    summer_preset = float(city_presets.get(city, {}).get("design_summer_C", 32.0))
    design_summer_C = st.sidebar.number_input(
        "Summer design outdoor temperature (°C) — preset (editable)",
        min_value=20.0,
        max_value=45.0,
        value=float(st.session_state.get("design_summer_C", summer_preset)),
        step=0.5,
    )

    st.sidebar.caption(
        "Note: requirements can vary by state building codes (Landesbauordnung). This app uses a generic mode and adds alerts."
    )

    st.session_state.update(
        {
            "city": city,
            "bundesland": bundesland,
            "use_type": use_type,
            "area_above_m2": float(area_above),
            "area_below_m2": float(area_below),
            "floors_above": int(floors_above),
            "floors_below": int(floors_below),
            "auto_occupancy": bool(auto_occupancy),
            "auto_roof_area": bool(auto_roof),
            "auto_spaces": bool(auto_spaces),
            "persons": int(persons),
            "vent_cat": vent_cat,
            "geg": geg,
            "roof_area_m2": float(roof_area),
            "tech_rooms_m2": float(tech_rooms_m2),
            "shafts_m2": float(shafts_m2),
            "design_summer_C": float(design_summer_C),
        }
    )

    return dict(st.session_state)
