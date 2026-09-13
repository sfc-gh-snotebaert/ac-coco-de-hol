# Restructure Air Canada HOL — 5 Sessions, Iceberg EDW.GOLD

## Context

Repo: `sfc-gh-snotebaert/ac-coco-de-hol` — Air Canada Data Engineering HOL Streamlit app. Confirmed data flow:

```
Postgres PG1 (airline_ops) ──Openflow CDC──▶ AIRLINE_OPS.{FLIGHT_OPS,RESERVATIONS}
        ──dbt (Iceberg tables)──▶ EDW.GOLD.{DIM_AIRPORT,DIM_FLIGHT,DIM_PASSENGER,FACT_BOOKING}
```

Session structure (per user):
| Session | Topic | Prompts |
|---|---|---|
| 1 | Review current configuration | P1: review AIRLINE_OPS + PG_SETUP objects; P2: review Openflow deployment/runtime config |
| 2 | Create Openflow Postgres connector | P1: add-connector.md prompt (start + monitor + verify row counts) |
| 3 | Create dbt project from STTM files | P1: dbt project for 4 models from STTMs; P2: dbt tests for DIM_PASSENGER (reuse+update existing); P3: dbt run + dbt test + summary report |
| 4 | Code Review | Keep, review for accuracy |
| 5 | Review Skill (stretch) | Keep, review for accuracy |

