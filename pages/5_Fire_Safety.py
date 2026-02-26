
import streamlit as st
from src.ui_common import sidebar
from src.calcs_fire import fire_predim
from src.utils import advisories_to_df
from src.sources import SOURCES

st.title("Fire protection / Brandschutz — pre-sizing (very limited)")
ctx = sidebar()

st.warning("This module does NOT replace a fire safety concept nor a specific design project. It only helps you decide when to escalate to a specialist.")

use = st.selectbox("Main use", ["Office", "Retail", "Residential", "Industrial/light"], index=0)
area = st.number_input("Approx. gross area (m²)", min_value=0.0, value=6000.0, step=100.0)
stories = st.number_input("No. of above-ground storeys", min_value=1, value=8, step=1)
und = st.checkbox("Basement/underground areas?", value=True)

res = fire_predim(use, area, int(stories), und)

st.subheader("Result")
st.write("**Requires specialist:**", "Yes" if res["needs_specialist"] else "Most likely yes")
st.write("**Reasons:**")
for r in res["reasons"]:
    st.write(f"- {r}")

st.subheader("Alerts")
st.dataframe(advisories_to_df(res["advisories"]), use_container_width=True)

with st.expander("Sources (fire)"):
    for sid in ["VDS_DIN14675","VDS_SPRINKLER_GUIDELINE","VDS_CEA4001_PDF"]:
        s=SOURCES[sid]
        st.write(f"- **{sid}** ({s.kind}): {s.title} — {s.url} — accessed {s.accessed}")
