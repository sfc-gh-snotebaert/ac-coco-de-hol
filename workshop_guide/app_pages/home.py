import streamlit as st

st.title("Air Canada Data Engineering Workshop")
st.markdown("Building Enterprise Pipelines with Cortex Code")

st.space("small")

col1, col2, col3 = st.columns(3)
col1.metric("Sections", "5", help="Hands-on lab sections")
col2.metric("Prompts", "11", help="Total prompts across all sessions")
col3.metric("Duration", "2.5 hrs", help="Total workshop time")

st.space("medium")

st.markdown("#### How this workshop works")

st.markdown("""
Each section has **numbered prompts** that you copy and paste into **Cortex Code**:

- **Cortex Code** — your AI pair-programmer for building infrastructure, pipelines, and reviewing code
- Each prompt builds on the previous — run them in order throughout the session

You will go from raw source data to a production-ready dimensional warehouse, with enterprise-grade ingestion, automated testing, and code review — all driven by natural language prompts.
""")

st.space("small")

st.markdown("#### The scenario")
with st.container(border=True):
    st.markdown("""
Air Canada's operational systems — flight operations and reservations — run on a Postgres database (PG1, airline_ops). Your mission: build an enterprise-grade data pipeline that ingests this data into Snowflake with Openflow, transforms it into an Iceberg-based dimensional warehouse with dbt, and optimizes it for production — all using Cortex Code as your AI pair-programmer.

We'll build a complete data engineering platform covering:

| Layer | What we build | Source |
|-------|---------------|--------|
| **Ingestion** | Openflow Gen2 CDC connector → AIRLINE_OPS | Postgres PG1 (airline_ops) |
| **EDW** | dbt staging + Iceberg dimensional marts in EDW.GOLD, driven by STTMs | AIRLINE_OPS replicated tables |
| **Quality** | dbt tests as data quality gates, consolidated DQ summary report | Mart models |
| **Optimization** | Code review, clustering recommendations, anti-pattern fixes | Generated SQL |
""")

st.space("small")

st.markdown("#### What we're building")

with st.container(border=True):
    st.markdown("""
In 2.5 hrs, we build an enterprise data engineering pipeline end-to-end:

**1. Review Current Configuration** — Explore the pre-provisioned AIRLINE_OPS and PG_SETUP databases and verify the Openflow deployment (DEPLOYMENT_DEV) and runtime (RUNTIME_PG) are active.

**2. Create Openflow Postgres Connector** — Create PG_CDC_CONNECTOR on RUNTIME_PG, replicate the airline_ops source into AIRLINE_OPS via CDC, and verify the initial load.

**3. Create dbt Project from STTM Files** — Accept four Source-to-Target Mapping documents, generate a dbt project with staging models and Iceberg dimensional marts in EDW.GOLD (with SCD2 in DIM_PASSENGER), run automated data quality tests, and produce a summary report.

**4. Code Review & Optimization** — Use Cortex Code as a code review agent to scan for SQL anti-patterns, analyze query profiles, and recommend clustering strategies.

**5. Data Engineer Skill (Stretch)** — Package the code review workflow as a reusable Cortex Code skill.
""")

st.space("small")

st.markdown("#### Prerequisites")
with st.container(border=True):
    st.markdown("""
- Snowflake account with **ACCOUNTADMIN** role — pre-provisioned with Openflow enabled (see **Getting Started**)
- **Cortex Code** open in Snowsight and connected to your account
- STTM files (provided in the workshop repo, linked in Session 3)
""")

st.space("medium")
st.caption("Built for the September 15, 2026 workshop  :material/location_on:  Air Canada Centre, Montreal, QC")
