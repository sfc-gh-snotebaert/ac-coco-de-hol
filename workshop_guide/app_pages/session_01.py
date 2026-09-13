import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built

render_session_header(1, "Review Current Configuration", "9:10 AM", "15 min", "Explore the pre-provisioned Snowflake objects and verify the Openflow deployment and runtime are ready")

render_technologies_used([
    {"name": "Snowflake Account Objects", "description": "Databases, schemas, and tables that have been pre-provisioned for this workshop: AIRLINE_OPS (CDC destination) and PG_SETUP (source database connection details).", "icon": "inventory_2"},
    {"name": "Openflow Deployments", "description": "The account-level container that hosts Openflow runtimes and connectors. Deployments manage the compute infrastructure for data replication.", "icon": "deployed_code"},
    {"name": "Openflow Runtimes", "description": "The managed compute engine (SPCS-based) that executes Openflow connectors. It handles scheduling, retries, and monitoring of replication jobs.", "icon": "sync"},
])


PROMPT_1_1 = """Review the current objects in the account:

1. Show the schemas and tables in the AIRLINE_OPS database
2. Show the schemas and tables in the PG_SETUP database
3. Show the contents of PG_SETUP.CONFIG.PG_INSTANCE_INFO

Report what you find."""

render_prompt("Prompt 1.1", "Review Pre-Provisioned Objects", PROMPT_1_1)

render_explanation("What this prompt does", """
Explores the two databases that have been pre-provisioned for this workshop:

```sql
-- CDC destination (currently empty schemas)
SHOW SCHEMAS IN DATABASE AIRLINE_OPS;
SHOW TABLES IN SCHEMA AIRLINE_OPS.RESERVATIONS;
SHOW TABLES IN SCHEMA AIRLINE_OPS.FLIGHT_OPS;

-- Source database connection details
SHOW SCHEMAS IN DATABASE PG_SETUP;
SELECT * FROM PG_SETUP.CONFIG.PG_INSTANCE_INFO;
```

**What you should see:**
- `AIRLINE_OPS` — an empty database with `RESERVATIONS` and `FLIGHT_OPS` schemas. The Openflow connector will create and populate the tables here.
- `PG_SETUP` — the `CONFIG.PG_INSTANCE_INFO` table holding the Postgres instance host and access role credentials (including the `snowflake_admin` user) for the PG1 instance running the `airline_ops` database.

**Why review first?** Before creating a connector, always confirm the destination is empty (no name collisions) and you know where the source credentials live. This is the same discipline you'd apply in a real production deployment.
""")


PROMPT_1_2 = """Review the Openflow deployment and runtime configuration on this account:

1. Show all Openflow deployments and their status
2. Show all Openflow runtimes and their status (deployment, node type, role)
3. Show any existing Openflow connectors

Report what you find."""

render_prompt("Prompt 1.2", "Verify Openflow Deployment & Runtime", PROMPT_1_2)

render_explanation("What this prompt does", """
Verifies the Openflow infrastructure that the connector will run on:

```sql
SHOW OPENFLOW DEPLOYMENTS;
SHOW OPENFLOW RUNTIMES;
SHOW OPENFLOW CONNECTORS;
```

**What you should see:**
- `DEPLOYMENT_DEV` — an active Snowflake-type Openflow deployment
- `OPENFLOW_DB.RUNTIME.RUNTIME_PG` — an active runtime in DEPLOYMENT_DEV, executing as `OPENFLOW_RUNTIME_PG_ROLE` with the Postgres external access integration attached
- **No connectors yet** — the `PG_CDC_CONNECTOR` is created in the next session

**Key concepts:**
- The **deployment** hosts the Openflow control plane and event table
- The **runtime** is the SPCS compute engine that runs connector jobs; its external access integration whitelists the Postgres host so the connector can reach PG1 over the network

If the deployment or runtime is not active, notify the workshop facilitator before continuing.
""")


render_key_concepts([
    {"term": "Openflow Deployment", "definition": "The account-level container for Openflow objects. It manages the event table (telemetry) and hosts runtimes. Our lab uses DEPLOYMENT_DEV, pre-provisioned on each account."},
    {"term": "Openflow Runtime", "definition": "A SPCS-based compute pool managed by Openflow that executes connector replication jobs. RUNTIME_PG is pre-provisioned with network egress to the PG1 Postgres instance."},
    {"term": "CDC Destination", "definition": "The AIRLINE_OPS database with empty RESERVATIONS and FLIGHT_OPS schemas. The Openflow connector creates and continuously populates tables here from the source Postgres."},
    {"term": "PG_SETUP.CONFIG.PG_INSTANCE_INFO", "definition": "Configuration table holding the PG1 instance connection details: host/port and access role credentials (application and snowflake_admin users). The connector prompt reads credentials from here."},
])

render_what_you_built([
    "Confirmed AIRLINE_OPS destination is empty and ready for CDC",
    "Located PG1 connection details in PG_SETUP.CONFIG.PG_INSTANCE_INFO",
    "Verified DEPLOYMENT_DEV is active",
    "Verified RUNTIME_PG is active with the correct role and network access",
    "Confirmed no connector exists yet (created in Session 2)",
])
