
import streamlit as st
import pandas as pd
from src.ui_common import sidebar
from src.calcs_hvac import DEFAULT_LOADS_W_M2, VENT_CAT, hvac_predim, ventilation_flow, hvac_advisories
from src.utils import advisories_to_df
from src.sources import SOURCES
from src.project_presizing import load_use_profiles, load_city_presets, suggest_specific_loads_wm2

st.title("HVAC — pre-sizing")
ctx = sidebar()
with st.expander('Project defaults'):
    st.write("City:", ctx.get("city"))
    st.write("Use:", ctx.get("use_type"))
    st.write("Above-ground area (m²):", ctx.get("area_above_m2"))
    st.write("Occupancy:", ctx.get("persons"))
    st.write("Vent category:", ctx.get("vent_cat"))


st.subheader("1) Specific loads (W/m²) — German market + city climate (pre-sizing)")

use_profiles = load_use_profiles()
use_options = list(use_profiles.keys())
default_use = ctx.get("use_type", "Office")
use = st.selectbox("Main use", use_options, index=use_options.index(default_use) if default_use in use_options else 0)

area = st.number_input("Area (m²)", min_value=0.0, value=float(ctx.get("area_above_m2", 1000.0)), step=100.0)

city_presets = load_city_presets()
t_winter = float(city_presets.get(ctx.get("city","Custom"), {}).get("design_temp_C", -10.0))
t_summer = float(ctx.get("design_summer_C", city_presets.get(ctx.get("city","Custom"), {}).get("design_summer_C", 32.0)))

auto_specific = st.toggle(
    "Auto specific loads from German market + city climate (pre-sizing)",
    value=True,
    help="Auto-suggested W/m² vary with city design temperatures and GEG context. Switch off to override manually."
)

sugg = suggest_specific_loads_wm2(
    use_type=use,
    geg_context=str(ctx.get("geg","Existing building")),
    design_temp_C=float(t_winter),
    design_summer_C=float(t_summer),
)

c1, c2, c3 = st.columns(3)
with c1:
    if auto_specific:
        heat_wm2 = st.number_input(
            "Heating specific load (W/m²) — suggested (auto)",
            min_value=0.0,
            value=float(round(sugg["heat_adj_W_m2"], 1)),
            step=5.0,
            disabled=True,
        )
    else:
        heat_wm2 = st.number_input(
            "Heating specific load (W/m²) — manual",
            min_value=0.0,
            value=float(use_profiles.get(use, {}).get("heating_W_m2", 50.0)),
            step=5.0,
        )

with c2:
    if auto_specific:
        cool_wm2 = st.number_input(
            "Cooling specific load (W/m²) — suggested (auto)",
            min_value=0.0,
            value=float(round(sugg["cool_adj_W_m2"], 1)),
            step=5.0,
            disabled=True,
        )
    else:
        cool_wm2 = st.number_input(
            "Cooling specific load (W/m²) — manual",
            min_value=0.0,
            value=float(use_profiles.get(use, {}).get("cooling_W_m2", 70.0)),
            step=5.0,
        )

with c3:
    diversity = st.number_input("Diversity (0.3–1.0)", min_value=0.3, max_value=1.0, value=0.85, step=0.05)

with st.expander("How the auto specific loads are built (pre-sizing)"):
    st.write({
        "GEG context": ctx.get("geg"),
        "City": ctx.get("city"),
        "Winter design temp (°C)": t_winter,
        "Summer design temp (°C)": t_summer,
        "Heat base (W/m²)": sugg["heat_base_W_m2"],
        "Cooling base (W/m²)": sugg["cool_base_W_m2"],
        "Heat climate factor": sugg["heat_factor"],
        "Cooling climate factor": sugg["cool_factor"],
        "Heat suggested (W/m²)": sugg["heat_adj_W_m2"],
        "Cooling suggested (W/m²)": sugg["cool_adj_W_m2"],
    })
    st.caption("These are market-style pre-sizing benchmarks. Final loads must be calculated with DIN EN 12831 / VDI 2078.")

loads = hvac_predim(area, use, heat_wm2, cool_wm2, diversity)

cA, cB = st.columns(2)
cA.metric("Heating capacity (kW)", f"{loads['Q_heat_kW']:.1f}")
cB.metric("Cooling capacity (kW)", f"{loads['Q_cool_kW']:.1f}")

st.subheader("2) Ventilation (DIN EN 16798-1) — simple person + m² method")
persons = st.number_input("Occupancy (persons)", min_value=0, value=100, step=5)
category = st.selectbox("Indoor air quality category", list(VENT_CAT.keys()), index=1)
vent = ventilation_flow(area, persons, category)

