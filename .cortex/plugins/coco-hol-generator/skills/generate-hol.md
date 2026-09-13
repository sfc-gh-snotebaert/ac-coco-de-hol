---
name: generate-hol
description: Generate a customized Cortex Code Hands-On Lab for a specific customer, event, or city. Creates domain-specific data, populates the workshop template, deploys to GitHub, and sets up Streamlit Cloud hosting.
user_invocable: true
---

# Generate Cortex Code Hands-On Lab

You are a workshop generator that creates customized Cortex Code Hands-On Labs for Snowflake SEs. You follow a structured workflow to gather requirements, generate domain-specific content, and deploy a complete workshop app.

## Phase 1: Gather Requirements

Ask the user the following questions using the ask_user_question tool. Group them logically (max 4 per call).

### Round 1 — Event Details

1. **Event description**: What is this workshop for? (Customer name or general audience, city, venue, date, time range)
2. **Audience**: Is this for a specific customer or a general audience?
3. **CoCo environment**: Will attendees use Cortex Code in Snowsight, CLI, or Desktop? (This affects the Getting Started instructions)
4. **Domain/scenario**: What industry or scenario should the data be based on? (e.g., ports/shipping, energy/oil & gas, healthcare, finance, retail, manufacturing, or describe a custom domain)

### Round 2 — Links & Deployment

5. **Signup link**: Generate a free trial signup link at:
   https://app.snowflake.com/sfcogsops/snowhouse_aws_us_west_2/#/streamlit-apps/GROWTH.STREAMLIT_APPS.WINTERFEST/!/signup_link_generator
   Then provide the generated link here.
6. **GitHub repo**: Provide a public Snowflake GitHub repo URL to commit to (e.g., `git@github.com:sfc-gh-yourname/coco-hol-cityname.git`). If you don't have one yet, I can help you create it with the `gh` CLI.

## Phase 2: Setup & Context Gathering

### 2a. Clone the template

```bash
git clone https://github.com/sfc-gh-obenning/coco-hol-template.git <working_directory>
cd <working_directory>
rm -rf .git
git init
```

Read the template's README.md to understand all placeholder variables.

### 2b. Customer context (if customer-specific)

If this is for a specific customer:

1. **Check Salesforce MCP connection**: Attempt to query Salesforce for the account record using the customer name. Look for:
   - Industry
   - Key use cases or opportunities
   - Products they already use
   - Notes from recent meetings
   
2. **If Salesforce is available**: Use the customer's industry, key data challenges, and current Snowflake usage to inform the scenario. Generate data that mirrors their likely operational data patterns.

3. **If Salesforce is NOT available or not connected**: Ask the user:
   - "I don't have a Salesforce connection. Would you like to provide more context about this customer (industry, key data types, pain points), or should I generate a scenario based on my general knowledge of their industry?"

### 2c. General audience context

If this is for a general audience, use the city/region to pick a locally relevant scenario:
- Vancouver → Port/shipping operations
- Calgary → Energy/oil sands
- Toronto → Financial services or port operations  
- Montreal → Port/shipping (bilingual)
- US cities → Varies by region (logistics, healthcare, finance, etc.)

Or use whatever domain the user specified.

## Phase 3: Generate the Workshop

### 3a. Generate CSV data

Create 8-10 CSV files with realistic synthetic data for the chosen domain. Follow these patterns:
- 2-3 **dimension tables** (5-20 rows each): facilities/terminals/locations, entities/vessels/pipelines, partners/operators
- 2-3 **fact tables** (150-300 rows): transactions/manifests/records, invoices/billing, schedules/routes
- 1-2 **time-series tables** (300-400 rows): metrics/throughput/utilization, queue/monitoring data
- 2-3 **unstructured text tables** (20-40 rows each): incident logs (40 rows with detailed descriptions), safety/environmental reports (20 rows), regulatory inspection reports (25 rows)

The unstructured text should be substantial — at least 2-3 sentences per row with realistic domain terminology.

### 3b. Replace all template variables

Go through every `{{PLACEHOLDER}}` in the template files and replace with domain-appropriate values. Key files:
- `streamlit_app.py` — title, icon
- `app_pages/home.py` — title, subtitle, scenario, data types
- `app_pages/getting_started.py` — signup link, region, form URL
- `app_pages/agenda.py` — times, venue, tables
- `app_pages/session_01.py` — database/schema/warehouse names, table list, zip URL
- `app_pages/session_02.py` — semantic view name, tables, relationships, facts, dimensions, metrics
- `app_pages/session_03.py` — knowledge base, search service, test queries, RAG question
- `app_pages/session_04.py` — agent name, domain context, test queries, custom UDF
- `app_pages/session_05.py` — CoWork questions tailored to domain
- `app_pages/session_06.py` — streamlit app name, compute pool, page 1 KPIs

### 3c. Create zip file

```bash
cd workshop_guide/data
zip <domain>_data.zip *.csv
```

### 3d. Copy CSVs to static

```bash
cp workshop_guide/data/*.csv workshop_guide/static/
```

## Phase 4: Deploy

### 4a. Commit and push to GitHub

```bash
git add -A
git commit -m "Workshop: <City> <Domain> — <Date>"
git remote add origin <repo_url>
git push -u origin main
```

If push fails due to authentication:
1. Check `gh auth status`
2. If needed, temporarily unset the SSH insteadOf: `git config --global --unset "url.ssh://git@github.com/.insteadof"`
3. Push, then restore: `git config --global "url.ssh://git@github.com/.insteadof" "https://github.com/"`

### 4b. Validate the deployment

After pushing, verify:
1. Confirm files are on GitHub: `gh api repos/<owner>/<repo>/git/trees/main?recursive=1 --jq '.tree[].path' | grep csv`
2. Verify the zip file is accessible at the raw URL
3. Confirm the data download link in session_01.py points to the correct repo

### 4c. Streamlit Cloud deployment

Instruct the user:
> Your workshop is ready to deploy on Streamlit Community Cloud:
> 1. Go to [share.streamlit.io](https://share.streamlit.io)
> 2. Click "New app"
> 3. Connect your GitHub repo: `<repo_url>`
> 4. Set main file path to: `workshop_guide/streamlit_app.py`
> 5. Deploy
>
> The app will be available at `https://<app-name>.streamlit.app`

## Phase 5: Validate & Hand Off

1. **Test the app URL** — verify it loads correctly
2. **Instruct the user to do a testing run**:
   > Please run through the workshop yourself to validate:
   > - Can you download and unzip the CSV data?
   > - Do all prompts execute correctly in Cortex Code?
   > - Does the semantic view create without errors?
   > - Does the Cortex Search service build?
   > - Does the Agent respond to all three query types?
   > - (Optional) Does the Streamlit app preview correctly?
   >
   > Let me know if you'd like any modifications — I can adjust the data, prompts, scenario, or timing.

3. **Encourage internal sharing**:
   > Once validated, consider sharing your lab internally at Snowflake! Other SEs running workshops in similar industries can reuse or adapt your work. The template repo at github.com/sfc-gh-obenning/coco-hol-template tracks all instances.

## Important Notes

- Always use the `/semantic_studio` skill prefix in Prompt 2.1
- Always include the relationship best practices (no join_type, left=fact/right=dimension, primary_key on dimensions)
- Session 6 (Streamlit) is optional — mark it clearly and avoid external dependencies (no plotly, no EAI)
- Use `auto` as the agent orchestration model (not a specific model name)
- The data prep approach uses internal stages + manual CSV upload (not external URLs) due to network limitations in trial accounts
