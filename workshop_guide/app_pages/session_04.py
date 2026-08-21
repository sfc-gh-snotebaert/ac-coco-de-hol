import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built

render_session_header(4, "Code Review & Optimization", "{{TIME_SESSION_4}}", "{{DUR_SESSION_4}}", "SQL anti-pattern detection, query profile analysis, and clustering recommendations")

render_technologies_used([
    {"name": "SQL Anti-Pattern Detection", "description": "Systematic review of SQL for common pitfalls: non-sargable predicates, implicit casts, SELECT *, missing filters, and Snowflake-specific traps.", "icon": "bug_report"},
    {"name": "Query Profile Analysis", "description": "Snowflake's execution plan showing partition pruning, spilling, join strategies, and operator timings. The ground truth for performance tuning.", "icon": "analytics"},
    {"name": "Clustering Keys", "description": "Column-level micro-partitioning strategy that co-locates related data for faster partition pruning on large tables.", "icon": "sort"},
])


PROMPT_4_1 = """Review the dbt SQL models we generated in Session 3 for the {{DBT_PROJECT_NAME}} project.

Perform a comprehensive code review covering:

1. **SQL Anti-Patterns** — Check every model for:
   - SELECT * usage (should explicitly list columns)
   - Implicit type casts that could cause precision loss
   - Non-sargable predicates (functions on indexed/clustered columns in WHERE clauses)
   - Cartesian join risks (missing join conditions)
   - UNION vs UNION ALL (unnecessary deduplication)
   - Integer division without explicit CAST

2. **Coding Standards** — Check for:
   - CTE naming conventions (should be descriptive, not cte1/cte2)
   - Column ordering (keys first, then dimensions, then measures, then metadata)
   - Consistent aliasing (table aliases should be meaningful, not a/b/c)
   - Hardcoded values that should be variables or config

3. **Snowflake Best Practices** — Check for:
   - Appropriate use of QUALIFY vs subquery for row_number filtering
   - MERGE vs DELETE+INSERT patterns
   - Proper NULL handling (NVL vs COALESCE vs IFNULL)
   - Transient vs permanent table choices for staging

For each issue found, report:
- The file and line
- The issue category (anti-pattern / standard / best practice)
- Severity (HIGH / MEDIUM / LOW)
- The current code
- The recommended fix

Present as a structured review report."""

render_prompt("Prompt 4.1", "SQL Anti-Pattern & Standards Review", PROMPT_4_1)

render_explanation("What this prompt does", """
Uses Cortex Code as a code review agent. It analyzes the generated SQL and produces findings like:

```
CODE REVIEW REPORT — {{DBT_PROJECT_NAME}}
==========================================

FINDING 1 [HIGH] — Anti-Pattern: Implicit Type Cast
File: models/marts/fact_booking.sql, Line 12
Current:  WHERE total_amount > '0'
Fix:      WHERE total_amount > 0
Reason:   Comparing NUMBER to VARCHAR forces implicit cast on every row

FINDING 2 [MEDIUM] — Standard: Non-descriptive CTE
File: models/marts/dim_passenger.sql, Line 3
Current:  WITH cte1 AS (...)
Fix:      WITH passenger_base AS (...)
Reason:   CTE names should describe their content for readability

FINDING 3 [LOW] — Best Practice: QUALIFY vs Subquery
File: models/staging/stg_flights.sql, Line 15
Current:  SELECT * FROM (SELECT ..., ROW_NUMBER() ...) WHERE rn = 1
Fix:      SELECT ... QUALIFY ROW_NUMBER() OVER (...) = 1
Reason:   QUALIFY is Snowflake-native, more readable, and avoids a subquery
```

This simulates a senior engineer reviewing code before merge — the kind of review that catches issues before they hit production.
""")


PROMPT_4_2 = """Now analyze the query performance of our dbt models. For the two largest models (FACT_BOOKING and FACT_FLIGHT_OPS):

1. Run EXPLAIN on the model SQL and analyze the query profile
2. Check for:
   - **Partition pruning**: Are we scanning more micro-partitions than necessary?
   - **Spilling**: Is the query spilling to local or remote storage?
   - **Join strategies**: Are joins using hash join vs nested loop? Is the build side appropriate?
   - **Bytes scanned**: How much data is being read relative to output?

3. Based on typical query patterns for an airline EDW:
   - Analysts filter by: date range, route (origin/destination), fare class
   - Operations filter by: flight date, aircraft, status
   - Loyalty team filters by: passenger, tier, transaction date

   Recommend clustering keys for:
   - FACT_BOOKING
   - FACT_FLIGHT_OPS
   - DIM_PASSENGER

4. Show the specific ALTER TABLE statements to apply the clustering

Present the analysis with before/after partition pruning estimates."""

render_prompt("Prompt 4.2", "Query Profile & Clustering Analysis", PROMPT_4_2)

