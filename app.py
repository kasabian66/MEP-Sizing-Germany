
import streamlit as st

from src.ui_common import sidebar
from src.project_presizing import (
    load_use_profiles, load_city_presets,
    estimate_electrical_loads, estimate_hvac_capacities, estimate_hvac_electrical_kw, estimate_lifts_kw,
    estimate_tech_rooms_and_shafts, estimate_rain_flow_lps,
)

st.set_page_config(page_title="MEP Pre-sizing — Germany", layout="wide")

st.title("MEP Pre-sizing — Germany")
st.markdown(
    "This dashboard is intended for **early-stage** estimates and preliminary sizing. "
    "It includes clear alerts when detailed engineering and code verification are required."
)

ctx = sidebar()

use_profiles = load_use_profiles()
city_presets = load_city_presets()
prof = use_profiles.get(ctx["use_type"], {})
cityp = city_presets.get(ctx["city"], city_presets.get("Custom", {}))

st.markdown("## Executive summary")
c1, c2, c3, c4 = st.columns(4)
c1.metric("City", ctx["city"])
c2.metric("Use", ctx["use_type"])
c3.metric("Above-ground area (m²)", f"{ctx['area_above_m2']:,.0f}")
c4.metric("Occupancy (persons)", f"{ctx['persons']:,.0f}")

st.markdown("## Space allowances (indicative)")
area_total = ctx["area_above_m2"] + ctx["area_below_m2"]
allow = estimate_tech_rooms_and_shafts(area_total, ctx["floors_above"], prof)
a1, a2, a3, a4 = st.columns(4)
a1.metric("Technical rooms (m²)", f"{ctx['tech_rooms_m2']:,.1f}")
a2.metric("Shafts total (m²)", f"{ctx['shafts_m2']:,.1f}")
a3.metric("Shafts per storey (m²)", f"{(ctx['shafts_m2']/max(1,ctx['floors_above'])):,.2f}")
a4.metric("Storeys above", f"{ctx['floors_above']}")

st.markdown("## Quick MEP indicators (pre-sizing)")
elec = estimate_electrical_loads(ctx["area_above_m2"], prof)
hvac_elec_kw, _ = estimate_hvac_electrical_kw(ctx["area_above_m2"], prof)
lifts_kw, _ = estimate_lifts_kw(ctx["area_above_m2"], prof)
hvac_cap = estimate_hvac_capacities(ctx["area_above_m2"], prof, design_temp_C=city_presets.get(ctx['city'], {}).get('design_temp_C', -10.0), persons=int(ctx.get('persons',0)), vent_cat=str(ctx.get('vent_cat','Cat II')), design_summer_C=float(ctx.get('design_summer_C',32.0)))
rain_q = estimate_rain_flow_lps(ctx["roof_area_m2"], float(cityp.get("rain_r_l_s_ha", 300)))

q1, q2, q3, q4 = st.columns(4)
q1.metric("Electrical connected (kW)", f"{sum(elec.values()):,.0f}")
q2.metric("HVAC electric (kW)", f"{hvac_elec_kw:,.0f}")
q3.metric("Heating (kW)", f"{hvac_cap['heating_kw']:,.0f}")
q4.metric("Rainwater Q (L/s)", f"{rain_q:,.2f}")

st.caption("All results are indicative and intended for early-stage pre-sizing. Always verify against applicable standards and local requirements.")
