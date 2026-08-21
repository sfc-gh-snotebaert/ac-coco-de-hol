import streamlit as st

st.title("Workshop agenda")

AGENDA = [
    ("{{TIME_ARRIVAL}}", "Arrival & Coffee", None, None),
    ("{{TIME_WELCOME}}", "Welcome & Workshop Overview", None, None),
    ("{{TIME_SESSION_1}}", "Session 1: Environment Setup", "{{DUR_SESSION_1}}", "1"),
    ("{{TIME_SESSION_2}}", "Session 2: Enterprise Ingestion with Openflow", "{{DUR_SESSION_2}}", "2"),
    ("{{TIME_BREAK}}", ":orange-badge[BREAK]", None, None),
    ("{{TIME_SESSION_3}}", "Session 3: EDW Pipeline from STTM with dbt", "{{DUR_SESSION_3}}", "3"),
    ("{{TIME_SESSION_4}}", "Session 4: Code Review & Optimization", "{{DUR_SESSION_4}}", "4"),
    ("{{TIME_SESSION_5}}", "Session 5: Data Engineer Skill (Stretch)", "{{DUR_SESSION_5}}", "5"),
]

for time, title, duration, session_num in AGENDA:
    if session_num:
        col1, col2 = st.columns([1, 4])
        col1.markdown(f"**{time}**")
        col2.markdown(f":material/play_circle: **{title}** :gray-badge[{duration}]")
    elif "BREAK" in title:
        col1, col2 = st.columns([1, 4])
        col1.markdown(f"**{time}**")
        col2.markdown(f"{title}")
    else:
        col1, col2 = st.columns([1, 4])
        col1.markdown(f"**{time}**")
        col2.markdown(f":gray[{title}]")

st.space("medium")

st.markdown("##### What you'll build by end of session")
st.markdown("""
| Object Type | Count | Examples |
|-------------|-------|---------|
| **Databases** | 2 | `RAW_AC` (ingestion layer), `EDW_AC` (warehouse layer) |
| **Iceberg Tables** | {{NUM_SOURCE_TABLES}} | Bookings, Passengers, Flights, Airports, Work Orders, Aeroplan Txns |
| **Batch Control** | 1 | `RAW_AC.INGESTION.BATCH_CONTROL` with audit trail |
| **dbt Models** | ~{{NUM_DBT_MODELS}} | Staging (1:1 from raw) + Marts (DIM/FACT) |
| **dbt Tests** | ~{{NUM_DBT_TESTS}} | not_null, unique, relationships, custom DQ |
| **Recommendations Report** | 1 | Clustering keys, anti-pattern fixes, performance improvements |
""")

st.space("small")

st.markdown("##### Location")
with st.container(border=True):
    st.markdown("""
:material/location_on: **{{VENUE_NAME}}, {{VENUE_CITY}}**

{{EVENT_DATE}} — {{EVENT_TIME_RANGE}}
""")
