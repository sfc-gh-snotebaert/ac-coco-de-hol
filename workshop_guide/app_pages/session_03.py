import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built

render_session_header(3, "EDW Pipeline from STTM with dbt", "{{TIME_SESSION_3}}", "{{DUR_SESSION_3}}", "dbt project generated from an enterprise STTM with SCD Type 1/2, hash-based change detection, and data quality tests")

render_technologies_used([
    {"name": "dbt (Data Build Tool)", "description": "A SQL-first transformation framework. Models are SELECT statements; dbt handles DDL, dependencies, testing, and documentation.", "icon": "build_circle"},
    {"name": "Source-to-Target Mapping (STTM)", "description": "An enterprise specification defining column mappings, SCD types, transformation logic, PII flags, and data sensitivity — the contract between analysts and engineers.", "icon": "map"},
    {"name": "SCD Type 1 & 2", "description": "Slowly Changing Dimension patterns. Type 1 overwrites history (current value only). Type 2 preserves history with effective date ranges.", "icon": "history"},
])

st.markdown("""
**Before running the prompts below**, review the STTM document:

1. Download the STTM: [{{STTM_FILENAME}}]({{STTM_DOWNLOAD_URL}})
2. Review its structure — it has four sections: Cover Sheet, Version Control, Data Dictionary, and the STTM mapping itself
3. Note the key columns: `TARGET_TYPE` (Type 1, Type 2, Technical Field), `TRANSFORMATION_LOGIC`, `PII_FLAG`, and `KEY_TYPE`
4. You will paste the full STTM content into the first prompt below
""")

st.space("small")


PROMPT_3_1 = """I have an enterprise Source-to-Target Mapping (STTM) document that defines DIM_CUSTOMER for our EDW. Here it is:

```
{{STTM_CONTENT}}
```

Using this STTM, generate a dbt project called {{DBT_PROJECT_NAME}} that implements the DIM_CUSTOMER table with full SCD Type 2 logic:

1. Create a staging model `stg_customer_master` in EDW_AC.STAGING that:
   - SELECTs from the source table DIM_CUSTOMER_MASTER in RAW_AC.INGESTION
   - Applies the column mappings and type casts from the STTM
   - Computes TYPE1HASH using SHA2(CONCAT_WS('|', ...)) over all Type 1 columns as defined in the STTM

2. Create the mart model `dim_customer` in EDW_AC.MARTS that implements:
   - SCD Type 2 logic with SCDSTARTDATETIME / SCDENDDATETIME
   - CURRENTFLAG to identify the active record
   - TYPE1HASH for change detection (compare incoming vs existing to detect updates)
   - LATEARRIVINGFLAG handling
   - DELETEDFLAG for soft deletes
   - CREATEDBATCHLOGID / UPDATEDBATCHLOGID tracking
   - UPDATETYPE column ('INSERT', 'UPDATE', 'DELETE')
   - DIM_CUSTOMER_KEY as autoincrement surrogate key

3. Use the dbt project structure: models/staging/, models/marts/, dbt_project.yml, sources.yml, and a profiles.yml connecting to EDW_AC

Generate all SQL model files and project configuration. Show the complete project structure and SQL for each model."""

render_prompt("Prompt 3.1", "Generate dbt Project from STTM", PROMPT_3_1)

