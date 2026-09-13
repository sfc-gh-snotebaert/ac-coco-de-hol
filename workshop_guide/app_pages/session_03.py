import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built

render_session_header(3, "Create dbt Project from STTM Files", "9:45 AM", "40 min", "dbt project generated from enterprise STTMs — staging models plus Iceberg dimensional marts in EDW.GOLD with SCD2 and automated tests")

render_technologies_used([
    {"name": "dbt (Data Build Tool)", "description": "A SQL-first transformation framework. Models are SELECT statements; dbt handles DDL, dependencies, testing, and documentation.", "icon": "build_circle"},
    {"name": "Source-to-Target Mapping (STTM)", "description": "An enterprise specification defining column mappings, SCD types, transformation logic, PII flags, and data sensitivity — the contract between analysts and engineers.", "icon": "map"},
    {"name": "Snowflake-Managed Iceberg Tables", "description": "Iceberg tables with Snowflake as the catalog and Snowflake-managed storage (EXTERNAL_VOLUME = SNOWFLAKE_MANAGED). Open format, no external volume configuration required.", "icon": "table_view"},
])

st.markdown("""
**Before running the prompts below**, review the four STTM documents:

1. Download the STTMs from the repo:
   - [sttm_dim_airport.csv](https://github.com/sfc-gh-snotebaert/ac-coco-de-hol/raw/main/sttm/sttm_dim_airport.csv)
   - [sttm_dim_flight.csv](https://github.com/sfc-gh-snotebaert/ac-coco-de-hol/raw/main/sttm/sttm_dim_flight.csv)
   - [sttm_dim_passenger.csv](https://github.com/sfc-gh-snotebaert/ac-coco-de-hol/raw/main/sttm/sttm_dim_passenger.csv)
   - [sttm_fact_booking.csv](https://github.com/sfc-gh-snotebaert/ac-coco-de-hol/raw/main/sttm/sttm_fact_booking.csv)
2. Each has four sections: Cover Sheet, Version Control, Data Dictionary, and the STTM mapping itself
3. Note the key columns: `TARGET_TYPE` (Type 1, Type 2, Technical Field), `TRANSFORMATION_LOGIC`, `PII_FLAG`, and `KEY_TYPE`
4. DIM_PASSENGER is the only SCD Type 2 table — the others are simple Type 1 loads with technical columns
5. You will paste the STTM contents into the first prompt below
""")

st.space("small")


PROMPT_3_1 = """I have four enterprise Source-to-Target Mapping (STTM) documents that define the EDW GOLD layer for our Air Canada data platform. They are in the sttm/ folder of my current workspace: sttm_dim_airport.csv, sttm_dim_flight.csv, sttm_dim_passenger.csv, and sttm_fact_booking.csv. Read them.

Using these STTMs, generate a dbt project called ac_edw that implements all four GOLD tables:

0. Prerequisites: create the EDW database with a GOLD schema if they do not exist (target: EDW.GOLD).

1. Create a staging model in EDW.STAGING for each source table, reading from the Openflow-replicated tables in AIRLINE_OPS:
   - stg_airports — from AIRLINE_OPS.FLIGHT_OPS.AIRPORTS
   - stg_flights — from AIRLINE_OPS.FLIGHT_OPS.FLIGHTS
   - stg_passengers — from AIRLINE_OPS.RESERVATIONS.PASSENGERS
   - stg_bookings — from AIRLINE_OPS.RESERVATIONS.BOOKINGS
   Each staging model applies the column mappings, type casts, and transformation logic defined in the STTMs.

2. Create the mart models in EDW.GOLD, implementing each STTM exactly:
   - DIM_AIRPORT — surrogate key, IATA_CODE business key, direct mappings, technical columns (CREATEDBATCHLOGID, UPDATEDBATCHLOGID, UPDATETYPE)
   - DIM_FLIGHT — surrogate key, FLIGHT_ID business key, direct mappings, technical columns
   - DIM_PASSENGER — full SCD Type 2: SCDSTARTDATETIME / SCDENDDATETIME, CURRENTFLAG, DELETEDFLAG, LATEARRIVINGFLAG, TYPE1HASH change detection (SHA2 over the Type 1 columns), CREATEDBATCHLOGID / UPDATEDBATCHLOGID, UPDATETYPE
   - FACT_BOOKING — surrogate key, PNR business key, FK lookups to DIM_FLIGHT (by FLIGHT_ID) and DIM_PASSENGER (current record by PASSENGER_ID), measures and technical columns

3. All mart models in EDW.GOLD must be materialized as Snowflake-managed Iceberg tables with Snowflake-managed storage: CREATE ICEBERG TABLE ... CATALOG = 'SNOWFLAKE' EXTERNAL_VOLUME = 'SNOWFLAKE_MANAGED'. Configure the dbt materialization accordingly (custom materialization or model config that emits the Iceberg DDL).

4. Use the dbt project structure: models/staging/, models/marts/, dbt_project.yml, sources.yml (pointing at AIRLINE_OPS), and profiles.yml connecting to Snowflake.

Generate all SQL model files and project configuration. Show the complete project structure and SQL for each model."""

