# CoCo Hands-On Lab — Data Engineering Template

This is the generic template for generating city/domain-specific CoCo Data Engineering workshop labs. Each workshop is a Streamlit app that guides attendees through 5 sessions building an enterprise data pipeline on Snowflake using Openflow, dbt, and AI-assisted code review.

## Workshop Structure

| Session | Topic | What's Built |
|---------|-------|--------------|
| 1 | Environment Setup | Multi-layer databases (RAW/EDW), warehouse, Openflow runtime, batch control |
| 2 | Enterprise Ingestion with Openflow | Openflow connector → Iceberg tables with audit columns and naming standards |
| 3 | EDW Pipeline from STTM with dbt | dbt project from STTM, staging + mart models, SCD Type 2, DQ tests |
| 4 | Code Review & Optimization | SQL anti-pattern scan, query profile analysis, clustering recommendations |
| 5 | Data Engineer Skill (Stretch) | Reusable CoCo skill packaging the code review workflow |

## Template Variables

All files use `{{VARIABLE_NAME}}` placeholders. When generating a new workshop, replace these with city/domain-specific values.

### Core Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `WORKSHOP_TITLE` | Main title | Air Canada Data Engineering Workshop |
| `WORKSHOP_SUBTITLE` | Subtitle line | Building Enterprise Pipelines with CoCo |
| `PAGE_ICON` | Streamlit page icon | `:material/engineering:` |
| `SCENARIO_DESCRIPTION` | 2-3 sentence scenario intro | Air Canada's operational systems run on legacy Postgres... |
| `DURATION` | Total workshop time | 2.5 hrs |

### Event Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `EVENT_DATE` | Date string | September 16, 2026 |
| `EVENT_TIME_RANGE` | Time range | 9:00 AM to 11:00 AM |
| `VENUE_NAME` | Venue name | Air Canada Office |
| `VENUE_CITY` | City/province | Montreal, QC |
| `SIGNUP_LINK` | Trial signup URL with tracking | No Link Provided |
| `RECOMMENDED_REGION` | AWS region suggestion | AWS Canada (Central) |

### Schedule Variables

| Variable | Description |
|----------|-------------|
| `TIME_ARRIVAL` | Arrival time slot |
| `TIME_WELCOME` | Welcome slot |
| `TIME_SESSION_1` through `TIME_SESSION_5` | Session time ranges |
| `TIME_BREAK` | Break time |
| `DUR_SESSION_1` through `DUR_SESSION_5` | Session durations |

### Infrastructure Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `WAREHOUSE_NAME` | Snowflake warehouse | COMPUTE_WH |
| `OPENFLOW_RUNTIME` | Openflow runtime name | RUNTIME_PG |

### Source Database Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SOURCE_HOST` | Postgres hostname | Details in PG_SETUP.CONFIG.PG_INSTANCE_INFO |
| `SOURCE_PORT` | Postgres port | 5432 |
| `SOURCE_DB` | Source database name | airline_ops |
| `SOURCE_SCHEMA_LIST` | Schemas to replicate | reservations, flight_ops |
| `SOURCE_USER` | Source DB username | snowflake_admin |
| `SOURCE_PASSWORD` | Source DB password | DBA_PASSWORD column in PG_SETUP.CONFIG.PG_INSTANCE_INFO|
| `NUM_SOURCE_TABLES` | Number of source tables | 4 |

### STTM & dbt Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `STTM_FILENAME` | STTM file name | sttm_dim_customer.csv |
| `STTM_DOWNLOAD_URL` | URL to download the STTM | https://github.com/.../sttm_dim_customer.csv |
| `STTM_CONTENT` | Full STTM document content (pasted into prompt) | (CSV content) |
| `DBT_PROJECT_NAME` | dbt project name | edw |
| `NUM_DBT_MODELS` | Number of dbt models generated | 11 |
| `NUM_DBT_TESTS` | Number of dbt tests generated | 12 |

## Generating a New Workshop

### Using the `/generate-hol` Skill (Recommended)

This repo includes a CoCo skill that automates the entire workshop creation process. Here's how to install and use it:

#### Step 1: Install the skill

Clone this template repo anywhere on your machine:

```bash
git clone https://github.com/sfc-gh-obenning/coco-hol-template.git
cd coco-hol-template
```

Then install the plugin in CoCo by running this in your terminal:

```bash
cortex plugin install ./
```

Or if using CoCo Desktop, add the plugin via **Settings → Plugins → Add local plugin** and point to the cloned directory.

#### Step 2: Generate your trial signup link

Before running the skill, generate a tracked trial signup link at:

