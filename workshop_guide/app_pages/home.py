import streamlit as st

st.title("Air Canada Data Engineering Workshop")
st.markdown("Building Enterprise Pipelines with Cortex Code")

st.space("small")

col1, col2, col3 = st.columns(3)
col1.metric("Sections", "5", help="Hands-on lab sections")
col2.metric("Prompts", "14", help="Total prompts across all sessions")
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
Air Canada's operational systems — reservations, flight ops, maintenance, and loyalty — run on a legacy Postgres database. Your mission: build an enterprise-grade data pipeline that ingests this data into Snowflake, transforms it into a dimensional warehouse, and optimizes it for production — all using Cortex Code as your AI pair-programmer.

We'll build a complete data engineering platform covering:

| Layer | What we build | Source |
|-------|---------------|--------|
| **Ingestion** | Openflow connector → Iceberg tables with audit columns | Postgres (operational systems) |
| **EDW** | dbt staging + dimensional marts driven by STTM | Raw Iceberg tables |
| **Quality** | dbt tests as data quality gates, DQ summary report | Mart models |
| **Optimization** | Code review, clustering recommendations, anti-pattern fixes | Generated SQL |
""")

st.space("small")

st.markdown("#### What we're building")

with st.container(border=True):
    st.markdown("""
In 2.5 hrs, we build an enterprise data engineering pipeline end-to-end:

**1. Environment Setup** — Create the multi-layer database architecture (RAW, EDW), warehouses, and verify Openflow readiness.

**2. Enterprise Ingestion with Openflow** — Connect to a Postgres source database, land data into Snowflake Iceberg tables with enterprise naming standards, batch control, and audit columns.

**3. EDW Pipeline from STTM** — Accept a Source-to-Target Mapping (JSON), generate a dbt project with staging and mart models, run automated data quality tests, and produce a test report.

**4. Code Review & Optimization** — Use Cortex Code as a code review agent to scan for SQL anti-patterns, analyze query profiles, and recommend clustering strategies.

**5. Data Engineer Skill (Stretch)** — Package the code review workflow as a reusable Cortex Code skill.
""")

st.space("small")

st.markdown("#### Prerequisites")
with st.container(border=True):
    st.markdown("""
- Snowflake account with **ACCOUNTADMIN** role — pre-provisioned with Openflow enabled (see **Getting Started**)
- **Cortex Code** open in Snowsight and connected to your account
- Source database connection details (provided during the workshop)
""")

st.space("medium")
st.caption("Built for the September 15, 2026 workshop  :material/location_on:  Air Canada Centre, Montreal, QC")
