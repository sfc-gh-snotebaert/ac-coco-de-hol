import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built

render_session_header(1, "Environment Setup", "9:10 AM", "15 min", "Multi-layer database architecture, warehouse, and Openflow runtime verification")

render_technologies_used([
    {"name": "Multi-Layer Architecture", "description": "Separate databases for raw ingestion (RAW_AC) and curated warehouse (EDW_AC) enforce clear data ownership and access boundaries.", "icon": "layers"},
    {"name": "Openflow Runtime", "description": "Snowflake's managed connector platform for replicating data from external databases into Snowflake in near real-time.", "icon": "sync"},
    {"name": "Batch Control Pattern", "description": "An audit table tracking every ingestion batch: start/end time, row counts, and status. Essential for enterprise observability.", "icon": "fact_check"},
])


PROMPT_1_1 = """Create the following Snowflake objects for our Air Canada data engineering workshop:

1. A database called RAW_AC (this is the raw ingestion layer)
2. A schema called INGESTION inside RAW_AC
3. A database called EDW_AC (this is the curated warehouse layer)
4. Schemas called STAGING and MARTS inside EDW_AC
5. A warehouse called AC_DE_WH (size MEDIUM, auto-suspend after 60 seconds, auto-resume enabled)
6. Set the session context to use RAW_AC.INGESTION and the new warehouse

Execute all SQL and confirm each object was created."""

render_prompt("Prompt 1.1", "Create Databases, Schemas & Warehouse", PROMPT_1_1)

render_explanation("What this prompt does", """
Creates the multi-layer architecture:

```sql
-- Raw ingestion layer
CREATE DATABASE RAW_AC;
CREATE SCHEMA RAW_AC.INGESTION;

-- Curated warehouse layer
CREATE DATABASE EDW_AC;
CREATE SCHEMA EDW_AC.STAGING;
CREATE SCHEMA EDW_AC.MARTS;

-- Compute
CREATE WAREHOUSE AC_DE_WH
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;

USE DATABASE RAW_AC;
USE SCHEMA INGESTION;
USE WAREHOUSE AC_DE_WH;
```

**Why two databases?** Separating raw and curated data enforces clear boundaries: raw tables are append-only landing zones owned by the ingestion process, while EDW tables are governed, tested, and optimized for consumers.
""")


PROMPT_1_2 = """Verify that Openflow is available and ready on this account:

1. Show any existing Openflow runtimes
2. Show available Openflow connector types
3. If no runtime exists, create one called AC_OPENFLOW_RT using warehouse AC_DE_WH

Report what you find."""

render_prompt("Prompt 1.2", "Verify Openflow Readiness", PROMPT_1_2)

render_explanation("What this prompt does", """
Checks Openflow availability and creates the runtime if needed:

```sql
SHOW OPENFLOW RUNTIMES;
SHOW OPENFLOW CONNECTOR TYPES;

-- If no runtime exists:
CREATE OPENFLOW RUNTIME AC_OPENFLOW_RT
  WAREHOUSE = AC_DE_WH;
```

The **Openflow Runtime** is the compute engine that runs connectors. It manages the lifecycle of data replication jobs.
""")


PROMPT_1_3 = """In RAW_AC.INGESTION, create a batch control table called BATCH_CONTROL with the following columns:

- BATCH_ID (NUMBER, auto-increment, primary key)
- SOURCE_TABLE (VARCHAR, not null) — the source table name
- SOURCE_SYSTEM (VARCHAR, default 'POSTGRES') — identifies the source system
- BATCH_START_TS (TIMESTAMP_NTZ, not null) — when ingestion started
- BATCH_END_TS (TIMESTAMP_NTZ) — when ingestion completed
- ROWS_LOADED (NUMBER) — count of rows loaded in this batch
- STATUS (VARCHAR, not null) — one of: RUNNING, SUCCESS, FAILED
- ERROR_MESSAGE (VARCHAR) — error details if failed
- CREATED_BY (VARCHAR, default CURRENT_USER())

Also create a view called BATCH_SUMMARY that shows the latest batch per source table with its status and row count.

Execute all SQL."""

render_prompt("Prompt 1.3", "Create Batch Control & Audit", PROMPT_1_3)

render_explanation("What this prompt does", """
Creates the observability foundation for enterprise pipelines:

```sql
CREATE TABLE RAW_AC.INGESTION.BATCH_CONTROL (
    BATCH_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    SOURCE_TABLE VARCHAR NOT NULL,
    SOURCE_SYSTEM VARCHAR DEFAULT 'POSTGRES',
    BATCH_START_TS TIMESTAMP_NTZ NOT NULL,
    BATCH_END_TS TIMESTAMP_NTZ,
    ROWS_LOADED NUMBER,
    STATUS VARCHAR NOT NULL,
    ERROR_MESSAGE VARCHAR,
    CREATED_BY VARCHAR DEFAULT CURRENT_USER()
);

CREATE VIEW RAW_AC.INGESTION.BATCH_SUMMARY AS
SELECT SOURCE_TABLE, STATUS, ROWS_LOADED, BATCH_END_TS
FROM BATCH_CONTROL
QUALIFY ROW_NUMBER() OVER (PARTITION BY SOURCE_TABLE ORDER BY BATCH_ID DESC) = 1;
```

**Why batch control?** In enterprise environments, you need to answer: "When did this data arrive? How many rows? Did it succeed?" This table provides that audit trail.
""")


render_key_concepts([
    {"term": "Multi-Layer Architecture", "definition": "A design pattern separating raw (landing), staging (cleaned), and marts (business-ready) layers. Each layer has distinct ownership, quality expectations, and access controls."},
    {"term": "Openflow Runtime", "definition": "The managed compute environment that executes Openflow connectors. It runs within SPCS (Snowpark Container Services) and handles scheduling, retries, and monitoring."},
    {"term": "Batch Control", "definition": "An operational metadata table that records every data load operation. Used for debugging failures, measuring freshness, and proving data lineage to auditors."},
])

render_what_you_built([
    "RAW_AC database with INGESTION schema (raw landing zone)",
    "EDW_AC database with STAGING and MARTS schemas (curated layer)",
    "AC_DE_WH warehouse (Medium, auto-suspend 60s)",
    "Openflow runtime verified and ready",
    "BATCH_CONTROL table and BATCH_SUMMARY view for audit",
])