https://app.snowflake.com/sfcogsops/snowhouse_aws_us_west_2/#/streamlit-apps/GROWTH.STREAMLIT_APPS.WINTERFEST/!/signup_link_generator

Save the generated URL — you'll provide it to the skill.

#### Step 3: Create a GitHub repo

Create a new **public** repo on the Snowflake GitHub org for your workshop. Naming convention: `coco-hol-<city>` (e.g., `coco-hol-seattle`, `coco-hol-london`).

```bash
gh repo create sfc-gh-<your-username>/coco-hol-<city> --public
```

#### Step 4: Provision the source database

This workshop requires a pre-provisioned Postgres database that participants connect to via Openflow. Set up the source DB with the appropriate schema and sample data for your domain.

#### Step 5: Run the skill

Open CoCo (Snowsight, CLI, or Desktop) and type:

```
/generate-hol
```

The skill will interactively guide you through:

1. **Event details** — City, venue, date, time range
2. **Source database** — Connection details for the pre-provisioned Postgres
3. **STTM** — Path to the STTM document(s) defining the EDW target
4. **Signup link** — The trial URL you generated in Step 2
5. **GitHub repo** — The repo URL from Step 3

The skill then:
- Clones this template
- Replaces all `{{PLACEHOLDER}}` variables with your scenario content
- Commits and pushes to your GitHub repo
- Validates the deployment
- Instructs you to deploy on Streamlit Community Cloud

#### Step 6: Deploy to Streamlit Cloud

After the skill pushes to GitHub:

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app** → connect your GitHub repo
3. Set main file path to: `workshop_guide/streamlit_app.py`
4. Deploy

Your workshop will be live at `https://<app-name>.streamlit.app`.

#### Step 7: Pre-provision participant accounts

Since Openflow/SPCS is not enabled by default on trial accounts:

1. Have participants create trial accounts in advance
2. Collect their account identifiers
3. Enable Openflow on each account (or pre-provision accounts with Openflow enabled)

#### Step 8: Test and iterate

Run through the workshop yourself end-to-end:
- Verify Openflow connector creation and ingestion
- Execute the dbt pipeline from STTM
- Run the code review prompts
- Check that all template variables rendered correctly

### Manual Generation

If you prefer not to use the skill:

1. Clone this template repo
2. Provision a Postgres source database with sample data
3. Create your STTM document(s) defining the EDW target structure
4. Replace all `{{VARIABLE}}` placeholders in all `.py` files under `workshop_guide/`
5. Push to a new GitHub repo
6. Deploy on Streamlit Community Cloud (point to `workshop_guide/streamlit_app.py`)

**Key files to update:**
- `workshop_guide/app_pages/home.py` — Scenario and overview
- `workshop_guide/app_pages/agenda.py` — Schedule times
- `workshop_guide/app_pages/getting_started.py` — Trial setup instructions
- `workshop_guide/app_pages/session_01.py` through `session_05.py` — Session content

## Deployment

### Streamlit Community Cloud

1. Push the completed workshop to a GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect the repo, point to `workshop_guide/streamlit_app.py`
4. Deploy

### Local Development

```bash
cd workshop_guide
uv venv .venv && uv pip install --python .venv/bin/python 'streamlit>=1.39.0'
.venv/bin/streamlit run streamlit_app.py
```

## File Structure

```
workshop_guide/
├── .streamlit/config.toml    # Theme and font configuration
├── app_pages/
│   ├── home.py               # Workshop overview and scenario
│   ├── getting_started.py    # Account provisioning steps
│   ├── agenda.py             # Schedule and deliverables
│   ├── session_01.py         # Environment Setup
│   ├── session_02.py         # Enterprise Ingestion with Openflow
│   ├── session_03.py         # EDW Pipeline from STTM with dbt
│   ├── session_04.py         # Code Review & Optimization
│   └── session_05.py         # Data Engineer Skill (Stretch)
├── static/                   # Fonts, logos
├── components.py             # Shared UI components
├── requirements.txt          # Python dependencies
└── streamlit_app.py          # Main entry point
```

## Previous Instances

| Date | City | Domain | Repo |
|------|------|--------|------|
| July 7, 2026 | Montreal | Port operations | sfc-gh-obenning/coco-hol-montreal |
| July 9, 2026 | Toronto | Port operations | sfc-gh-obenning/coco-hol-toronto |
| July 16, 2026 | Calgary | Energy/oil sands | sfc-gh-obenning/coco-hol-calgary |
| July 21, 2026 | Vancouver | Port operations | sfc-gh-obenning/coco-hol-vancouver |
