import streamlit as st
from pathlib import Path
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built

STTM_DIR = Path(__file__).resolve().parent.parent.parent / "sttm"

render_session_header(3, "Create dbt Project from STTM Files", "9:45 AM", "40 min", "dbt project generated from enterprise STTMs — Iceberg dimensional marts in AIRLINE_OPS_LABUSERXX.GOLD with SCD2 and automated tests")

render_technologies_used([
    {"name": "dbt (Data Build Tool)", "description": "A SQL-first transformation framework. Models are SELECT statements; dbt handles DDL, dependencies, testing, and documentation.", "icon": "build_circle"},
    {"name": "Source-to-Target Mapping (STTM)", "description": "An enterprise specification defining column mappings, SCD types, transformation logic, PII flags, and data sensitivity — the contract between analysts and engineers.", "icon": "map"},
    {"name": "Snowflake-Managed Iceberg Tables", "description": "Iceberg tables with Snowflake as the catalog and Snowflake-managed storage (EXTERNAL_VOLUME = SNOWFLAKE_MANAGED). Open format, no external volume configuration required.", "icon": "table_view"},
])

st.markdown("#### Step 1: Configure Iceberg as the default table format for schema GOLD")

PROMPT_3_0 = """Create a schema called GOLD in AIRLINE_OPS_LABUSERXX that uses SNOWFLAKE as the catalog and SNOWFLAKE_MANAGED as the external volume."""

render_prompt("Prompt 3.0", "Create GOLD schema and set Iceberg as default table format", PROMPT_3_0)
st.warning(":material/edit: **Before executing in CoCo:** replace `XX` in the occurrences of `LABUSERXX` in the prompt with your assigned lab user number.")

render_explanation("What this prompt does", """
Creates the GOLD schema and configures it as an Iceberg schema:

```sql
CREATE SCHEMA IF NOT EXISTS AIRLINE_OPS_LABUSERXX.GOLD;
ALTER SCHEMA AIRLINE_OPS_LABUSERXX.GOLD SET CATALOG = 'SNOWFLAKE' EXTERNAL_VOLUME = 'SNOWFLAKE_MANAGED';
```

Setting the catalog and external volume at the **schema level** means every table created in GOLD automatically inherits Iceberg format — no per-table or per-model config needed. The GOLD layer is readable by Spark, Trino, and other engines through the Iceberg REST catalog, while Snowflake manages all storage.
""")

st.space("small")

st.markdown("#### Step 2: Review & upload the STTMs")

st.markdown("""
**Before running the prompts below**, review the three STTM documents:

1. Download the STTM files and review their contents
2. Each has four sections: Cover Sheet, Version Control, Data Dictionary, and the STTM mapping itself
3. Note the key columns: `TARGET_TYPE` (Type 1, Type 2, Technical Field), `TRANSFORMATION_LOGIC`, `PII_FLAG`, and `KEY_TYPE`
4. DIM_PASSENGER is the only SCD Type 2 table — the others are simple Type 1 loads with technical columns
5. Upload the 3 STTMs to the current CoCo chat session window
""")

st.markdown("##### STTM Downloads")
_dl_cols = st.columns(3)
for _col, _fname in zip(_dl_cols, [
    "sttm_dim_flight.csv",
    "sttm_dim_passenger.csv",
    "sttm_fact_booking.csv",
]):
    _fpath = STTM_DIR / _fname
    _col.download_button(
        label=f":material/download: {_fname.replace('sttm_', '').replace('.csv', '').replace('_', ' ').upper()}",
        data=_fpath.read_bytes(),
        file_name=_fname,
        mime="text/csv",
        use_container_width=True,
    )

st.space("small")


PROMPT_3_1 = """Read the three STTM files: sttm_dim_flight.csv, sttm_dim_passenger.csv, sttm_fact_booking.csv.

Generate a dbt project called edw that implements these three GOLD tables:

1. Create mart models in AIRLINE_OPS_LABUSERXX.GOLD schema — one per STTM. Each reads directly from the AIRLINE_OPS_LABUSERXX source tables (dbt sources) and applies the mappings, casts, and transformation logic from the STTMs:
   - DIM_FLIGHT
   - DIM_PASSENGER
   - FACT_BOOKING
2. Project structure: models/marts/, dbt_project.yml, sources.yml (AIRLINE_OPS_LABUSERXX), profiles.yml.

Generate all files and show the complete project structure. Do not run the build or validate — we will do that interactively in the workspace using dbt commands."""

render_prompt("Prompt 3.1", "Generate dbt Project from STTMs", PROMPT_3_1)
st.warning(":material/edit: **Before executing in CoCo:** replace `XX` in the 3 occurrences of `LABUSERXX` in the prompt with your assigned lab user number.")
st.info(":material/terminal: Use the `dbt compile` and `dbt run` commands in the UI (bottom pane). If there are errors during the dbt run — click **Fix with CoCo** to fix them.")

render_explanation("What this prompt does", """
Generates a complete dbt project implementing the three STTM specifications:

```
edw/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── sources.yml              # AIRLINE_OPS_LABUSERXX replicated tables
│   └── marts/
│       ├── dim_flight.sql
│       ├── dim_passenger.sql
│       └── fact_booking.sql
```

Because the GOLD schema was configured with Iceberg defaults in Step 1, all three models are automatically materialized as Snowflake-managed Iceberg tables — no per-model config needed.

**DIM_PASSENGER SCD2 logic:**
- New records → INSERT with CURRENTFLAG='1', UPDATETYPE='INSERT'
- Changed records (TYPE1HASH mismatch) → expire old (set SCDENDDATETIME, CURRENTFLAG='0') + insert new version with UPDATETYPE='UPDATE'
- Deleted records → set DELETEDFLAG='1', UPDATETYPE='DELETE'

The STTM is the **contract** — CoCo translates it directly into executable dbt models.
""")


