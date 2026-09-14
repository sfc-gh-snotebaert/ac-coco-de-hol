import streamlit as st

st.title("Workshop agenda")

AGENDA = [
    ("9:00 AM", "Welcome & Workshop Overview", None, None),
    ("9:05 AM", "Session 1: Review Current Configuration", "10 min", "1"),
    ("9:15 AM", "Session 2: Create Openflow Postgres Connector", "30 min", "2"),
    ("9:45 AM", "Session 3: Create dbt Project from STTM Files", "40 min", "3"),
    ("10:25 AM", "Session 4: Code Review & Optimization", "20 min", "4"),
    ("10:45 AM", "Session 5: Data Engineer Skill (Stretch)", "10 min", "5"),
]

for time, title, duration, session_num in AGENDA:
    if session_num:
        col1, col2 = st.columns([1, 4])
        col1.markdown(f"**{time}**")
        col2.markdown(f":material/play_circle: **{title}** :gray-badge[{duration}]")
    else:
        col1, col2 = st.columns([1, 4])
        col1.markdown(f"**{time}**")
        col2.markdown(f":gray[{title}]")

st.space("medium")

st.markdown("##### What you'll build by end of session")
st.markdown("""
| Object Type | Count | Examples |
|-------------|-------|---------|
| **Databases** | 2 | `AIRLINE_OPS` (CDC landing zone), `EDW` (warehouse layer) |
| **Openflow Connector** | 1 | `PG_CDC_CONNECTOR` — live Postgres CDC into AIRLINE_OPS |
| **Iceberg Tables** | 3 | `EDW.GOLD.DIM_FLIGHT`, `DIM_PASSENGER` (SCD2), `FACT_BOOKING` |
| **dbt Models** | 4 | Mart models (Iceberg in EDW.GOLD) |
| **dbt Tests** | ~12 | not_null, unique, relationships, accepted_values, custom SCD integrity |
| **Recommendations Report** | 1 | Clustering keys, anti-pattern fixes, performance improvements |
""")

st.space("small")

st.markdown("##### Location")
with st.container(border=True):
    st.markdown("""
:material/location_on: **Air Canada Centre, Montreal, QC**

September 16, 2026 — 9:00 AM to 11:00 AM
""")
