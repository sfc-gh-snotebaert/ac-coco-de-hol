import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built

render_session_header(2, "Enterprise Ingestion with Openflow", "{{TIME_SESSION_2}}", "{{DUR_SESSION_2}}", "Openflow connector replicating Postgres → Iceberg tables with enterprise naming and audit columns")

render_technologies_used([
    {"name": "Openflow Connectors", "description": "Managed CDC connectors that replicate data from external databases (Postgres, MySQL, SQL Server) into Snowflake with minimal configuration.", "icon": "cable"},
    {"name": "Apache Iceberg Tables", "description": "Open table format providing ACID transactions, time travel, and schema evolution. Iceberg tables in Snowflake are interoperable with other engines.", "icon": "table_view"},
    {"name": "Enterprise Naming Standards", "description": "Consistent naming conventions (uppercase, standardized prefixes, audit columns) ensure discoverability and governance at scale.", "icon": "label"},
])


PROMPT_2_1 = """In RAW_AC.INGESTION, I need to connect to an external Postgres database and replicate its tables into Snowflake.

Source database connection details:
- Host: {{SOURCE_HOST}}
- Port: {{SOURCE_PORT}}
- Database: {{SOURCE_DB}}
- Schemas to replicate: {{SOURCE_SCHEMA_LIST}}
- Username: {{SOURCE_USER}}
- Password: {{SOURCE_PASSWORD}}

Using Openflow:
1. Create a secret to store the source database credentials
2. Create an Openflow connector called AC_POSTGRES_CONNECTOR that connects to this Postgres source
3. Configure it to replicate all tables from the schemas listed above into RAW_AC.INGESTION
4. Apply this naming convention: source table names should be converted to UPPERCASE (e.g., source `reservations.bookings` becomes target `BOOKINGS`)

Execute all SQL and show the connector configuration."""

render_prompt("Prompt 2.1", "Create Openflow Connector to Postgres", PROMPT_2_1)

render_explanation("What this prompt does", """
Creates the connection from Snowflake to the source Postgres database:

```sql
-- Store credentials securely
CREATE SECRET RAW_AC.INGESTION.POSTGRES_CREDENTIALS
  TYPE = PASSWORD
  USERNAME = '{{SOURCE_USER}}'
  PASSWORD = '{{SOURCE_PASSWORD}}';

-- Create the Openflow connector
CREATE OPENFLOW CONNECTOR AC_POSTGRES_CONNECTOR
  RUNTIME = {{OPENFLOW_RUNTIME}}
  SOURCE = POSTGRES
  CONNECTION = (
    HOST = '{{SOURCE_HOST}}',
    PORT = {{SOURCE_PORT}},
    DATABASE = '{{SOURCE_DB}}'
  )
  CREDENTIALS = RAW_AC.INGESTION.POSTGRES_CREDENTIALS
  TARGET_DATABASE = 'RAW_AC'
  TARGET_SCHEMA = 'INGESTION';
```

**Key points:**
- Credentials are stored as a Snowflake Secret (never in plain text in connector config)
- The connector runs on the Openflow Runtime created in Session 1
- Target naming is standardized: all table names in UPPERCASE
""")


PROMPT_2_2 = """Now I need to configure the Iceberg tables for the replicated data. For each source table that Openflow will replicate:

Source tables:
- reservations.bookings (PNR, booking_date, flight_id, passenger_id, fare_class, status, total_amount)
- reservations.passengers (passenger_id, first_name, last_name, email, loyalty_tier, home_airport)
- flight_ops.flights (flight_id, flight_number, origin, destination, departure_ts, arrival_ts, aircraft_id, status)
- flight_ops.airports (iata_code, airport_name, city, country, timezone)
- maintenance.work_orders (work_order_id, aircraft_id, work_type, scheduled_date, completed_date, status, description)
- loyalty.aeroplan_txns (txn_id, passenger_id, txn_date, points, txn_type, description)

For each table:
1. Create it as an Iceberg table in RAW_AC.INGESTION with the name in UPPERCASE
2. Map the Postgres column types to appropriate Snowflake types
3. Add three audit columns to every table: _LOADED_AT (TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()), _BATCH_ID (NUMBER), _SOURCE_SYSTEM (VARCHAR DEFAULT 'POSTGRES')
4. Include a comment on each table describing its source

Execute all SQL and show confirmation for each table."""

render_prompt("Prompt 2.2", "Create Iceberg Tables with Audit Columns", PROMPT_2_2)

