Add a Gen2 Postgres connector named PG_CDC_CONNECTOR to RUNTIME_PG. 
The postgres instance information is in PG_SETUP.CONFIG.PG_INSTANCE_INFO table. 
Use the snowflake_admin credentials.
The postgres database to connect is AIRLINE_OPS and the schemas to replicate are FLIGHT_OPS and RESERVATIONS. 
The publication name is OPENFLOW_PUB. The target snowflake database is AIRLINE_OPS.