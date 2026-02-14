
import streamlit as st
from src.ui_common import sidebar
from src.calcs_drainage import rain_flow_lps, suggest_rain_pipe_d_mm, drainage_advisories
from src.utils import advisories_to_df
from src.sources import SOURCES

st.title("Drainage / Rainwater — pre-sizing")
ctx = sidebar()
with st.expander('Project defaults'):
    st.write("City:", ctx.get("city"))
    st.write("Roof area (m²):", ctx.get("roof_area_m2"))


tab1, tab2 = st.tabs(["Rainwater", "Wastewater (basic)"])

with tab1:
    st.subheader("1) Rainwater flow")
    area = st.number_input("Effective roof area (m²)", min_value=0.0, value=800.0, step=10.0)
    r = st.number_input("Rain intensity r (L/s·m²)", min_value=0.001, value=0.03, step=0.005,
                        help="Local value per adopted method (e.g., KOSTRA/DWD). Here used as input.")
    q = rain_flow_lps(area, r)
    st.metric("Rainwater flow (L/s)", f"{q:.1f}")

    st.subheader("2) Indicative diameter")
    v = st.number_input("Velocity (m/s) (indicative)", min_value=0.5, max_value=5.0, value=2.0, step=0.1)
    d = suggest_rain_pipe_d_mm(q, v)
    st.metric("Equivalent internal diameter (mm)", f"{d:.0f}")
    st.caption("Select a commercial DN and verify against the applicable standard (EN 12056 / DIN 1986-100) and the chosen solution (siphonic / gravity).")

with tab2:
    st.subheader("Basic")
    st.info("For internal wastewater, a detailed fixture-based method is required (EN 12056-2). This tab is limited to alerts and scope.")
    st.dataframe(advisories_to_df(drainage_advisories()), use_container_width=True)

with st.expander("Sources (drainage)"):
    for sid in ["DIN1986_100_OVERVIEW_AENOR","EN12056_INTERTEK"]:
        s=SOURCES[sid]
        st.write(f"- **{sid}** ({s.kind}): {s.title} — {s.url} — accessed {s.accessed}")
