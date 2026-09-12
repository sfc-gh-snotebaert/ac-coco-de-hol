Add a Gen2 Postgres connector to runtime_pg. 
The postgres instance information is in PG_SETUP.CONFIG.PG_INSTANCE_INFO table. 
Use the snowflake_admin credentials.
The postgres database to connect is airline_ops and the schemas to replicate are flight_ops and reservations. 
The publication name is openflow_pub. The target snowflake database is airline_ops.