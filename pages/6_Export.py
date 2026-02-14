
import streamlit as st
import pandas as pd
import tempfile, os

from src.ui_common import sidebar
from src.reporting import build_pdf
from src.sources import SOURCES

st.title("Export (PDF / CSV)")
ctx = sidebar()

st.info("This module exports a simple PDF with an executive summary and a table you paste here. For complete results, export CSV from each module and attach them to your calculation note.")


st.subheader("1) Paste a table (CSV) to export")
csv_text = st.text_area("CSV (with header)", height=200, value="Col1,Col2\n1,2\n3,4")
title = st.text_input("Table title", value="Table exportada")
try:
    df = pd.read_csv(pd.compat.StringIO(csv_text))
except Exception:
    try:
        import io
        df = pd.read_csv(io.StringIO(csv_text))
    except Exception as e:
        df = pd.DataFrame()

st.dataframe(df, use_container_width=True)

st.subheader("2) Export")
source_ids = st.multiselect("Sources to include", list(SOURCES.keys()), default=list(SOURCES.keys())[:5])
exec_summary = {
    "Bundesland": ctx["bundesland"],
    "Note": "Pre-sizing (not a design project). See README for scope and limitations.",
}

if st.button("Generate PDF"):
    with tempfile.TemporaryDirectory() as td:
        pdf_path = os.path.join(td, "predim_report.pdf")
        build_pdf(
            filename=pdf_path,
            executive=exec_summary,
            tables=[{"title": title, "df": df}],
            source_ids=source_ids,
        )
        with open(pdf_path, "rb") as f:
            st.download_button("Download PDF", f, file_name="predim_report.pdf", mime="application/pdf")

st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), file_name="table.csv", mime="text/csv")