PROMPT_3_2 = """Generate a dbt test suite for DIM_PASSENGER based on its STTM (sttm_dim_passenger.csv):

1. Schema tests derived from the STTM columns (not_null, unique, accepted_values, relationships)
2. Custom SCD2 integrity tests: no overlapping date ranges, exactly one current record per passenger, hash consistency
3. PII-aware tests: verify masking policies on PII-flagged columns (NAME_PASSENGER, EMAIL)

Generate all test files."""

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


PROMPT_3_3 = """1. Run `dbt test` to execute all schema tests and custom DQ tests
2. Produce a consolidated summary report showing:
   - Total models built and their status (success/error)
   - Total tests run, passed, failed, and warned
   - For any failed tests: the test name, the model it applies to, and the number of failing rows
   - Row counts for each GOLD table: DIM_FLIGHT, DIM_PASSENGER, FACT_BOOKING
   - For DIM_PASSENGER: distinct PASSENGER_ID count and count of current active records (CURRENTFLAG='1')

3. If any tests fail, explain what the failures mean and suggest a fix
4. Confirm the GOLD tables are Iceberg tables (SHOW ICEBERG TABLES IN AIRLINE_OPS_LABUSERXX.GOLD) and show a sample of 5 rows from DIM_PASSENGER to verify the SCD2 structure

Execute and show the full report."""

render_prompt("Prompt 3.3", "Execute Tests & DQ Report", PROMPT_3_3)
st.warning(":material/edit: **Before executing in CoCo:** replace `XX` in `LABUSERXX` in the prompt with your assigned lab user number.")

render_explanation("What this prompt does", """
Runs the dbt tests and produces a quality report:

```
dbt test --project-dir edw
```

**Expected output:**
```
DQ Summary Report
=================
Models: 3 built (3 marts) | 0 errors
Tests:  12 passed | 0 failed | 0 warned

GOLD Layer (Iceberg tables in AIRLINE_OPS_LABUSERXX.GOLD):
  DIM_FLIGHT:     1,850 rows
  DIM_PASSENGER:  3,200 rows (2,980 current records)
  FACT_BOOKING:  12,400 rows

SHOW ICEBERG TABLES IN AIRLINE_OPS_LABUSERXX.GOLD → all 3 marts listed as Iceberg
```

This validates that:
- All STTM mappings were implemented correctly
- The SCD2 logic works (history versions and current records are consistent)
- No overlapping date ranges, exactly one current record per active passenger
- FK integrity holds (bookings reference real flights and passengers)
- The GOLD layer is materialized as Snowflake-managed Iceberg tables
""")


PROMPT_3_4 = """Add the following instruction to the AGENTS.md file:

When creating any new dbt model, always generate a corresponding schema test entry in a schema.yml file with the following baseline tests derived from the model's columns:

- not_null on every primary key and required column
- unique on primary key columns
- accepted_values on any column with a known set of valid values (e.g. status fields, flags, type indicators)
- relationships for any foreign key column, referencing the appropriate parent model and column

These tests should be generated automatically alongside the model — do not wait for a separate prompt to add them."""

render_prompt("Prompt 3.4", "Add default test generation rule to AGENTS.md", PROMPT_3_4)

render_explanation("What this prompt does", """
Adds a standing instruction to `AGENTS.md` so that CoCo automatically generates dbt schema tests every time it creates a new model — no separate prompt required.

After this, any model CoCo generates will come with a `schema.yml` entry including:
```yaml
models:
  - name: my_new_model
    columns:
      - name: MY_PK
        tests: [not_null, unique]
      - name: STATUS
        tests:
          - accepted_values:
              values: ['ACTIVE', 'INACTIVE']
      - name: PARENT_FK
        tests:
          - relationships:
              to: ref('parent_model')
              field: PARENT_PK
```

This ensures data quality testing is a **default behavior**, not an afterthought.
""")


render_key_concepts([
    {"term": "SCD Type 2", "definition": "A slowly changing dimension pattern that preserves full history. When a value changes, the current record is expired (SCDENDDATETIME set) and a new version is inserted. Enables point-in-time queries ('what was this passenger's tier on Jan 1?')."},
    {"term": "TYPE1HASH", "definition": "A SHA-256 hash computed over all Type 1 (overwritable) columns. Used for change detection: if the incoming hash differs from the existing hash, the record has changed and needs updating."},
    {"term": "Snowflake-Managed Iceberg Table", "definition": "An Iceberg table using Snowflake as the catalog and Snowflake-managed storage (EXTERNAL_VOLUME = SNOWFLAKE_MANAGED). Open format interoperability with zero external volume or IAM configuration."},
    {"term": "FK Lookups in Facts", "definition": "FACT_BOOKING resolves FLIGHT_KEY and PASSENGER_KEY by looking up the dimension surrogate keys from the source business keys — the standard pattern when facts reference dimensions by natural keys."},
    {"term": "STTM as Contract", "definition": "The STTM is not documentation — it's a specification. Every column, type, nullability, and transformation is defined. CoCo translates this contract directly into executable code."},
])

render_what_you_built([
    "dbt project (edw) implementing all 3 STTMs",
    "3 mart models in AIRLINE_OPS_LABUSERXX.GOLD as Snowflake-managed Iceberg tables",
    "DIM_PASSENGER with full SCD Type 2 logic (versioning, hash change detection, soft deletes)",
    "~12 data quality tests derived from STTM metadata",
    "Consolidated DQ summary report validating the GOLD layer",
], session_num=3)
