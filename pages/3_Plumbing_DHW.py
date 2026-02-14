
import streamlit as st
import pandas as pd
from src.ui_common import sidebar
from src.calcs_plumbing import FIXTURE_DEFAULTS, peak_flow_lps, suggest_pipe_diameter_mm, acs_energy_kwh_per_day, plumbing_advisories
from src.utils import advisories_to_df
from src.sources import SOURCES

st.title("Plumbing / DHW — pre-sizing")
ctx = sidebar()

st.caption('Tip: you can seed fixtures from the project occupancy (rule-of-thumb).')
if st.button('Apply suggested fixtures from occupancy'):
    suggested = estimate_fixtures_from_occupancy(ctx.get('use_type','Office'), int(ctx.get('persons',0)))
    for k,v in suggested.items():
        st.session_state[f'fix_{k}'] = int(v)


st.subheader("1) Fixtures and peak flow (simplified method)")
st.caption("Enter the number of fixtures. Per-fixture flow values are indicative. For final design: DIN 1988-300 / EN 806-3.")

cols = st.columns(3)
fixtures = {}
keys=list(FIXTURE_DEFAULTS.keys())
for i,k in enumerate(keys):
    with cols[i%3]:
        fixtures[k] = st.number_input(k, min_value=0, value=10 if k=="WC cistern" else 5, step=1)

sim = st.number_input("Global simultaneity factor (0.1–1.0)", min_value=0.1, max_value=1.0, value=0.35, step=0.05)
flows = peak_flow_lps(fixtures, sim)

c1, c2 = st.columns(2)
c1.metric("Σ nominal flows (L/s)", f"{flows['q_sum_lps']:.2f}")
c2.metric("Estimated peak flow (L/s)", f"{flows['q_peak_lps']:.2f}")

st.subheader("2) Indicative diameter by max velocity")
vmax = st.number_input("Max velocity (m/s)", min_value=0.5, max_value=3.0, value=2.0, step=0.1)
dmm = suggest_pipe_diameter_mm(flows["q_peak_lps"], vmax)
st.metric("Equivalent internal diameter (mm)", f"{dmm:.0f}")
st.caption("Selecting a commercial DN requires choosing the material, wall thickness (SDR), and accounting for local losses.")

st.subheader("3) DHW (optional)")
acs_on = st.checkbox("Compute daily DHW energy", value=False)
if acs_on:
    persons = st.number_input("Persons", min_value=0, value=100, step=5)
    lpp = st.number_input("Liters per person·day", min_value=0.0, value=12.0, step=1.0)
    deltaT = st.number_input("ΔT (K)", min_value=10.0, value=35.0, step=1.0)
    eff = st.number_input("System efficiency", min_value=0.5, max_value=1.0, value=0.9, step=0.01)
    e = acs_energy_kwh_per_day(persons, lpp, deltaT, eff)
    st.metric("DHW energy (kWh/day)", f"{e:.0f}")

st.subheader("4) Alerts and sources")
st.dataframe(advisories_to_df(plumbing_advisories()), use_container_width=True)

with st.expander("Sources (water)"):
    for sid in ["DIN1988_300_PDF","ZVSHK_T110_PDF","EN806_3_CATALOG"]:
        s=SOURCES[sid]
        st.write(f"- **{sid}** ({s.kind}): {s.title} — {s.url} — accessed {s.accessed}")