render_explanation("What this prompt does", """
Creates Iceberg-format tables in the ingestion layer with enterprise standards:

```sql
CREATE ICEBERG TABLE RAW_AC.INGESTION.BOOKINGS (
    PNR VARCHAR,
    BOOKING_DATE DATE,
    FLIGHT_ID NUMBER,
    PASSENGER_ID NUMBER,
    FARE_CLASS VARCHAR,
    STATUS VARCHAR,
    TOTAL_AMOUNT NUMBER(10,2),
    -- Audit columns (added to every table)
    _LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _BATCH_ID NUMBER,
    _SOURCE_SYSTEM VARCHAR DEFAULT 'POSTGRES'
)
  CATALOG = 'SNOWFLAKE'
  EXTERNAL_VOLUME = '...'
  BASE_LOCATION = 'raw_ac/ingestion/bookings/'
  COMMENT = 'Source: {{SOURCE_DB}}.reservations.bookings';
```

**Why Iceberg?**
- Open format: data is readable by Spark, Trino, Flink — not locked into Snowflake
- Time travel and schema evolution built-in
- Efficient partition pruning for large datasets

**Why audit columns?**
- `_LOADED_AT`: When did this row arrive? (freshness tracking)
- `_BATCH_ID`: Which batch loaded it? (links to BATCH_CONTROL)
- `_SOURCE_SYSTEM`: Where did it come from? (lineage)
""")


PROMPT_2_3 = """Start the Openflow connector AC_POSTGRES_CONNECTOR to begin replicating data:

1. Start the connector
2. Monitor its progress — wait until the initial load completes for all tables
3. Once complete, insert a record into RAW_AC.INGESTION.BATCH_CONTROL for each table with:
   - SOURCE_TABLE = the table name
   - BATCH_START_TS = the connector start time
   - BATCH_END_TS = now
   - ROWS_LOADED = the actual row count loaded
   - STATUS = 'SUCCESS'
4. Show the BATCH_SUMMARY view to confirm all tables loaded successfully
5. Show row counts for all tables in RAW_AC.INGESTION (excluding BATCH_CONTROL)

Execute and report the results."""

render_prompt("Prompt 2.3", "Start Ingestion & Record Batch Audit", PROMPT_2_3)

render_explanation("What this prompt does", """
Starts the replication and records the results:

```sql
-- Start the connector
ALTER OPENFLOW CONNECTOR AC_POSTGRES_CONNECTOR RESUME;

-- Monitor progress
SHOW OPENFLOW CONNECTOR STATUS AC_POSTGRES_CONNECTOR;

-- Record batch results (for each table)
INSERT INTO RAW_AC.INGESTION.BATCH_CONTROL
  (SOURCE_TABLE, BATCH_START_TS, BATCH_END_TS, ROWS_LOADED, STATUS)
SELECT 'BOOKINGS', <start_ts>, CURRENT_TIMESTAMP(), COUNT(*), 'SUCCESS'
FROM RAW_AC.INGESTION.BOOKINGS;

-- Verify
SELECT * FROM RAW_AC.INGESTION.BATCH_SUMMARY;

-- Row counts
SELECT TABLE_NAME, ROW_COUNT
FROM RAW_AC.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'INGESTION'
  AND TABLE_NAME != 'BATCH_CONTROL'
ORDER BY ROW_COUNT DESC;
```

At this point you have a fully operational ingestion pipeline with:
- Live CDC from Postgres
- Enterprise naming standards
- Complete audit trail in BATCH_CONTROL
""")


render_key_concepts([
    {"term": "CDC (Change Data Capture)", "definition": "A technique that captures row-level changes (inserts, updates, deletes) from a source database and applies them to a target. Openflow uses the Postgres WAL (Write-Ahead Log) for this."},
    {"term": "Iceberg Table Format", "definition": "An open table format that stores data in Parquet files with a metadata layer tracking snapshots, schema, and partitions. Enables time travel, schema evolution, and engine-agnostic access."},
    {"term": "Audit Columns", "definition": "Metadata columns added to every table (_LOADED_AT, _BATCH_ID, _SOURCE_SYSTEM) that answer 'when, how, and from where' for every row. Non-negotiable in enterprise data platforms."},
    {"term": "Openflow Connector", "definition": "A managed replication job that handles connection, schema detection, initial load, and ongoing CDC. Runs on the Openflow Runtime within Snowflake."},
])

render_what_you_built([
    "Openflow connector to Postgres source (AC_POSTGRES_CONNECTOR)",
    "{{NUM_SOURCE_TABLES}} Iceberg tables with enterprise naming (UPPERCASE)",
    "Audit columns on every table (_LOADED_AT, _BATCH_ID, _SOURCE_SYSTEM)",
    "Batch control records with row counts and status",
    "End-to-end audit trail from source to landing zone",
])
