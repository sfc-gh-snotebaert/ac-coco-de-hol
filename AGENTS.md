# Agent Instructions

## dbt Project — Iceberg Materialization

All dbt models must be materialized as **Snowflake-managed Iceberg tables**. The generated DDL must use:

```sql
CREATE ICEBERG TABLE ... CATALOG = 'SNOWFLAKE' EXTERNAL_VOLUME = 'SNOWFLAKE_MANAGED';
```

In `dbt_project.yml`, add the following model config:

```yaml
flags:
  enable_iceberg_materializations: true

models:
  +materialized: table
  +table_format: iceberg
  +external_volume: SNOWFLAKE_MANAGED
```