**Iceberg finding (verified in Snowflake docs):** Snowflake-managed Iceberg tables with Snowflake storage use `CREATE ICEBERG TABLE ... CATALOG = 'SNOWFLAKE' EXTERNAL_VOLUME = 'SNOWFLAKE_MANAGED'` — **no external volume object or IAM setup is required**. Therefore `setup_openflow_pg.sql` needs **no Iceberg additions**. The dbt prompt in Session 3 instructs that mart models materialize as Iceberg tables with Snowflake-managed storage (dbt-snowflake iceberg materialization; if unavailable in the attendee's dbt version, CoCo generates a custom materialization macro emitting the CTAS with CATALOG='SNOWFLAKE' EXTERNAL_VOLUME='SNOWFLAKE_MANAGED').

**SCD decision:** SCD2 (SCDSTART/ENDDATETIME, CURRENTFLAG, hashes, LATEARRIVINGFLAG) applies **only to DIM_PASSENGER**. The other STTMs keep standard technical columns (surrogate key, business key, batch log IDs, UPDATETYPE) without SCD2 scaffolding.

## Implementation Steps

### 1. Create 4 STTM files in `sttm/`, remove `sttm_dim_customer.csv`
Same 4-section structure as [sttm_dim_customer.csv](sttm/sttm_dim_customer.csv) (COVER SHEET / VERSION CONTROL / DATA DICTIONARY / STTM):
- `sttm_dim_airport.csv` — EDW.GOLD.DIM_AIRPORT ← AIRLINE_OPS.FLIGHT_OPS.AIRPORTS (iata_code, airport_name, city, country, timezone). No SCD2.
- `sttm_dim_flight.csv` — EDW.GOLD.DIM_FLIGHT ← AIRLINE_OPS.FLIGHT_OPS.FLIGHTS (flight_id, flight_number, origin, destination, departure_ts, arrival_ts, aircraft_id, status). No SCD2.
- `sttm_dim_passenger.csv` — EDW.GOLD.DIM_PASSENGER ← AIRLINE_OPS.RESERVATIONS.PASSENGERS (passenger_id, first_name, last_name, email, loyalty_tier, home_airport). **Full SCD2** like DIM_CUSTOMER: SCDSTARTDATETIME/SCDENDDATETIME, CURRENTFLAG, DELETEDFLAG, LATEARRIVINGFLAG, TYPE1HASH (over name/email/tier/home_airport), CREATEDBATCHLOGID/UPDATEDBATCHLOGID, UPDATETYPE. PII flags on NAME_PASSENGER + EMAIL with Masking.
- `sttm_fact_booking.csv` — EDW.GOLD.FACT_BOOKING ← AIRLINE_OPS.RESERVATIONS.BOOKINGS (pnr, booking_date, flight_id FK, passenger_id FK, fare_class, status, total_amount). Insert-oriented; no SCD2.

### 2. Rewrite `session_01.py` — Review Current Configuration
- PROMPT_1_1: reuse existing explore prompt (AIRLINE_OPS + PG_SETUP objects); fix card title
- PROMPT_1_2: reuse Openflow verification prompt; explanation names DEPLOYMENT_DEV / RUNTIME_PG, remove stale AC_OPENFLOW_RT snippet
- Remove prompts 1.3/1.4 (batch control, EDW creation); update header, technologies, concepts, what-you-built

### 3. Rewrite `session_02.py` — Create Openflow Postgres Connector
- PROMPT_2_1: [add-connector.md](add-connector.md) text + start connector, monitor to initial-load completion, verify row counts in AIRLINE_OPS.{RESERVATIONS,FLIGHT_OPS}
- Explanation: Gen2 connector SQL (RUNTIME = OPENFLOW_DB.RUNTIME.RUNTIME_PG), credentials from PG_SETUP.CONFIG.PG_INSTANCE_INFO, publication/CDC concepts
- Update technologies, concepts, what-you-built

### 4. Rewrite `session_03.py` — Create dbt Project from STTM Files
- Intro: link 4 STTM files (GitHub raw URLs)
- PROMPT_3_1: dbt project `ac_edw` from all 4 STTMs — staging models per source table (from AIRLINE_OPS) + marts DIM_AIRPORT, DIM_FLIGHT, DIM_PASSENGER (SCD2 + hash change detection), FACT_BOOKING in **EDW.GOLD**, materialized as **Snowflake-managed Iceberg tables** (CATALOG='SNOWFLAKE', EXTERNAL_VOLUME='SNOWFLAKE_MANAGED')
- PROMPT_3_2: reuse existing test prompt updated for DIM_PASSENGER (AK, PII on name/email, SCD integrity tests)
- PROMPT_3_3: reuse run+report prompt — dbt run, dbt test, consolidated DQ summary across all 4 models
- Update explanations (Iceberg mart DDL examples, EDW.GOLD targets), concepts, what-you-built

### 5. Review `session_04.py` + `session_05.py` for accuracy
- Session 4: fix `EDW_AC.MARTS` → `EDW.GOLD`; `FACT_FLIGHT_OPS` → real models (FACT_BOOKING, DIM_FLIGHT, DIM_PASSENGER); align example model names in report
- Session 5: keep (generic references are accurate)

### 6. Update `home.py`, `agenda.py`, `getting_started.py`, `streamlit_app.py`
- home: metrics (Prompts = 11), scenario table (Iceberg EDW.GOLD layer), "What we're building" list to new session titles
- agenda: new session titles; "What you'll build" table (Openflow connector, 4 Iceberg tables in EDW.GOLD, ~8 dbt models, ~12 tests, recommendations report); times/venue unchanged
- getting_started: read-through only (content accurate)
- streamlit_app: verify page list/titles

### 7. `setup_openflow_pg.sql`
- **No Iceberg changes required** — SNOWFLAKE_MANAGED storage needs no external volume. Only read-through to confirm nothing conflicts (e.g., EDW database creation is not needed pre-event since dbt/attendees create EDW.GOLD during Session 3 — the Session 3 prompt handles `CREATE DATABASE EDW` + `CREATE SCHEMA GOLD` if missing).

### 8. Validate & deploy
- Restart Streamlit app, click through all pages
- Grep `workshop_guide/` for stale refs — zero hits: `RAW_AC`, `EDW_AC`, `AC_POSTGRES_CONNECTOR`, `AC_OPENFLOW_RT`, `DIM_CUSTOMER_MASTER`, `BATCH_CONTROL`, `maintenance`, `aircanada_ops`
- Commit + push to origin/main

## Verification
- All pages render; prompt numbering continuous; STTMs valid CSV with correct section structure
- DIM_PASSENGER is the only STTM with SCD2 columns; all 4 target EDW.GOLD
- Session 3 prompt explicitly requires Iceberg tables with CATALOG='SNOWFLAKE' EXTERNAL_VOLUME='SNOWFLAKE_MANAGED'
- Stale-ref grep sweep returns zero; git push succeeds

## Critical Files
- [add-connector.md](add-connector.md) — Session 2 prompt source
- [sttm/sttm_dim_customer.csv](sttm/sttm_dim_customer.csv) — STTM structural template
- [workshop_guide/app_pages/session_03.py](workshop_guide/app_pages/session_03.py) — dbt + Iceberg materialization prompts
- [setup_pg_source_db/setup_airline_ops.sql](setup_pg_source_db/setup_airline_ops.sql) — authoritative source columns
- [setup_openflow_pg/setup_openflow_pg.sql](setup_openflow_pg/setup_openflow_pg.sql) — verified: no Iceberg additions needed