render_prompt("Prompt 3.1", "Generate dbt Project from STTMs", PROMPT_3_1)

render_explanation("What this prompt does", """
Generates a complete dbt project implementing the four STTM specifications:

```
ac_edw/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── sources.yml              # AIRLINE_OPS replicated tables
│   ├── staging/
│   │   ├── stg_airports.sql
│   │   ├── stg_flights.sql
│   │   ├── stg_passengers.sql
│   │   └── stg_bookings.sql
│   └── marts/
│       ├── dim_airport.sql
│       ├── dim_flight.sql
│       ├── dim_passenger.sql
│       └── fact_booking.sql
```

**Staging model** — standardizes the replicated source and applies STTM transformations:
```sql
-- models/staging/stg_passengers.sql
SELECT
    PASSENGER_ID,
    CONCAT_WS(' ', TRIM(FIRST_NAME), TRIM(LAST_NAME)) AS NAME_PASSENGER,
    LOWER(TRIM(EMAIL)) AS EMAIL,
    UPPER(TRIM(LOYALTY_TIER)) AS LOYALTY_TIER,
    HOME_AIRPORT
FROM {{ source('airline_ops', 'RESERVATIONS_PASSENGERS') }}
```

**Mart model (Iceberg)** — the marts are created as Snowflake-managed Iceberg tables:
```sql
-- The materialization emits DDL equivalent to:
CREATE ICEBERG TABLE EDW.GOLD.DIM_PASSENGER (
    DIM_PASSENGER_KEY BIGINT,   -- autoincrement surrogate key
    PASSENGER_ID BIGINT,
    NAME_PASSENGER VARCHAR(200),
    EMAIL VARCHAR(200),
    LOYALTY_TIER VARCHAR(20),
    HOME_AIRPORT VARCHAR(3),
    LATEARRIVINGFLAG CHAR(1),
    CURRENTFLAG CHAR(1),
    DELETEDFLAG CHAR(1),
    SCDSTARTDATETIME TIMESTAMP_NTZ,
    SCDENDDATETIME TIMESTAMP_NTZ,
    TYPE1HASH VARCHAR(64),
    CREATEDBATCHLOGID BIGINT,
    UPDATEDBATCHLOGID BIGINT,
    UPDATETYPE VARCHAR(10)
)
  CATALOG = 'SNOWFLAKE'
  EXTERNAL_VOLUME = 'SNOWFLAKE_MANAGED';
```

**Why Iceberg with Snowflake-managed storage?** The GOLD layer becomes an open-format data product — readable by Spark, Trino, and other engines through the Iceberg REST catalog — while Snowflake stores and manages all the files (no external volume or IAM setup required).

**DIM_PASSENGER SCD2 logic:**
- New records → INSERT with CURRENTFLAG='1', UPDATETYPE='INSERT'
- Changed records (TYPE1HASH mismatch) → expire old (set SCDENDDATETIME, CURRENTFLAG='0') + insert new version with UPDATETYPE='UPDATE'
- Deleted records → set DELETEDFLAG='1', UPDATETYPE='DELETE'

The STTM is the **contract** — Cortex Code translates it directly into executable dbt models.
""")


