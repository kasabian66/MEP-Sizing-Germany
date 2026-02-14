
import streamlit as st
import pandas as pd
from src.ui_common import sidebar
from src.calcs_hvac import DEFAULT_LOADS_W_M2, VENT_CAT, hvac_predim, ventilation_flow, hvac_advisories
from src.utils import advisories_to_df
from src.sources import SOURCES

st.title("HVAC — pre-sizing")
ctx = sidebar()
with st.expander('Project defaults'):
    st.write("City:", ctx.get("city"))
    st.write("Use:", ctx.get("use_type"))
    st.write("Above-ground area (m²):", ctx.get("area_above_m2"))
    st.write("Occupancy:", ctx.get("persons"))
    st.write("Vent category:", ctx.get("vent_cat"))


st.subheader("1) Indicative loads (W/m²) — adjustable")
use = st.selectbox("Main use", list(DEFAULT_LOADS_W_M2.keys()), index=0)
area = st.number_input("Area (m²)", min_value=0.0, value=float(ctx.get("area_above_m2", 1000.0)), step=100.0)

c1, c2, c3 = st.columns(3)
with c1:
    heat_wm2 = st.number_input("Heating load (W/m²)", min_value=0.0, value=float(DEFAULT_LOADS_W_M2[use]["heat"]), step=5.0)
with c2:
    cool_wm2 = st.number_input("Cooling load (W/m²)", min_value=0.0, value=float(DEFAULT_LOADS_W_M2[use]["cool"]), step=5.0)
with c3:
    diversity = st.number_input("Diversity (0.3–1.0)", min_value=0.3, max_value=1.0, value=0.85, step=0.05)

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
vent = estimate_ventilation_flow_m3h(float(ctx.get("area_above_m2", area)), int(ctx.get("persons", 0)), str(ctx.get("vent_cat", "Cat II")))
st.write({
    "Indoor air category": vent["vent_cat"],
    "qp (L/s·person)": vent["qp_Ls_per_person"],
    "qB (L/s·m²)": vent["qB_Ls_per_m2"],
    "Outdoor air flow (L/s)": round(vent["q_Ls"], 1),
    "Outdoor air flow (m³/h)": round(vent["q_m3h"], 0),
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