render_explanation("What this prompt does", """
Generates a complete dbt project implementing the STTM specification:

```
{{DBT_PROJECT_NAME}}/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── sources.yml
│   ├── staging/
│   │   └── stg_customer_master.sql
│   └── marts/
│       └── dim_customer.sql
```

**Staging model** — standardizes the source and computes the change detection hash:
```sql
-- models/staging/stg_customer_master.sql
SELECT
    CUSTOMER_NUMBER,
    NAME_CUSTOMER,
    IDENTIFICATION_LEGACY_NUMBER,
    COUNTRY,
    TAX_NUMBER,
    TAX_CATEGORY,
    SHA2(CONCAT_WS('|',
        COALESCE(CUSTOMER_NUMBER, ''),
        COALESCE(NAME_CUSTOMER, ''),
        COALESCE(IDENTIFICATION_LEGACY_NUMBER, ''),
        COALESCE(COUNTRY, ''),
        COALESCE(TAX_NUMBER, ''),
        COALESCE(TAX_CATEGORY, '')
    ), 256) AS TYPE1HASH
FROM {{ source('raw_ac', 'DIM_CUSTOMER_MASTER') }}
WHERE _BATCH_ID IS NOT NULL
```

**Mart model** — implements the full SCD Type 2 MERGE pattern:
```sql
-- models/marts/dim_customer.sql (incremental with merge)
{% set config = {
    'materialized': 'incremental',
    'unique_key': 'DIM_CUSTOMER_KEY',
    'merge_update_columns': ['SCDENDDATETIME', 'CURRENTFLAG', ...]
} %}

-- Detects changes via TYPE1HASH comparison:
-- New records → INSERT with CURRENTFLAG='1', UPDATETYPE='INSERT'
-- Changed records → expire old (set SCDENDDATETIME, CURRENTFLAG='0')
--                   + insert new version with UPDATETYPE='UPDATE'
-- Deleted records → set DELETEDFLAG='1', UPDATETYPE='DELETE'
```

The STTM is the **contract** — Cortex Code translates it directly into executable dbt models.
""")


PROMPT_3_2 = """For the {{DBT_PROJECT_NAME}} dbt project, generate a comprehensive test suite based on the STTM metadata:

1. Schema tests (in schema.yml files) derived from the STTM:
   - DIM_CUSTOMER_KEY: not_null + unique (it's the PK per KEY_TYPE)
   - CUSTOMER_NUMBER: not_null + unique (it's the AK — alternate/business key)
   - All columns marked TARGET_NULLABLE = 'No': not_null tests
   - CURRENTFLAG: accepted_values ['0', '1']
   - DELETEDFLAG: accepted_values ['0', '1']
   - LATEARRIVINGFLAG: accepted_values ['Y', 'N']
   - UPDATETYPE: accepted_values ['INSERT', 'UPDATE', 'DELETE']

2. Custom data quality tests (in tests/ folder):
   - scd_no_overlapping_versions: For any CUSTOMER_NUMBER, date ranges (SCDSTARTDATETIME to SCDENDDATETIME) must not overlap
   - exactly_one_current_record: Every CUSTOMER_NUMBER with DELETEDFLAG='0' must have exactly one record with CURRENTFLAG='1'
   - hash_integrity: TYPE1HASH must match the recomputed SHA2 of the Type 1 columns (detect drift/corruption)
   - batch_log_consistency: UPDATEDBATCHLOGID must be >= CREATEDBATCHLOGID

3. PII-aware tests (derived from PII_FLAG column in STTM):
   - Verify that columns flagged as PII (NAME_CUSTOMER, TAX_NUMBER) have masking policies applied

Generate all test files and show me the complete test configuration."""

render_prompt("Prompt 3.2", "Generate dbt Tests from STTM Metadata", PROMPT_3_2)

render_explanation("What this prompt does", """
Creates tests derived directly from the STTM metadata — not guesswork:

**Schema tests** (in `models/marts/schema.yml`):
```yaml
models:
  - name: dim_customer
    columns:
      - name: DIM_CUSTOMER_KEY
        tests:
          - not_null
          - unique
      - name: CUSTOMER_NUMBER
        tests:
          - not_null
          - unique:
              where: "CURRENTFLAG = '1' AND DELETEDFLAG = '0'"
      - name: CURRENTFLAG
        tests:
          - not_null
          - accepted_values:
              values: ['0', '1']
      - name: UPDATETYPE
        tests:
          - not_null
          - accepted_values:
              values: ['INSERT', 'UPDATE', 'DELETE']
```

**Custom SCD integrity tests** (in `tests/`):
```sql
-- tests/scd_no_overlapping_versions.sql
SELECT a.CUSTOMER_NUMBER, a.SCDSTARTDATETIME, a.SCDENDDATETIME
FROM {{ ref('dim_customer') }} a
JOIN {{ ref('dim_customer') }} b
  ON a.CUSTOMER_NUMBER = b.CUSTOMER_NUMBER
  AND a.DIM_CUSTOMER_KEY != b.DIM_CUSTOMER_KEY
  AND a.SCDSTARTDATETIME < COALESCE(b.SCDENDDATETIME, '9999-12-31')
  AND b.SCDSTARTDATETIME < COALESCE(a.SCDENDDATETIME, '9999-12-31')
```

The key insight: **the STTM itself tells you what to test.** PK columns get uniqueness tests, nullable flags drive not_null tests, SCD metadata drives temporal integrity tests.
""")