v1, v2 = st.columns(2)
v1.metric("Outdoor air flow (L/s)", f"{vent['q_outdoor_lps']:.0f}")
v2.metric("Outdoor air flow (m³/h)", f"{vent['q_outdoor_m3h']:.0f}")

st.caption("Note: values are typical examples by category; adjust per use/method/materials and applicable standard text.")

st.subheader("3) Alerts and out-of-scope")
st.dataframe(advisories_to_df(hvac_advisories(use)), use_container_width=True)

with st.expander("Sources (HVAC)"):
    for sid in ["REHVA_EN16798_PDF","DIN_TR_16789_DRAFT","VDI_2078_PAGE","BWP_KLIMAKARTE","EU_GEG_OVERVIEW","DINMEDIA_GEG_TOPIC"]:
        s = SOURCES[sid]
        st.write(f"- **{sid}** ({s.kind}): {s.title} — {s.url} — accessed {s.accessed}")

st.warning("For final design: standards-based load calculations, equipment selection, acoustics, controls, heat recovery, etc.")


st.markdown("## Climate-aware ventilation (pre-sizing)")

# Use the same backend as the capacity estimate to avoid duplicated logic.
# This is a simplified pre-sizing sensitivity, not a DIN EN 12831 / VDI 2078 calculation.
try:
    import json
    from pathlib import Path
    _cp = json.load(open(Path(__file__).resolve().parent.parent / "data" / "city_presets.json", "r", encoding="utf-8"))
    t_winter = float(_cp.get(ctx.get("city","Custom"), {}).get("design_temp_C", -10.0))
except Exception:
    t_winter = -10.0

t_summer = float(ctx.get("design_summer_C", 32.0))

caps = estimate_hvac_capacities(
    float(ctx.get("area_above_m2", area)),
    {"heating_W_m2": heat_wm2, "cooling_W_m2": cool_wm2},
    diversity=float(div),
    design_temp_C=float(t_winter),
    persons=int(ctx.get("persons", 0)),
    vent_cat=str(ctx.get("vent_cat", "Cat II")),
    design_summer_C=float(t_summer),
)

st.write({
    "Indoor air category": str(ctx.get("vent_cat", "Cat II")),
    "Outdoor air flow (m³/h)": round(float(caps.get("vent_m3h", 0.0)), 0),
    "Vent heating add-on (kW)": round(float(caps.get("vent_heat_kw", 0.0)), 1),
    "Vent cooling add-on (kW)": round(float(caps.get("vent_cool_kw", 0.0)), 1),
    "Winter design temp (°C)": float(caps.get("design_temp_C", t_winter)),
    "Summer design temp (°C)": float(caps.get("design_summer_C", t_summer)),
})

st.markdown("## HVAC capacities including ventilation sensitivity (pre-sizing)")
# Winter design temperature uses city preset already present in app context.
try:
    import json
    from pathlib import Path
    _cp = json.load(open(Path(__file__).resolve().parent.parent / "data" / "city_presets.json", "r", encoding="utf-8"))
    t_winter = float(_cp.get(ctx.get("city","Custom"), {}).get("design_temp_C", -10.0))
except Exception:
    t_winter = -10.0

t_summer = float(ctx.get("design_summer_C", 32.0))
hv = estimate_hvac_capacities(
    float(ctx.get("area_above_m2", area)),
    {"heating_W_m2": heat_wm2, "cooling_W_m2": cool_wm2},
    diversity=float(div),
    design_temp_C=float(t_winter),
    persons=int(ctx.get("persons", 0)),
    vent_cat=str(ctx.get("vent_cat", "Cat II")),
    design_summer_C=float(t_summer),
)

st.write({
    "Heating capacity incl. ventilation (kW)": round(hv["heating_kw"], 1),
    "Cooling capacity incl. ventilation (kW)": round(hv["cooling_kw"], 1),
    "Ventilation flow (m³/h)": round(hv["vent_m3h"], 0),
    "Vent heating add-on (kW)": round(hv["vent_heat_kw"], 1),
    "Vent cooling add-on (kW)": round(hv["vent_cool_kw"], 1),
    "Summer design temp (°C)": hv["design_summer_C"],
    "Winter design temp (°C)": hv["design_temp_C"],
})

st.caption("Ventilation flow is driven mainly by IAQ category and occupancy (EN 16798 example). Climate affects the energy to condition the outdoor air; this section applies a simplified sensitivity using design temperatures.")