PROMPT_3_2 = """For the ac_edw dbt project, generate a comprehensive test suite for the DIM_PASSENGER model based on its STTM metadata (sttm_dim_passenger.csv):

1. Schema tests (in schema.yml) derived from the STTM:
   - DIM_PASSENGER_KEY: not_null + unique (it's the PK per KEY_TYPE)
   - PASSENGER_ID: not_null + unique among current records (it's the AK — alternate/business key)
   - All columns marked TARGET_NULLABLE = 'No': not_null tests
   - CURRENTFLAG: accepted_values ['0', '1']
   - DELETEDFLAG: accepted_values ['0', '1']
   - LATEARRIVINGFLAG: accepted_values ['Y', 'N']
   - UPDATETYPE: accepted_values ['INSERT', 'UPDATE', 'DELETE']
   - HOME_AIRPORT: relationships test to DIM_AIRPORT.IATA_CODE (FK per KEY_TYPE)

2. Custom data quality tests (in tests/ folder):
   - scd_no_overlapping_versions: For any PASSENGER_ID, date ranges (SCDSTARTDATETIME to SCDENDDATETIME) must not overlap
   - exactly_one_current_record: Every PASSENGER_ID with DELETEDFLAG='0' must have exactly one record with CURRENTFLAG='1'
   - hash_integrity: TYPE1HASH must match the recomputed SHA2 of the Type 1 columns (detect drift/corruption)

3. PII-aware tests (derived from PII_FLAG column in STTM):
   - Verify that columns flagged as PII (NAME_PASSENGER, EMAIL) have masking policies applied

Generate all test files and show me the complete test configuration."""

render_prompt("Prompt 3.2", "Generate dbt Tests for DIM_PASSENGER", PROMPT_3_2)

render_explanation("What this prompt does", """
Creates tests derived directly from the STTM metadata — not guesswork:

**Schema tests** (in `models/marts/schema.yml`):
```yaml
models:
  - name: dim_passenger
    columns:
      - name: DIM_PASSENGER_KEY
        tests:
          - not_null
          - unique
      - name: PASSENGER_ID
        tests:
          - not_null
          - unique:
              where: "CURRENTFLAG = '1' AND DELETEDFLAG = '0'"
      - name: HOME_AIRPORT
        tests:
          - relationships:
              to: ref('dim_airport')
              field: IATA_CODE
      - name: UPDATETYPE
        tests:
          - accepted_values:
              values: ['INSERT', 'UPDATE', 'DELETE']
```

**Custom SCD integrity tests** (in `tests/`):
```sql
-- tests/scd_no_overlapping_versions.sql
SELECT a.PASSENGER_ID, a.SCDSTARTDATETIME, a.SCDENDDATETIME
FROM {{ ref('dim_passenger') }} a
JOIN {{ ref('dim_passenger') }} b
  ON a.PASSENGER_ID = b.PASSENGER_ID
  AND a.DIM_PASSENGER_KEY != b.DIM_PASSENGER_KEY
  AND a.SCDSTARTDATETIME < COALESCE(b.SCDENDDATETIME, '9999-12-31')
  AND b.SCDSTARTDATETIME < COALESCE(a.SCDENDDATETIME, '9999-12-31')
```

The key insight: **the STTM itself tells you what to test.** PK columns get uniqueness tests, nullable flags drive not_null tests, KEY_TYPE drives relationship tests, and SCD metadata drives temporal integrity tests.
""")


