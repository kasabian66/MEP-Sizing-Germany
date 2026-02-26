import streamlit as st

from src.ui_common import sidebar
from src.calcs_electrical import LoadItem, compute_demand, size_feeder, MOTOR_START_METHODS
from src.project_presizing import load_use_profiles, estimate_hvac_electrical_kw, estimate_lifts_kw

st.title("Electrical (LV) — pre-sizing")

ctx = sidebar()
use_profiles = load_use_profiles()
prof = use_profiles.get(ctx.get("use_type", "Office"), {})

st.markdown("## Inputs")

area = st.number_input(
    "Area used for electrical pre-sizing (m²)",
    min_value=0.0,
    value=float(ctx.get("area_above_m2", 1000.0)),
    step=100.0,
)

c1, c2, c3 = st.columns(3)
with c1:
    lighting_wm2 = st.number_input(
        "Lighting (W/m²) — indicative",
        min_value=0.0,
        value=float(prof.get("lighting_W_m2", 8.0)),
        step=1.0,
    )
with c2:
    sockets_wm2 = st.number_input(
        "Sockets / small power (W/m²) — indicative",
        min_value=0.0,
        value=float(prof.get("sockets_W_m2", 15.0)),
        step=1.0,
    )
with c3:
    other_wm2 = st.number_input(
        "Other (W/m²) — indicative",
        min_value=0.0,
        value=float(prof.get("other_W_m2", 5.0)),
        step=1.0,
    )

st.markdown("### Diversity")
div_lighting = st.slider("Lighting diversity", 0.2, 1.0, 0.9, 0.05)
div_sockets = st.slider("Sockets diversity", 0.2, 1.0, 0.8, 0.05)
div_other = st.slider("Other diversity", 0.2, 1.0, 0.8, 0.05)
div_hvac = st.slider("HVAC diversity", 0.2, 1.0, 0.9, 0.05)
div_lifts = st.slider("Lifts diversity", 0.2, 1.0, 0.6, 0.05)

st.markdown("### Optional known loads (auto-estimated by default)")
auto_est = st.toggle(
    "Auto-estimate HVAC and lifts from project definition",
    value=True,
    help="Uses simple rules of thumb based on the selected use profile and above-ground area. You can override the values.",
)

if auto_est:
    hvac_est_kw, hvac_meta = estimate_hvac_electrical_kw(float(ctx.get("area_above_m2", area)), prof, design_summer_C=float(ctx.get("design_summer_C", 32.0)))
    lifts_est_kw, lifts_meta = estimate_lifts_kw(float(ctx.get("area_above_m2", area)), prof)

    hvac_kw = st.number_input("HVAC (kW) — estimated (editable)", min_value=0.0, value=float(round(hvac_est_kw, 2)), step=5.0)
    lifts_kw = st.number_input("Lifts (kW) — estimated (editable)", min_value=0.0, value=float(round(lifts_est_kw, 2)), step=2.0)

    with st.expander("HVAC & lifts estimation assumptions"):
        st.write(f"Use profile: **{ctx.get('use_type','Office')}**")
        st.write(f"Above-ground area: **{float(ctx.get('area_above_m2', area)):,.0f} m²**")
        st.markdown("**HVAC electrical estimate**")
        st.write(hvac_meta)
        st.markdown("**Lifts estimate**")
        st.write(lifts_meta)
else:
    hvac_kw = st.number_input("HVAC (kW) — if known", min_value=0.0, value=0.0, step=5.0)
    lifts_kw = st.number_input("Lifts (kW) — if applicable", min_value=0.0, value=0.0, step=2.0)

st.markdown("## Feeder sizing (simplified)")

cA, cB, cC = st.columns(3)
with cA:
    v_ll = st.number_input("Voltage (V, L-L)", min_value=100.0, value=400.0, step=10.0)
with cB:
    length_m = st.number_input("Feeder length (m)", min_value=1.0, value=50.0, step=5.0)
with cC:
    max_vdrop = st.number_input("Max voltage drop (%)", min_value=1.0, value=3.0, step=0.5)

st.markdown("### Motor (optional)")
add_motor = st.checkbox("Include a motor starting check (informative)", value=False)
motor_kw = 0.0
motor_method = "Direct on line (DOL)"
if add_motor:
    cM1, cM2 = st.columns(2)
    with cM1:
        motor_kw = st.number_input("Motor power (kW)", min_value=0.0, value=15.0, step=1.0)
    with cM2:
        motor_method = st.selectbox("Start method", list(MOTOR_START_METHODS.keys()), index=0)

# Build load list
lighting_kw = area * lighting_wm2 / 1000.0
sockets_kw = area * sockets_wm2 / 1000.0
other_kw = area * other_wm2 / 1000.0

loads = [
    LoadItem("Lighting", lighting_kw, div_lighting),
    LoadItem("Sockets / small power", sockets_kw, div_sockets),
    LoadItem("HVAC", float(hvac_kw), div_hvac),
    LoadItem("Lifts", float(lifts_kw), div_lifts),
    LoadItem("Other", other_kw, div_other),
]

p_dem_kw, df = compute_demand(loads)

res = size_feeder(
    p_dem_kw=p_dem_kw,
    v_ll=float(v_ll),
    length_m=float(length_m),
    max_vdrop_pct=float(max_vdrop),
    add_motor=bool(add_motor),
    motor_kw=float(motor_kw),
    motor_start_method=str(motor_method),
)

st.markdown("## Results")

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Demand power (kW)", f"{res['P_dem_kW']:.1f}")
with k2:
    st.metric("Design current (A)", f"{res['I_design_A']:.0f}")
with k3:
    st.metric("Suggested section (mm²)", f"{res['Section_mm2']:.0f}")
with k4:
    st.metric("Voltage drop (%)", f"{res['Vdrop_pct']:.2f}")

st.dataframe(df, use_container_width=True)

st.markdown("### Approx. short-circuit (very rough)")
st.write(f"Estimated end short-circuit current: **{res['Ik_end_A_approx']:.0f} A** (indicative only)")

if res.get("motor"):
    st.markdown("### Motor starting (informative)")
    st.write(res["motor"])

for a in res.get("advisories", []):
    if a.level == "danger":
        st.error(a.text)
    elif a.level == "warning":
        st.warning(a.text)
    else:
        st.info(a.text)

st.info(
    "Pre-sizing only. Final design must verify short-circuit withstand, selectivity, installation conditions, "
    "correction factors and applicable VDE/DIN requirements."
)
