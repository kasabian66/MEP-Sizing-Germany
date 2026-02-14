
import streamlit as st
import pandas as pd

from src.ui_common import sidebar
from src.project_presizing import (
    load_use_profiles, load_city_presets,
    estimate_electrical_loads, estimate_hvac_capacities, estimate_hvac_electrical_kw, estimate_lifts_kw,
    estimate_rain_flow_lps, estimate_tech_rooms_and_shafts, estimate_fixtures_from_occupancy,
)

st.title("Project summary — auto pre-sizing")

ctx = sidebar()
use_profiles = load_use_profiles()
city_presets = load_city_presets()
prof = use_profiles.get(ctx["use_type"], {})
cityp = city_presets.get(ctx["city"], city_presets.get("Custom", {}))

st.markdown("## Inputs")
st.write({
    "City": ctx["city"],
    "Bundesland": ctx["bundesland"],
    "Use": ctx["use_type"],
    "Above-ground area (m²)": ctx["area_above_m2"],
    "Below-ground area (m²)": ctx["area_below_m2"],
    "Storeys above": ctx["floors_above"],
    "Storeys below": ctx["floors_below"],
    "Occupancy (persons)": ctx["persons"],
    "Vent category (EN 16798 example)": ctx["vent_cat"],
    "GEG context": ctx["geg"],
    "Roof area (m²)": ctx["roof_area_m2"],
})

st.markdown("## Space allowances")
area_total = ctx["area_above_m2"] + ctx["area_below_m2"]
allow = estimate_tech_rooms_and_shafts(area_total, ctx["floors_above"], prof)
df_space = pd.DataFrame([
    {"Item": "Technical rooms (m²)", "Estimated": allow["tech_rooms_m2"], "Used (editable)": ctx["tech_rooms_m2"]},
    {"Item": "Shafts total (m²)", "Estimated": allow["shafts_m2"], "Used (editable)": ctx["shafts_m2"]},
    {"Item": "Shafts per storey (m²)", "Estimated": allow["shafts_m2_per_floor"], "Used (editable)": ctx["shafts_m2"] / max(1, ctx["floors_above"])},
])
st.dataframe(df_space, use_container_width=True)

st.markdown("## Electrical (LV) — estimated connected loads")
elec = estimate_electrical_loads(ctx["area_above_m2"], prof)
hvac_kw, hvac_meta = estimate_hvac_electrical_kw(ctx["area_above_m2"], prof, design_summer_C=float(ctx.get("design_summer_C", 32.0)))
lifts_kw, lifts_meta = estimate_lifts_kw(ctx["area_above_m2"], prof)

df_elec = pd.DataFrame([
    {"Component": "Lighting", "kW": elec["lighting_kw"]},
    {"Component": "Sockets/small power", "kW": elec["sockets_kw"]},
    {"Component": "HVAC (electric)", "kW": elec["hvac_kw"]},
    {"Component": "Lifts", "kW": elec["lifts_kw"]},
    {"Component": "Other", "kW": elec["other_kw"]},
])
df_elec.loc[len(df_elec)] = {"Component": "TOTAL connected (kW)", "kW": float(df_elec["kW"].sum())}
st.dataframe(df_elec, use_container_width=True)

with st.expander("Electrical estimation assumptions"):
    st.write(f"Use profile: {ctx['use_type']}")
    st.markdown("**HVAC electrical estimate**")
    st.write(hvac_meta)
    st.markdown("**Lifts estimate**")
    st.write(lifts_meta)

st.markdown("## HVAC — capacities (very simplified)")
hv = estimate_hvac_capacities(ctx["area_above_m2"], prof, diversity=0.8, design_temp_C=float(cityp.get('design_temp_C', -10.0)))
df_hvac = pd.DataFrame([
    {"Item": "Heating capacity (kW)", "Value": hv["heating_kw"]},
    {"Item": "Cooling capacity (kW)", "Value": hv["cooling_kw"]},
    {"Item": "Heating specific load (W/m²)", "Value": hv["heat_W_m2"]},
    {"Item": "Cooling specific load (W/m²)", "Value": hv["cool_W_m2"]},
    {"Item": "Design outdoor temperature (°C) — preset", "Value": cityp.get("design_temp_C", "")},
])
st.dataframe(df_hvac, use_container_width=True)

st.markdown("## Plumbing / DHW — starter fixtures (rule-of-thumb)")
fixtures = estimate_fixtures_from_occupancy(ctx["use_type"], ctx["persons"])
df_fix = pd.DataFrame([{"Fixture": k, "Count (estimated)": v} for k, v in fixtures.items()])
st.dataframe(df_fix, use_container_width=True)
st.caption("These fixtures are only to seed pre-sizing. Verify against the design brief and applicable requirements.")

st.markdown("## Rainwater — pre-sizing")
c1, c2, c3 = st.columns(3)
with c1:
    r_l_s_ha = st.number_input("Rain intensity r (L/s·ha) — preset (editable)", min_value=0.0, value=float(cityp.get("rain_r_l_s_ha", 300.0)), step=10.0)
with c2:
    runoff = st.number_input("Runoff coefficient C", min_value=0.1, max_value=1.0, value=0.9, step=0.05)
with c3:
    roof_area = st.number_input("Roof area (m²)", min_value=0.0, value=float(ctx["roof_area_m2"]), step=50.0)

q_lps = estimate_rain_flow_lps(roof_area, r_l_s_ha, runoff)
st.metric("Estimated roof rainwater flow (L/s)", f"{q_lps:,.2f}")
st.caption("Q = r · C · A, where r is in L/(s·ha) and A is roof area in hectares. Use local dataset values for r (e.g., KOSTRA-DWD).")

st.markdown("## Notes")
st.info("All results are indicative and intended for early-stage pre-sizing. Always verify against the applicable standards and local requirements.")