PROMPT_3_3 = """Now execute the dbt project and produce a data quality report:

1. Run `dbt run` to build the staging and mart models in EDW
2. Run `dbt test` to execute all schema tests and custom DQ tests
3. Produce a consolidated summary report showing:
   - Total models built and their status (success/error)
   - Total tests run, passed, failed, and warned
   - For any failed tests: the test name, the model it applies to, and the number of failing rows
   - Row counts for each GOLD table: DIM_AIRPORT, DIM_FLIGHT, DIM_PASSENGER, FACT_BOOKING
   - For DIM_PASSENGER: distinct PASSENGER_ID count and count of current active records (CURRENTFLAG='1')

4. If any tests fail, explain what the failures mean and suggest a fix
5. Confirm the GOLD tables are Iceberg tables (SHOW ICEBERG TABLES IN EDW.GOLD) and show a sample of 5 rows from DIM_PASSENGER to verify the SCD2 structure

Execute and show the full report."""

render_prompt("Prompt 3.3", "Execute Pipeline & DQ Report", PROMPT_3_3)

render_explanation("What this prompt does", """
Runs the full dbt pipeline and produces a quality report:

```
dbt run --project-dir ac_edw
dbt test --project-dir ac_edw
```

**Expected output:**
```
DQ Summary Report
=================
Models: 8 built (4 staging + 4 marts) | 0 errors
Tests:  12 passed | 0 failed | 0 warned

GOLD Layer (Iceberg tables in EDW.GOLD):
  DIM_AIRPORT:      120 rows
  DIM_FLIGHT:     1,850 rows
  DIM_PASSENGER:  3,200 rows (2,980 current records)
  FACT_BOOKING:  12,400 rows

SHOW ICEBERG TABLES IN EDW.GOLD → all 4 marts listed as Iceberg
```

This validates that:
- All STTM mappings were implemented correctly
- The SCD2 logic works (history versions and current records are consistent)
- No overlapping date ranges, exactly one current record per active passenger
- FK integrity holds (bookings reference real flights and passengers)
- The GOLD layer is materialized as Snowflake-managed Iceberg tables
""")


render_key_concepts([
    {"term": "SCD Type 2", "definition": "A slowly changing dimension pattern that preserves full history. When a value changes, the current record is expired (SCDENDDATETIME set) and a new version is inserted. Enables point-in-time queries ('what was this passenger's tier on Jan 1?')."},
    {"term": "TYPE1HASH", "definition": "A SHA-256 hash computed over all Type 1 (overwritable) columns. Used for change detection: if the incoming hash differs from the existing hash, the record has changed and needs updating."},
    {"term": "Snowflake-Managed Iceberg Table", "definition": "An Iceberg table using Snowflake as the catalog and Snowflake-managed storage (EXTERNAL_VOLUME = SNOWFLAKE_MANAGED). Open format interoperability with zero external volume or IAM configuration."},
    {"term": "FK Lookups in Facts", "definition": "FACT_BOOKING resolves FLIGHT_KEY and PASSENGER_KEY by looking up the dimension surrogate keys from the source business keys — the standard pattern when facts reference dimensions by natural keys."},
    {"term": "STTM as Contract", "definition": "The STTM is not documentation — it's a specification. Every column, type, nullability, and transformation is defined. Cortex Code translates this contract directly into executable code."},
])

render_what_you_built([
    "dbt project (ac_edw) implementing all 4 STTMs",
    "4 staging models reading from AIRLINE_OPS replicated tables",
    "4 mart models in EDW.GOLD as Snowflake-managed Iceberg tables",
    "DIM_PASSENGER with full SCD Type 2 logic (versioning, hash change detection, soft deletes)",
    "~12 data quality tests derived from STTM metadata",
    "Consolidated DQ summary report validating the EDW layer",
])
