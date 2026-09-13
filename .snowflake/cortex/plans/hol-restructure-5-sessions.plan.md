---
name: "hol-restructure-5-sessions"
created: "2026-09-13T20:41:09.516Z"
status: pending
---

# Restructure Air Canada HOL — 5 Sessions, Real Environment

## Context

The repo (`sfc-gh-snotebaert/ac-coco-de-hol`) hosts the Air Canada Data Engineering HOL Streamlit app. The user has restructured the workshop. New data flow (no separate Iceberg/batch-control step anymore):

```
Postgres PG1 (airline_ops) ──Openflow CDC──▶ Snowflake AIRLINE_OPS.{FLIGHT_OPS,RESERVATIONS}
        ──dbt──▶ Snowflake EDW.GOLD.{DIM_AIRPORT,DIM_FLIGHT,DIM_PASSENGER,FACT_BOOKING}
```

New session structure (per user):

| Session | Topic                              | Prompts                                                                                                                                     |
| ------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1       | Review current configuration       | P1: review AIRLINE\_OPS + PG\_SETUP objects; P2: review Openflow deployment/runtime                                                         |
| 2       | Create Openflow Postgres connector | P3 (session prompt 1): the add-connector.md prompt                                                                                          |
| 3       | Create dbt project from STTM files | P1: dbt project for 4 models from STTMs; P2: dbt tests for DIM\_PASSENGER (reuse existing, update); P3: dbt run + dbt test + summary report |
| 4       | Code Review                        | Keep existing — review for accuracy only                                                                                                    |
| 5       | Review Skill (stretch)             | Keep existing — review for accuracy only                                                                                                    |

Reusable material identified in current files:

