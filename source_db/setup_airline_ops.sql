-- ============================================================================
-- Air Canada HOL — Source Database Setup
-- Target: Snowflake Postgres instance PG01, database: airline_ops
-- Creates schemas, tables, and synthetic data for the workshop
--
-- Usage:  psql "service=postgres1 connect_timeout=10" -f setup_airline_ops.sql
--   (run against the default 'postgres' database — the script creates and
--    connects to airline_ops automatically)
-- ============================================================================

-- CREATE DATABASE cannot run inside a transaction, so we use psql's
-- \gexec trick: SELECT the DDL only if the database doesn't already exist.
SELECT 'CREATE DATABASE airline_ops'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airline_ops') \gexec

-- Switch connection to the new database (psql meta-command)
\connect airline_ops

-- ============================================================================
-- SCHEMAS
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS reservations;
CREATE SCHEMA IF NOT EXISTS flight_ops;

-- ============================================================================
-- TABLES
-- ============================================================================

-- flight_ops.airports — reference table
CREATE TABLE IF NOT EXISTS flight_ops.airports (
    iata_code   VARCHAR(3)    PRIMARY KEY,
    airport_name VARCHAR(200)  NOT NULL,
    city         VARCHAR(100)  NOT NULL,
    country      VARCHAR(3)    NOT NULL,  -- ISO 3166-1 alpha-3
    timezone     VARCHAR(50)   NOT NULL
);

-- flight_ops.flights — flight schedule and status
CREATE TABLE IF NOT EXISTS flight_ops.flights (
    flight_id     SERIAL        PRIMARY KEY,
    flight_number VARCHAR(10)   NOT NULL,
    origin        VARCHAR(3)    NOT NULL REFERENCES flight_ops.airports(iata_code),
    destination   VARCHAR(3)    NOT NULL REFERENCES flight_ops.airports(iata_code),
    departure_ts  TIMESTAMP     NOT NULL,
    arrival_ts    TIMESTAMP     NOT NULL,
    aircraft_id   VARCHAR(10)   NOT NULL,
    status        VARCHAR(20)   NOT NULL DEFAULT 'SCHEDULED'
);

-- reservations.passengers — passenger profiles
CREATE TABLE IF NOT EXISTS reservations.passengers (
    passenger_id  SERIAL        PRIMARY KEY,
    first_name    VARCHAR(100)  NOT NULL,
    last_name     VARCHAR(100)  NOT NULL,
    email         VARCHAR(200)  NOT NULL,
    loyalty_tier  VARCHAR(20)   NOT NULL DEFAULT 'BASIC',
    home_airport  VARCHAR(3)    NOT NULL REFERENCES flight_ops.airports(iata_code)
);