render_explanation("What this prompt does", """
Analyzes execution plans and recommends clustering strategies:

```sql
-- Analyze query profile
SELECT *
FROM TABLE(GET_QUERY_OPERATOR_STATS(LAST_QUERY_ID()));

-- Recommend clustering based on query patterns
ALTER TABLE EDW_AC.MARTS.FACT_BOOKING
  CLUSTER BY (BOOKING_DATE, ORIGIN_AIRPORT, FARE_CLASS);

ALTER TABLE EDW_AC.MARTS.FACT_FLIGHT_OPS
  CLUSTER BY (DEPARTURE_DATE, AIRCRAFT_ID, STATUS);

ALTER TABLE EDW_AC.MARTS.DIM_PASSENGER
  CLUSTER BY (LOYALTY_TIER, HOME_AIRPORT);
```

**Clustering key selection principles:**
- Choose columns that appear in WHERE/JOIN conditions of the most common queries
- Put the highest-cardinality filter first (date) for maximum pruning
- Limit to 3-4 columns (more = diminishing returns + higher reclustering cost)
- Don't cluster small tables (< 1GB) — the overhead isn't worth it

**Expected improvement:** Proper clustering on a 100M+ row fact table can reduce partition scans from 100% to 5-10% for typical date-range queries.
""")


PROMPT_4_3 = """Produce a consolidated Optimization Recommendations Report for the entire {{DBT_PROJECT_NAME}} project.

The report should include:

1. **Executive Summary** — 2-3 sentences on overall code health and top priorities

2. **Prioritized Findings Table** — All issues from the code review and query analysis:
   | # | Category | Severity | Model | Issue | Recommended Fix |
   Sorted by severity (HIGH first), then by model

3. **Clustering Recommendations** — The ALTER TABLE statements ready to execute

4. **Refactored SQL** — For the top 3 HIGH severity issues, show the complete corrected model SQL (not just the line — the full file)

5. **Impact Assessment** — For each HIGH/MEDIUM finding, estimate:
   - Performance impact (e.g., "reduces scan by ~80%")
   - Risk if not fixed (e.g., "silent precision loss in financial calculations")
   - Effort to fix (e.g., "1 line change" vs "model restructure")

Format this as a professional report that could be shared with a data engineering team lead."""

render_prompt("Prompt 4.3", "Consolidated Recommendations Report", PROMPT_4_3)

render_explanation("What this prompt does", """
Produces a complete, actionable optimization report:

```
OPTIMIZATION RECOMMENDATIONS REPORT
====================================
Project: {{DBT_PROJECT_NAME}}
Date: [today]
Reviewer: Cortex Code

EXECUTIVE SUMMARY
-----------------
The pipeline is functionally correct with good test coverage.
3 high-severity issues identified: implicit type cast in financial
calculations, missing clustering on fact tables, and a non-sargable
predicate causing full table scans.

PRIORITIZED FINDINGS
--------------------
| # | Category      | Sev  | Model         | Issue                    |
|----|---------------|------|---------------|--------------------------|
| 1  | Anti-Pattern  | HIGH | fact_booking  | Implicit cast on amount  |
| 2  | Performance   | HIGH | fact_booking  | No clustering key        |
| 3  | Anti-Pattern  | HIGH | fact_flight   | Non-sargable DATE()      |
| 4  | Standard      | MED  | dim_passenger | CTE naming               |
| ...
```

This is the deliverable for Session 4 — a report you could hand to a tech lead or use in a PR review.
""")


render_key_concepts([
    {"term": "Non-Sargable Predicate", "definition": "A WHERE condition that applies a function to a column (e.g., DATE(departure_ts) = '2024-01-01'), preventing the optimizer from using partition pruning or indexes. Fix: restructure to keep the column bare."},
    {"term": "Clustering Key", "definition": "Columns that Snowflake uses to physically co-locate data in micro-partitions. Enables partition pruning — the #1 performance lever for large tables. Applied via ALTER TABLE ... CLUSTER BY."},
    {"term": "Partition Pruning", "definition": "The optimizer skipping micro-partitions that cannot contain matching rows based on min/max metadata. Well-clustered tables prune 90%+ of partitions on filtered queries."},
    {"term": "Query Profile", "definition": "Snowflake's execution plan showing operator tree, bytes scanned, spilling, pruning ratios, and timings. Access via GET_QUERY_OPERATOR_STATS() or the Snowsight Query Profile UI."},
    {"term": "Spilling", "definition": "When a query's intermediate results exceed available memory, they 'spill' to local SSD or remote storage. Spilling dramatically slows queries — fix by reducing data volume (better pruning) or upsizing the warehouse."},
])

render_what_you_built([
    "SQL anti-pattern review identifying coding issues across all models",
    "Query profile analysis with partition pruning and spilling assessment",
    "Clustering key recommendations for fact and dimension tables",
    "Refactored SQL for the highest-severity issues",
    "Professional optimization report ready for team lead review",
])