PROMPT_3_3 = """Now execute the dbt project and produce a data quality report:

1. Run `dbt run` to build the staging and mart models in EDW_AC
2. Run `dbt test` to execute all schema tests and custom DQ tests
3. Produce a summary report showing:
   - Total models built and their status (success/error)
   - Total tests run, passed, failed, and warned
   - For any failed tests: the test name, the model it applies to, and the number of failing rows
   - DIM_CUSTOMER row count, distinct CUSTOMER_NUMBER count, and count of current active records (CURRENTFLAG='1')

4. If any tests fail, explain what the failures mean and suggest a fix
5. Show a sample of 5 rows from DIM_CUSTOMER to verify the SCD2 structure looks correct

Execute and show the full report."""

render_prompt("Prompt 3.3", "Execute Pipeline & DQ Report", PROMPT_3_3)

render_explanation("What this prompt does", """
Runs the full dbt pipeline and produces a quality report:

```
dbt run --project-dir {{DBT_PROJECT_NAME}}
dbt test --project-dir {{DBT_PROJECT_NAME}}
```

**Expected output:**
```
DQ Summary Report
=================
Models: 2 built (1 staging + 1 mart) | 0 errors
Tests:  12 passed | 0 failed | 0 warned

DIM_CUSTOMER Stats:
  Total rows:              28,450
  Distinct customers:      24,200
  Current active records:  23,800
  Historical versions:      4,250
  Soft-deleted:               400
```

This validates that:
- The SCD2 logic is working (historical versions exist)
- Hash-based change detection is functioning
- No overlapping date ranges
- Exactly one current record per active customer
""")


render_key_concepts([
    {"term": "SCD Type 2", "definition": "A slowly changing dimension pattern that preserves full history. When a value changes, the current record is expired (SCDENDDATETIME set) and a new version is inserted. Enables point-in-time queries ('what was this customer's country on Jan 1?')."},
    {"term": "TYPE1HASH", "definition": "A SHA-256 hash computed over all Type 1 (overwritable) columns. Used for change detection: if the incoming hash differs from the existing hash, the record has changed and needs updating."},
    {"term": "Surrogate Key", "definition": "An artificial primary key (DIM_CUSTOMER_KEY) with no business meaning. Enables SCD2 by allowing multiple versions of the same business entity (CUSTOMER_NUMBER) to coexist."},
    {"term": "Late-Arriving Dimension", "definition": "When a fact record arrives referencing a dimension member that doesn't exist yet. LATEARRIVINGFLAG marks placeholder records that will be updated when the real dimension data arrives."},
    {"term": "STTM as Contract", "definition": "The STTM is not documentation — it's a specification. Every column, type, nullability, and transformation is defined. Cortex Code translates this contract directly into executable code."},
])

render_what_you_built([
    "dbt project ({{DBT_PROJECT_NAME}}) implementing DIM_CUSTOMER from STTM",
    "Staging model with hash-based change detection",
    "Mart model with full SCD Type 2 logic (versioning, expiry, soft deletes)",
    "~12 data quality tests derived from STTM metadata (schema + custom SCD integrity)",
    "DQ summary report validating SCD2 correctness",
])