-- reservations.bookings — flight bookings
CREATE TABLE IF NOT EXISTS reservations.bookings (
    pnr           VARCHAR(6)    PRIMARY KEY,
    booking_date  DATE          NOT NULL,
    flight_id     INTEGER       NOT NULL REFERENCES flight_ops.flights(flight_id),
    passenger_id  INTEGER       NOT NULL REFERENCES reservations.passengers(passenger_id),
    fare_class    VARCHAR(1)    NOT NULL,
    status        VARCHAR(20)   NOT NULL DEFAULT 'CONFIRMED',
    total_amount  NUMERIC(10,2) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_flights_origin ON flight_ops.flights(origin);
CREATE INDEX IF NOT EXISTS idx_flights_destination ON flight_ops.flights(destination);
CREATE INDEX IF NOT EXISTS idx_flights_departure ON flight_ops.flights(departure_ts);
CREATE INDEX IF NOT EXISTS idx_bookings_flight ON reservations.bookings(flight_id);
CREATE INDEX IF NOT EXISTS idx_bookings_passenger ON reservations.bookings(passenger_id);
CREATE INDEX IF NOT EXISTS idx_bookings_date ON reservations.bookings(booking_date);
CREATE INDEX IF NOT EXISTS idx_passengers_home ON reservations.passengers(home_airport);

-- ============================================================================
-- SYNTHETIC DATA
-- ============================================================================

-- flight_ops.airports — 25 airports (Air Canada network)
INSERT INTO flight_ops.airports (iata_code, airport_name, city, country, timezone) VALUES
    ('YUL', 'Montréal-Pierre Elliott Trudeau International', 'Montréal', 'CAN', 'America/Toronto'),
    ('YYZ', 'Toronto Pearson International', 'Toronto', 'CAN', 'America/Toronto'),
    ('YVR', 'Vancouver International', 'Vancouver', 'CAN', 'America/Vancouver'),
    ('YYC', 'Calgary International', 'Calgary', 'CAN', 'America/Edmonton'),
    ('YOW', 'Ottawa Macdonald-Cartier International', 'Ottawa', 'CAN', 'America/Toronto'),
    ('YEG', 'Edmonton International', 'Edmonton', 'CAN', 'America/Edmonton'),
    ('YWG', 'Winnipeg James Armstrong Richardson International', 'Winnipeg', 'CAN', 'America/Winnipeg'),
    ('YHZ', 'Halifax Stanfield International', 'Halifax', 'CAN', 'America/Halifax'),
    ('YQB', 'Québec City Jean Lesage International', 'Québec City', 'CAN', 'America/Toronto'),
    ('YXE', 'Saskatoon John G. Diefenbaker International', 'Saskatoon', 'CAN', 'America/Regina'),
    ('JFK', 'John F. Kennedy International', 'New York', 'USA', 'America/New_York'),
    ('LAX', 'Los Angeles International', 'Los Angeles', 'USA', 'America/Los_Angeles'),
    ('ORD', 'O''Hare International', 'Chicago', 'USA', 'America/Chicago'),
    ('SFO', 'San Francisco International', 'San Francisco', 'USA', 'America/Los_Angeles'),
    ('MIA', 'Miami International', 'Miami', 'USA', 'America/New_York'),
    ('LHR', 'London Heathrow', 'London', 'GBR', 'Europe/London'),
    ('CDG', 'Charles de Gaulle', 'Paris', 'FRA', 'Europe/Paris'),
    ('FRA', 'Frankfurt Airport', 'Frankfurt', 'DEU', 'Europe/Berlin'),
    ('NRT', 'Narita International', 'Tokyo', 'JPN', 'Asia/Tokyo'),
    ('HND', 'Haneda Airport', 'Tokyo', 'JPN', 'Asia/Tokyo'),
    ('PVG', 'Shanghai Pudong International', 'Shanghai', 'CHN', 'Asia/Shanghai'),
    ('HKG', 'Hong Kong International', 'Hong Kong', 'HKG', 'Asia/Hong_Kong'),
    ('CUN', 'Cancún International', 'Cancún', 'MEX', 'America/Cancun'),
    ('SJU', 'Luis Muñoz Marín International', 'San Juan', 'PRI', 'America/Puerto_Rico'),
    ('BOG', 'El Dorado International', 'Bogotá', 'COL', 'America/Bogota')
ON CONFLICT (iata_code) DO NOTHING;

-- flight_ops.flights — ~500 flights over a 30-day window
INSERT INTO flight_ops.flights (flight_number, origin, destination, departure_ts, arrival_ts, aircraft_id, status)
SELECT
    'AC' || (100 + (row_number() OVER ())::int % 900)::text AS flight_number,
    origins.code AS origin,
    destinations.code AS destination,
    base_date + (interval '1 hour' * (random() * 16 + 6)::int) AS departure_ts,
    base_date + (interval '1 hour' * (random() * 16 + 6)::int) + (interval '1 hour' * duration_hrs) AS arrival_ts,
    'C-F' || chr(65 + (random() * 25)::int) || chr(65 + (random() * 25)::int) || chr(65 + (random() * 25)::int) AS aircraft_id,
    CASE
        WHEN base_date < CURRENT_DATE - interval '5 days' THEN
            (ARRAY['COMPLETED', 'COMPLETED', 'COMPLETED', 'COMPLETED', 'CANCELLED', 'DIVERTED'])[1 + (random() * 5)::int]
        WHEN base_date < CURRENT_DATE THEN
            (ARRAY['COMPLETED', 'COMPLETED', 'COMPLETED', 'DELAYED', 'CANCELLED'])[1 + (random() * 4)::int]
        WHEN base_date = CURRENT_DATE THEN
            (ARRAY['SCHEDULED', 'BOARDING', 'IN_FLIGHT', 'DELAYED'])[1 + (random() * 3)::int]
        ELSE 'SCHEDULED'
    END AS status
FROM
    generate_series(CURRENT_DATE - interval '30 days', CURRENT_DATE + interval '14 days', interval '1 day') AS base_date,
    (VALUES ('YUL'), ('YYZ'), ('YVR'), ('YYC'), ('YOW'), ('YEG')) AS origins(code),
    (VALUES ('YUL'), ('YYZ'), ('YVR'), ('YYC'), ('JFK'), ('LAX'), ('LHR'), ('CDG'), ('NRT'), ('CUN'), ('ORD'), ('SFO'), ('MIA'), ('HKG')) AS destinations(code),
    (SELECT random() * 8 + 1.5 AS duration_hrs) AS dur
WHERE origins.code != destinations.code
  AND random() < 0.07
ON CONFLICT DO NOTHING;

-- reservations.passengers — ~300 passengers
INSERT INTO reservations.passengers (first_name, last_name, email, loyalty_tier, home_airport)
SELECT
    first_names.name,
    last_names.name,
    lower(first_names.name || '.' || last_names.name || (row_number() OVER ())::text || '@example.com'),
    (ARRAY['BASIC', 'BASIC', 'BASIC', 'SILVER', 'SILVER', 'GOLD', 'PLATINUM', 'SUPER_ELITE'])[1 + (random() * 7)::int],
    (ARRAY['YUL', 'YYZ', 'YVR', 'YYC', 'YOW', 'YEG', 'YWG', 'YHZ', 'YQB'])[1 + (random() * 8)::int]
FROM
    (VALUES ('James'),('Mary'),('Robert'),('Patricia'),('John'),('Jennifer'),('Michael'),('Linda'),
            ('David'),('Elizabeth'),('William'),('Barbara'),('Richard'),('Susan'),('Joseph'),('Jessica'),
            ('Thomas'),('Sarah'),('Daniel'),('Karen'),('Matthew'),('Lisa'),('Anthony'),('Nancy'),
            ('Mark'),('Betty'),('Donald'),('Margaret'),('Steven'),('Sandra'),('Paul'),('Ashley'),
            ('Andrew'),('Emily'),('Joshua'),('Donna'),('Kenneth'),('Michelle'),('Kevin'),('Carol'),
            ('Brian'),('Amanda'),('George'),('Melissa'),('Timothy'),('Deborah'),('Ronald'),('Stephanie'),
            ('Edward'),('Rebecca')) AS first_names(name),
    (VALUES ('Smith'),('Johnson'),('Williams'),('Brown'),('Jones'),('Garcia')) AS last_names(name)
WHERE random() < 0.99
ON CONFLICT DO NOTHING;

-- reservations.bookings — ~800 bookings
INSERT INTO reservations.bookings (pnr, booking_date, flight_id, passenger_id, fare_class, status, total_amount)
SELECT
    upper(substr(md5(random()::text), 1, 6)) AS pnr,
    (f.departure_ts::date - (random() * 60 + 1)::int * interval '1 day')::date AS booking_date,
    f.flight_id,
    p.passenger_id,
    (ARRAY['Y', 'Y', 'Y', 'Y', 'M', 'M', 'C', 'J', 'F'])[1 + (random() * 8)::int] AS fare_class,
    CASE
        WHEN f.status = 'CANCELLED' AND random() < 0.3 THEN 'CANCELLED'
        WHEN random() < 0.05 THEN 'PENDING'
        WHEN random() < 0.02 THEN 'CANCELLED'
        ELSE 'CONFIRMED'
    END AS status,
    CASE (ARRAY['Y', 'Y', 'Y', 'Y', 'M', 'M', 'C', 'J', 'F'])[1 + (random() * 8)::int]
        WHEN 'Y' THEN round((random() * 400 + 150)::numeric, 2)
        WHEN 'M' THEN round((random() * 600 + 300)::numeric, 2)
        WHEN 'C' THEN round((random() * 1500 + 800)::numeric, 2)
        WHEN 'J' THEN round((random() * 3000 + 2000)::numeric, 2)
        WHEN 'F' THEN round((random() * 5000 + 4000)::numeric, 2)
        ELSE round((random() * 500 + 200)::numeric, 2)
    END AS total_amount
FROM flight_ops.flights f
CROSS JOIN reservations.passengers p
WHERE random() < 0.006
ON CONFLICT (pnr) DO NOTHING;

-- ============================================================================
-- VERIFICATION
-- ============================================================================
SELECT 'flight_ops.airports' AS table_name, count(*) AS row_count FROM flight_ops.airports
UNION ALL
SELECT 'flight_ops.flights', count(*) FROM flight_ops.flights
UNION ALL
SELECT 'reservations.passengers', count(*) FROM reservations.passengers
UNION ALL
SELECT 'reservations.bookings', count(*) FROM reservations.bookings
ORDER BY table_name;
