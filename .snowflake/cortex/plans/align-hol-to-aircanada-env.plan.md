---
name: "align-hol-to-aircanada-env"
created: "2026-09-13T16:34:57.310Z"
status: pending
---

# Align Air Canada HOL to Real Environment

## Context

The repo (`sfc-gh-snotebaert/ac-coco-de-hol`) is the workshop app for an **Air Canada Data Engineering HOL**. The session pages describe an older fictional environment (RAW\_AC, AC\_POSTGRES\_CONNECTOR, maintenance/loyalty schemas, DIM\_CUSTOMER\_MASTER source) that doesn't match the real pre-provisioned attendee accounts:

- Openflow deployment **DEPLOYMENT\_DEV**, runtime **RUNTIME\_PG** (in OPENFLOW\_DB.RUNTIME)
- **AIRLINE\_OPS** database with empty RESERVATIONS and FLIGHT\_OPS schemas (CDC target)
- **PG\_SETUP.CONFIG.PG\_INSTANCE\_INFO** holding PG1 host + snowflake\_admin credentials
- Connector to create: **PG\_CDC\_CONNECTOR** (Gen2 Postgres CDC, publication `openflow_pub`, source db `airline_ops`, schemas `flight_ops` + `reservations`) — prompt text is in `add-connector.md`
- Source Postgres tables (from `setup_pg_source_db/setup_airline_ops.sql`): `flight_ops.airports`, `flight_ops.flights`, `reservations.passengers`, `reservations.bookings`

Decisions confirmed with the user:

- Align all sessions to the real env (not just session 2)
- Layering: **AIRLINE\_OPS = raw CDC landing zone**; governed **Iceberg tables live in a separate EDW database** — named **`EDW`** (not EDW\_AC)
- Event details stay as-is (Air Canada Centre Montreal, current agenda times)
- Generate new STTMs: keep `sttm/sttm_dim_customer.csv` as-is, create from scratch (same 4-section structure) **sttm\_dim\_flight.csv, sttm\_dim\_airport.csv, sttm\_fact\_bookings.csv** mapped to the real source columns
- Repo is already GitHub-linked; commit+push at the end

## Target pipeline taught by the workshop

```
Postgres (airline_ops) ──PG_CDC_CONNECTOR──▶ AIRLINE_OPS.{RESERVATIONS,FLIGHT_OPS}   (raw CDC)
        ──Session 2: CTAS governed Iceberg tables──▶ EDW.INGESTION (audit columns)  (governed raw)
        ──Session 3: dbt staging──▶ EDW.STAGING
        ──Session 3: dbt marts──▶ EDW.MARTS (DIM_CUSTOMER, DIM_FLIGHT, DIM_AIRPORT, FACT_BOOKINGS)
        ──Session 4: dbt tests as DQ gates + consolidated DQ report, SQL review, clustering
```

## Tasks

### 1. Create 3 new STTM files (`sttm/`)

Follow the exact 4-section structure of `sttm_dim_customer.csv` (COVER SHEET / VERSION CONTROL / DATA DICTIONARY / STTM), Air Canada branding ([AC235328-SF@AIRCANADA.CA](<> "mailto:AC235328-SF@AIRCANADA.CA"), EDW Phase 1, dated 2026-09-16):

- `sttm_dim_flight.csv` — DIM\_FLIGHT: FLIGHT\_NUMBER (AK), ORIGIN/DESTINATION FK references (display via lookups), DEPARTURE/ARRIVAL timestamps, AIRCRAFT\_ID, STATUS, SCD2 technical columns (KEY, hashes, flags, batch log IDs, UPDATETYPE) mirroring DIM\_CUSTOMER's pattern. Source: AIRLINE\_OPS.FLIGHT\_OPS.FLIGHTS
- `sttm_dim_airport.csv` — DIM\_AIRPORT: IATA\_CODE as AK + surrogate key, AIRPORT\_NAME, CITY, COUNTRY, TIMEZONE, standard technical columns. Source: AIRLINE\_OPS.FLIGHT\_OPS.AIRPORTS
- `sttm_fact_bookings.csv` — FACT\_BOOKINGS: PNR as AK, BOOKING\_DATE, FLIGHT\_KEY/CUSTOMER\_KEY (FK to dims), FARE\_CLASS, STATUS, TOTAL\_AMOUNT + technical columns. Source: AIRLINE\_OPS.RESERVATIONS.BOOKINGS

### 2. Rewrite `workshop_guide/app_pages/session_01.py` (Environment Setup)