- session\_01.py: PROMPT\_1\_1 (explore AIRLINE\_OPS/PG\_SETUP) fits new Session 1 P1; PROMPT\_1\_2 (show deployments/runtimes/connectors) fits Session 1 P2
- add-connector.md: PG\_CDC\_CONNECTOR prompt → Session 2 P1
- session\_03.py: PROMPT\_3\_1/3\_2/3\_3 (dbt project from STTM, tests from STTM metadata, run+report) — reuse with updated model names, sources (AIRLINE\_OPS not RAW\_AC), and STTM set
- session\_04.py: keep; fix stale refs (EDW\_AC.MARTS → EDW\.GOLD, FACT\_FLIGHT\_OPS doesn't exist, model names fact\_booking/dim\_passenger → FACT\_BOOKING/DIM\_PASSENGER per final naming)
- session\_05.py: keep as-is (references Session 4 generically — accurate)
- Source table schemas from setup\_airline\_ops.sql: airports (iata\_code PK, airport\_name, city, country, timezone), flights (flight\_id, flight\_number, origin, destination, departure\_ts, arrival\_ts, aircraft\_id, status), passengers (passenger\_id, first\_name, last\_name, email, loyalty\_tier, home\_airport), bookings (pnr PK, booking\_date, flight\_id, passenger\_id, fare\_class, status, total\_amount)
- STTM structure template: sttm\_dim\_customer.csv — 4 sections (COVER SHEET / VERSION CONTROL / DATA DICTIONARY / STTM), Air Canada branding, SCD2 + hash + batch-log technical columns

## Implementation Steps

### 1. Create 4 STTM files in `sttm/` (replace dim\_customer)

Following sttm\_dim\_customer.csv structure exactly (same section headers, same technical-column pattern: surrogate KEY, AK, LATEARRIVINGFLAG, CURRENTFLAG, DELETEDFLAG, SCDSTART/ENDDATETIME, TYPE1HASH, CREATEDBATCHLOGID, UPDATEDBATCHLOGID, UPDATETYPE):

- **sttm\_dim\_airport.csv** — EDW\.GOLD.DIM\_AIRPORT ← AIRLINE\_OPS.FLIGHT\_OPS.AIRPORTS. Business key IATA\_CODE; columns: AIRPORT\_NAME, CITY, COUNTRY, TIMEZONE. Small dim → SCD1-style with SCD2 technical scaffolding retained.
- **sttm\_dim\_flight.csv** — EDW\.GOLD.DIM\_FLIGHT ← AIRLINE\_OPS.FLIGHT\_OPS.FLIGHTS. AK FLIGHT\_ID; FLIGHT\_NUMBER, ORIGIN, DESTINATION, DEPARTURE\_TS, ARRIVAL\_TS, AIRCRAFT\_ID, STATUS.
- **sttm\_dim\_passenger.csv** — EDW\.GOLD.DIM\_PASSENGER ← AIRLINE\_OPS.RESERVATIONS.PASSENGERS. AK PASSENGER\_ID; FIRST\_NAME+LAST\_NAME → NAME\_PASSENGER (PII, masking, like NAME\_CUSTOMER), EMAIL (PII), LOYALTY\_TIER, HOME\_AIRPORT.
- **sttm\_fact\_booking.csv** — EDW\.GOLD.FACT\_BOOKING ← AIRLINE\_OPS.RESERVATIONS.BOOKINGS. AK PNR; BOOKING\_DATE, FLIGHT\_ID (FK), PASSENGER\_ID (FK), FARE\_CLASS, STATUS, TOTAL\_AMOUNT + technical columns (insert-oriented fact; UPDATETYPE retained).
- Delete `sttm/sttm_dim_customer.csv` (no longer referenced; sources don't exist).

### 2. Rewrite `session_01.py` — Review Current Configuration

- Header: title "Review Current Configuration", subtitle about exploring the pre-provisioned environment
- PROMPT\_1\_1: reuse existing explore prompt (AIRLINE\_OPS + PG\_SETUP objects) — fix the mismatched prompt card title ("Create Databases, Schemas & Warehouse" → "Explore Pre-Provisioned Objects")
- PROMPT\_1\_2: reuse existing Openflow verification prompt (show deployments/runtimes/connectors); update explanation to name DEPLOYMENT\_DEV / RUNTIME\_PG expectations and remove the stale `CREATE OPENFLOW RUNTIME AC_OPENFLOW_RT` snippet
- Remove PROMPT\_1\_3/1\_4 (batch control, EDW creation) — no longer part of the lab
- Update technologies, key concepts, what-you-built to match a review-only session

### 3. Rewrite `session_02.py` — Create Openflow Postgres Connector

- PROMPT\_2\_1: use add-connector.md text verbatim as the core (PG\_CDC\_CONNECTOR on RUNTIME\_PG, credentials from PG\_SETUP.CONFIG.PG\_INSTANCE\_INFO, snowflake\_admin, database airline\_ops, schemas flight\_ops + reservations, publication openflow\_pub, target AIRLINE\_OPS), plus steps to start the connector and monitor until initial load completes, then show row counts in AIRLINE\_OPS
- Explanation: Gen2 connector SQL examples (CREATE OPENFLOW CONNECTOR ... RUNTIME = OPENFLOW\_DB.RUNTIME.RUNTIME\_PG), publication/CDC concepts, why credentials come from PG\_SETUP
- Update technologies, key concepts, what-you-built (connector created, CDC replicating 4 tables into AIRLINE\_OPS)

### 4. Rewrite `session_03.py` — Create dbt Project from STTM Files

- Intro: link the 4 STTM files (GitHub raw URLs to sttm/ in this repo)
- PROMPT\_3\_1: reuse existing structure — dbt project `ac_edw` from all 4 STTMs: staging models (one per source table, reading AIRLINE\_OPS.FLIGHT\_OPS.\* / AIRLINE\_OPS.RESERVATIONS.\*) + mart models DIM\_AIRPORT, DIM\_FLIGHT, DIM\_PASSENGER (SCD2 + hash change detection per DIM\_CUSTOMER pattern), FACT\_BOOKING in EDW\.GOLD
- PROMPT\_3\_2: reuse existing DIM\_CUSTOMER test prompt, updated for DIM\_PASSENGER (AK PASSENGER\_ID unique among current, PII tests on NAME\_PASSENGER/EMAIL, SCD integrity tests)
- PROMPT\_3\_3: reuse existing run+report prompt — dbt run, dbt test, consolidated DQ summary report across all 4 models
- Update STTM download link, explanations (sources from AIRLINE\_OPS, marts in EDW\.GOLD), key concepts, what-you-built

### 5. Review `session_04.py` — Code Review (keep, fix accuracy)

- PROMPT\_4\_1: references "ac\_edw project" — accurate; model names in examples OK
- PROMPT\_4\_2: fix stale refs — `FACT_FLIGHT_OPS` doesn't exist (models are FACT\_BOOKING, DIM\_FLIGHT, DIM\_PASSENGER); clustering examples `EDW_AC.MARTS.*` → `EDW.GOLD.*`; review the "typical query patterns" text (loyalty team filters still valid via DIM\_PASSENGER)
- PROMPT\_4\_3: example report model names (fact\_booking/dim\_passenger/fact\_flight) → align to actual model names
- Keep structure, key concepts, what-you-built as-is

### 6. Review `session_05.py` — Review Skill (keep as-is)

- Content references Session 4 generically — accurate; no changes needed beyond reading. Only touch if a stale reference surfaces.

### 7. Update `home.py`, `agenda.py`, `getting_started.py`, `streamlit_app.py`

- home.py: update metrics (Sessions 5, Prompts count = 2+1+3+3+2 = 11, duration), scenario table (Ingestion: Openflow CDC → AIRLINE\_OPS; EDW: dbt → EDW\.GOLD from 4 STTMs; Quality: dbt tests + DQ report; Optimization unchanged), "What we're building" list to the new 5 session titles
- agenda.py: update session titles in AGENDA list (1: Review Current Configuration, 2: Create Openflow Postgres Connector, 3: Create dbt Project from STTM Files, 4: Code Review & Optimization, 5: Data Engineer Skill (Stretch)); update "What you'll build" table (no RAW\_AC/batch control; connector + 4 dbt models in EDW\.GOLD + tests); times/venue unchanged
- getting\_started.py: content is accurate (Snowsight, ACCOUNTADMIN, Openflow pre-provisioned); no changes expected beyond a read-through
- streamlit\_app.py: verify title/icon page list matches the 5 sessions

### 8. Validate & deploy

- Restart the local Streamlit app, click through all pages in the browser to catch rendering errors
- Grep `workshop_guide/` for stale refs — must be zero: `RAW_AC`, `EDW_AC`, `AC_POSTGRES_CONNECTOR`, `AC_OPENFLOW_RT`, `DIM_CUSTOMER_MASTER`, `maintenance`, `loyalty\.aeroplan`, `aircanada_ops`, `BATCH_CONTROL` (session 1/2 no longer create it)
- `EDW_AC` in session\_04 explanations → `EDW`
- Commit + push to origin/main

## Verification

- All 5 session pages render without errors in the running Streamlit app
- Prompt numbering is continuous per session and matches the structure above
- STTM files parse as valid CSV and follow the dim\_customer section structure
- Grep sweep for stale references returns zero hits in workshop\_guide/
- git push succeeds; GitHub raw URLs for sttm files resolve (after push)

## Critical Files

- add-connector.md — source of the Session 2 connector prompt
- sttm/sttm\_dim\_customer.csv — structural template for the 4 new STTMs
- workshop\_guide/app\_pages/session\_02.py — full rewrite (connector session)
- workshop\_guide/app\_pages/session\_03.py — dbt prompts update (sources, model names, STTM links)
- setup\_pg\_source\_db/setup\_airline\_ops.sql — authoritative source column list for STTMs
