import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built

render_session_header(2, "Create Openflow Postgres Connector", "9:15 AM", "30 min", "Gen2 Postgres CDC connector replicating airline_ops into AIRLINE_OPS via Openflow")

render_technologies_used([
    {"name": "Openflow Gen2 Connectors", "description": "Managed CDC connectors that replicate data from external databases (Postgres, MySQL, SQL Server) into Snowflake with minimal configuration.", "icon": "cable"},
    {"name": "Postgres CDC (WAL)", "description": "Change Data Capture that reads the Postgres write-ahead log through a publication, delivering inserts, updates, and deletes with low latency.", "icon": "podcasts"},
    {"name": "Credential Management", "description": "Source credentials are read from PG_SETUP.CONFIG.PG_INSTANCE_INFO and stored as a Snowflake Secret — never hard-coded in connector configuration.", "icon": "key"},
])


PROMPT_2_1 = """Add a Gen2 Postgres connector named PG_CDC_CONNECTOR to RUNTIME_PG.

The Postgres instance information is in PG_SETUP.CONFIG.PG_INSTANCE_INFO table.
Use the snowflake_admin credentials.

The Postgres database to connect is airline_ops and the schemas to replicate are flight_ops and reservations.

The publication name is openflow_pub. The target Snowflake database is AIRLINE_OPS.

After creating the connector:
1. Start the connector
2. Monitor its progress and wait until the initial load completes for all tables
3. Show the row counts of all replicated tables in AIRLINE_OPS

Execute all SQL and report the results."""

render_prompt("Prompt 2.1", "Create & Start the PG_CDC_CONNECTOR", PROMPT_2_1)

render_explanation("What this prompt does", """
Creates the CDC pipeline from Postgres into Snowflake:

```sql
-- 1. Store the source credentials (read from PG_SETUP.CONFIG.PG_INSTANCE_INFO)
CREATE OR REPLACE SECRET OPENFLOW_DB.RUNTIME.PG_CREDENTIALS
  TYPE = PASSWORD
  USERNAME = 'snowflake_admin'
  PASSWORD = '<from PG_INSTANCE_INFO>';

-- 2. Create the Gen2 Postgres connector on the pre-provisioned runtime
CREATE OPENFLOW CONNECTOR OPENFLOW_DB.RUNTIME.PG_CDC_CONNECTOR
  RUNTIME = OPENFLOW_DB.RUNTIME.RUNTIME_PG
  SOURCE = POSTGRES
  CONNECTION = (
    HOST = '<host:port from PG_INSTANCE_INFO>',
    DATABASE = 'airline_ops'
  )
  CREDENTIALS = OPENFLOW_DB.RUNTIME.PG_CREDENTIALS
  REPLICATION = (
    SCHEMAS = ('flight_ops', 'reservations'),
    PUBLICATION = 'openflow_pub'
  )
  TARGET_DATABASE = 'AIRLINE_OPS';

-- 3. Start replication and monitor
ALTER OPENFLOW CONNECTOR OPENFLOW_DB.RUNTIME.PG_CDC_CONNECTOR RESUME;
SELECT * FROM TABLE(SHOW_OPENFLOW_CONNECTOR_STATUS('OPENFLOW_DB.RUNTIME.PG_CDC_CONNECTOR'));

-- 4. Verify the landing zone
SELECT TABLE_SCHEMA, TABLE_NAME, ROW_COUNT
FROM AIRLINE_OPS.INFORMATION_SCHEMA.TABLES
ORDER BY TABLE_SCHEMA, TABLE_NAME;
```

**Key points:**
- The connector runs on `RUNTIME_PG` (verified in Session 1) inside `DEPLOYMENT_DEV`
- Credentials come from `PG_SETUP.CONFIG.PG_INSTANCE_INFO` — the same table you reviewed in Prompt 1.1
- The publication `openflow_pub` was created on the source; the connector subscribes to it for CDC
- The runtime role was already granted `CREATE TABLE` on `AIRLINE_OPS.RESERVATIONS` and `AIRLINE_OPS.FLIGHT_OPS`, so the connector can create its target tables automatically

Once the initial load completes, AIRLINE_OPS contains live replicated copies of `airports`, `flights`, `passengers`, and `bookings` — and stays in sync as the source changes.
""")


render_key_concepts([
    {"term": "CDC (Change Data Capture)", "definition": "A technique that captures row-level changes (inserts, updates, deletes) from a source database and applies them to a target. Openflow's Postgres connector reads the write-ahead log (WAL) through a publication for low-latency replication."},
    {"term": "Publication (openflow_pub)", "definition": "A Postgres publication defines which tables are exposed for logical replication. The connector subscribes to the publication to receive change events from the WAL."},
    {"term": "Snowflake Secret", "description": "A first-class Snowflake object that stores credentials securely. Connector configuration references the secret — no plain-text passwords in DDL."},
    {"term": "Connector Lifecycle", "definition": "CREATE → RESUME → monitor initial load → continuous CDC. The connector manages table creation, schema changes, and error recovery automatically within the target schemas."},
])

render_what_you_built([
    "PG_CDC_CONNECTOR on RUNTIME_PG (Gen2 Postgres CDC)",
    "Credentials stored as a Snowflake Secret from PG_INSTANCE_INFO values",
    "Live replication of flight_ops and reservations schemas into AIRLINE_OPS",
    "4 replicated tables: AIRPORTS, FLIGHTS, PASSENGERS, BOOKINGS",
    "Continuous CDC from the airline_ops source via the openflow_pub publication",
])