- Fix duplication: PROMPT\_1\_2 and PROMPT\_1\_3 are currently identical; PROMPT\_1\_4 is rendered with the wrong constant name (`PROMPT_1_3`)
- PROMPT\_1\_1 (explore): keep — shows AIRLINE\_OPS + PG\_SETUP schemas/contents
- PROMPT\_1\_2 (verify Openflow): rewrite to check DEPLOYMENT\_DEV (active), RUNTIME\_PG (active), no connectors exist yet
- PROMPT\_1\_3 (create EDW): create `EDW` database with INGESTION, STAGING, MARTS schemas; create BATCH\_CONTROL + BATCH\_SUMMARY in `EDW.INGESTION` (currently references RAW\_AC)
- PROMPT\_1\_4 (batch control): merge into PROMPT\_1\_3 or renumber — final: 3 clean prompts
- Update "What you built" list and key concepts to match

### 3. Rewrite `workshop_guide/app_pages/session_02.py` (Enterprise Ingestion)

- PROMPT\_2\_1: use the `add-connector.md` text (PG\_CDC\_CONNECTOR on RUNTIME\_PG, credentials from PG\_SETUP.CONFIG.PG\_INSTANCE\_INFO, snowflake\_admin user, publication openflow\_pub, target AIRLINE\_OPS). Add start-connector and monitor steps
- PROMPT\_2\_2: new prompt — create governed **Iceberg tables in EDW\.INGESTION** (one per replicated source table: AIRPORTS, FLIGHTS, PASSENGERS, BOOKINGS) via CTAS from AIRLINE\_OPS, with UPPERCASE naming, mapped types, audit columns (\_LOADED\_AT, \_BATCH\_ID, \_SOURCE\_SYSTEM), table comments
- PROMPT\_2\_3: batch audit — insert BATCH\_CONTROL records per table with real row counts, show BATCH\_SUMMARY, show row counts
- Update explanations (Gen2 connector SQL examples referencing OPENFLOW\_DB.RUNTIME.RUNTIME\_PG), key concepts, what-you-built

### 4. Rewrite `workshop_guide/app_pages/session_03.py` (EDW Pipeline from STTM)

- Point STTM download links to the 4 files in the repo's `sttm/` folder (GitHub raw URLs)
- PROMPT\_3\_1: build dbt project `ac_edw` from **all four STTMs** — staging models per source (from EDW\.INGESTION Iceberg tables) + mart models DIM\_CUSTOMER, DIM\_FLIGHT, DIM\_AIRPORT, FACT\_BOOKINGS in EDW\.MARTS with SCD2 logic (keep DIM\_CUSTOMER's SCD2/hash pattern as the exemplar)
- PROMPT\_3\_2: dbt tests derived from STTM metadata across all 4 models (not\_null/unique/accepted\_values/relationships + custom SCD integrity tests)
- PROMPT\_3\_3: execute `dbt run` + `dbt test` + consolidated DQ summary report (model statuses, test pass/fail counts, failing rows, row counts per mart)

### 5. Review `session_04.py` (Code Review & Optimization) and `session_05.py`

- Session 4 references FACT\_BOOKING/FACT\_FLIGHT\_OPS models — update model names to FACT\_BOOKINGS/dims that actually exist after task 4; check remaining content (read rest of file during implementation) and align anti-pattern/clustering prompts with the new pipeline
- Session 5 (skill stretch): read and adjust only references that no longer resolve (table/db names); keep the skill-building content
- Both sessions: update EDW\_AC → EDW naming

### 6. Update `home.py`, `agenda.py`, `getting_started.py`, `streamlit_app.py`

- home.py: update scenario table (Ingestion row: "Openflow CDC → governed Iceberg tables in EDW"; EDW row: 4 STTMs; update counts: prompts and object counts to match final content; dbt models count)
- agenda.py: update the "What you'll build" table (EDW database, Iceberg tables in EDW\.INGESTION, dbt models \~8, tests, EDW name) — times/venue unchanged
- getting\_started.py: read and verify — CoCo in Snowsight instructions, signup link, region; update only stale references
- streamlit\_app.py: check title/icon — keep "Air Canada Data Engineering Workshop"

### 7. Validate & deploy

- Restart the local Streamlit app, click through every page in the CoCo browser to catch rendering errors
- Grep for stale references: `RAW_AC`, `EDW_AC`, `AC_POSTGRES_CONNECTOR`, `AC_OPENFLOW_RT`, `DIM_CUSTOMER_MASTER`, `maintenance`, `loyalty`, `aircanada_ops` — must be zero hits in `workshop_guide/`
- Commit + push to origin/main (repo already linked)

## Notes / Open Items

- Signup link for getting\_started.py: current value will be kept unless the user provides a new one
- The generated STTMs are teaching artifacts; SCD Type 2 applies to the dims, FACT\_BOOKINGS is insert-only (UPDATETYPE pattern retained)
- Session 5 remains the optional stretch skill-building session
