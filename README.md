# MEP Pre-sizing — Germany (Streamlit)

Streamlit dashboard for **early-stage MEP pre-sizing** in Germany (e.g., Berlin and Düsseldorf), ready to push to GitHub and deploy on Streamlit Community Cloud.

> ⚠️ Key limitation: this does **not** replace detailed engineering design. Many DIN/VDE/VDI standards are paywalled; this repository uses publicly accessible sources and provides traceability via `data/sources_matrix.csv`.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deployment (Streamlit Cloud)

- Push the repo to GitHub
- Create a new Streamlit app pointing to `app.py`
- Ensure `requirements.txt` is in the repository root

## Structure

- `app.py` — home / executive KPIs
- `pages/` — modules (Electrical, HVAC, Plumbing/DHW, Drainage/Rainwater, Fire Safety, Export)
- `src/` — calculations and utilities
- `data/` — profiles/presets and Sources Matrix

## Pre-sizing philosophy

- Provide indicative values and editable assumptions
- Make out-of-scope boundaries explicit
- Always validate against the applicable standards and local authority requirements
